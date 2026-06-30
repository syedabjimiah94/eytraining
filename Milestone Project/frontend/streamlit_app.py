import requests
import streamlit as st

API_BASE = "http://localhost:8000"

st.set_page_config(page_title="Self Healing Weather API", layout="wide")
st.title("🌦 Self-Healing Weather Platform")
st.caption("Live weather + mock demo + LangGraph workflow + SQLite incident audit")

with st.sidebar:
    st.header("Demo Controls")
    mode = st.radio("Provider mode", ["live", "mock"], horizontal=True)

    st.subheader("Failure Simulator")

    failure_type = st.selectbox(
        "Choose failure scenario",
        [
            "success",
            "network_error",
            "weather_api_down",
            "llm_timeout",
            "invalid_api_key",
            "database_down",
        ],
    )


    def post_toggle(path, value):
        return requests.post(f"{API_BASE}{path}/{str(value).lower()}", timeout=5).json()

    try:
        status = requests.get(f"{API_BASE}/simulator/status", timeout=5).json()
        api_down = st.toggle("Primary API Down", value=status["api_down"])
        bad_payload = st.toggle("Bad Provider Payload", value=status["bad_payload"])
        slow_response = st.toggle("Slow Response / Timeout", value=status["slow_response"])

        if api_down != status["api_down"]:
            post_toggle("/simulator/api-down", api_down)
        if bad_payload != status["bad_payload"]:
            post_toggle("/simulator/bad-payload", bad_payload)
        if slow_response != status["slow_response"]:
            post_toggle("/simulator/slow-response", slow_response)

        if st.button("Reset Simulator"):
            requests.post(f"{API_BASE}/simulator/reset", timeout=5)
            st.rerun()
    except Exception as exc:
        st.error(f"Backend not reachable: {exc}")

st.divider()
city = st.text_input("Ask weather for city", "Chennai")

if st.button("Generate Weather Output", type="primary"):
    try:
        with st.spinner("Calling backend workflow..."):
            response = requests.get(
                f"{API_BASE}/weather",
                params={
                        "city": city,
                        "mode": mode,
                        "failure_type": failure_type,
                    },
                timeout=30,
            )
            response.raise_for_status()
            data = response.json()

        col1, col2, col3, col4,col5 = st.columns(5)
        col1.metric("Temperature", f"{data['temperature']} °C")
        col2.metric("Humidity", f"{data['humidity']} %")
        col3.metric("Wind", f"{data['wind_speed']} km/h")
        col4.metric("Source", data.get("source", "unknown"))
        col5.metric(
            "Latency",
            f"{data.get('latency_ms',0)} ms"
        )
        if data.get("healed"):
            st.warning("Primary failed. Self-healing returned fallback weather output.")
        else:
            st.success("Weather generated successfully.")

        st.subheader("Weather Response")
        st.json(data)

        st.divider()
        st.subheader("Failure Flow: Monitor → Diagnosis → Healing → Validate")
        workflow = data.get("workflow", [])
        if workflow:
            cols = st.columns(min(5, len(workflow)))
            for idx, step in enumerate(workflow):
                with cols[idx % len(cols)]:
                    status = step.get("status", "UNKNOWN")
                    icon = "✅" if status == "SUCCESS" or status == "SAVED" else "⚠️" if status in ["FAILED", "NOT_SENT"] else "ℹ️"
                    st.markdown(f"### {icon} {step.get('step', '').title()}")
                    st.write(status)
                    st.caption(step.get("message", ""))
                    if "llm_used" in step:
                        st.caption(f"LLM used: {step['llm_used']}")
        else:
            st.info("No failure workflow was needed because the provider succeeded.")

        if data.get("incident_id"):
            st.subheader("Incident + Ticket")
            st.json({
                "incident_id": data.get("incident_id"),
                "attempts": data.get("attempts"),
                "diagnosis": data.get("diagnosis"),
                "healing": data.get("healing"),
                "verification": data.get("verification"),
                "ticket": data.get("ticket"),
            })
            if data.get("ticket", {}).get("status") in ["NOT_SENT", "FAILED"]:
                st.error("Manual investigation needed. Ticket format was created, but email was not sent because Resend is not configured or failed.")
                st.text_area("Manual investigation ticket body", data.get("ticket", {}).get("body", ""), height=300)
    except Exception as exc:
        st.error(f"Request failed: {exc}")

st.divider()
try:
    health = requests.get(f"{API_BASE}/health", timeout=5).json()
    st.subheader("System Health")
    col1, col2, col3 = st.columns(3)
    col1.metric("Status", health["status"])
    col2.metric("Incidents", health["total_incidents"])
    col3.metric("Healed", health["total_healed"])

    st.subheader("Recent SQLite Incidents")
    incidents = requests.get(f"{API_BASE}/incidents", timeout=5).json()
    st.dataframe(incidents, use_container_width=True)
except Exception as exc:
    st.error(f"Could not load health/incidents: {exc}")
