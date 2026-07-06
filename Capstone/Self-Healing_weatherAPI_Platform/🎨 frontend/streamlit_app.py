import os
import requests
import streamlit as st
import pandas as pd
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

API_BASE = os.getenv("API_BASE", "http://localhost:8000")
# st.sidebar.caption(f"Backend API: {API_BASE}")

st.set_page_config(
    page_title="Self Healing Weather API",
    page_icon="🌦️",
    layout="wide"
)

st.markdown("""
<style>
.stApp {
    background: #f8fafc;
}

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #061529 0%, #0b1f3a 100%);
    padding-top: 20px;
}

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #061529 0%, #0b1f3a 100%);
}

/* Only normal text is white */
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3,
[data-testid="stSidebar"] h4,
[data-testid="stSidebar"] label {
    color: white!important;
}

.block-container {
    padding-top: 2rem;
    padding-left: 2rem;
    padding-right: 2rem;
}

.main-title {
    font-size: 40px;
    font-weight: 900;
    margin-bottom: 0;
    background: linear-gradient(90deg, #2563EB, #0EA5E9, #06B6D4);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.subtitle {
    color: #64748b;
    font-size: 16px;
    margin-bottom: 28px;
}

.card {
    background: white;
    border-radius: 18px;
    padding: 24px;
    border: 1px solid #e5e7eb;
    box-shadow: 0 8px 22px rgba(15, 23, 42, 0.06);
}

.health-card {
    background: linear-gradient(135deg, #f0fdf4, #ffffff);
    border: 1px solid #bbf7d0;
    border-radius: 18px;
    padding: 28px;
    text-align: center;
}

.metric-card {
    border-radius: 18px;
    padding: 24px;
    border: 1px solid #e5e7eb;
    min-height: 145px;
    box-shadow: 0 8px 22px rgba(15, 23, 42, 0.05);
}

.purple { background: linear-gradient(135deg, #faf5ff, #ffffff); }
.green { background: linear-gradient(135deg, #f0fdf4, #ffffff); }
.blue { background: linear-gradient(135deg, #eff6ff, #ffffff); }
.orange { background: linear-gradient(135deg, #fff7ed, #ffffff); }
.yellow { background: linear-gradient(135deg, #fffbeb, #ffffff); }
.pink { background: linear-gradient(135deg, #fff1f2, #ffffff); }
.cyan { background: linear-gradient(135deg, #ecfeff, #ffffff); }

.card-label {
    color: #475569;
    font-size: 14px;
    font-weight: 700;
}

.card-value {
    font-size: 34px;
    font-weight: 800;
    color: #0f172a;
    margin-top: 10px;
}

.card-sub {
    color: #64748b;
    font-size: 13px;
    margin-top: 6px;
}

.section-title {
    font-size: 25px;
    font-weight: 800;
    color: #0f172a;
    margin-top: 36px;
    margin-bottom: 22px;
}

.status-success {
    color: #16a34a;
    font-weight: 800;
}

.status-failed {
    color: #dc2626;
    font-weight: 800;
}

.sidebar-box {
    background: rgba(255,255,255,0.08);
    border: 1px solid rgba(255,255,255,0.12);
    border-radius: 16px;
    padding: 18px;
    margin-top: 18px;
}

/* About card text */
.sidebar-box,
.sidebar-box * {
    color: white !important;
}

/* Selectbox - Streamlit 1.58 */
div[data-testid="stSelectbox"] div[data-baseweb="select"] {
    background: white !important;
    border-radius: 10px !important;
}

div[data-testid="stSelectbox"] div[data-baseweb="select"] * {
    color: black !important;
}

div[data-testid="stSelectbox"] svg {
    fill: black !important;
}

div[role="listbox"] {
    background: white !important;
}

div[role="option"] {
    color: black !important;
    background: white !important;
}

.footer {
    color: #64748b;
    font-size: 13px;
    margin-top: 35px;
    padding-top: 20px;
    border-top: 1px solid #e5e7eb;
}
div[data-testid="stSelectbox"] label {
    color: white !important;
    font-weight: 700 !important;
}

div[data-testid="stSelectbox"] div[data-baseweb="select"] {
    background: white !important;
    border-radius: 10px !important;
}

div[data-testid="stSelectbox"] div[data-baseweb="select"] * {
    color: black !important;
}

div[data-testid="stSelectbox"] svg {
    fill: black !important;
}

div[role="listbox"] {
    background: white !important;
}

div[role="option"] {
    color: black !important;
    background: white !important;
}

div[role="option"]:hover {
    background: #e2e8f0 !important;
}
</style>
""", unsafe_allow_html=True)



def safe_get(url, default):
    try:
        return requests.get(url, timeout=5).json()
    except Exception:
        return default


def show_top_cards():
    top1, top2, top3 = st.columns(3)

    with top1:
        st.markdown("""
        <div class="card">
            <div class="status-success">✅ SYSTEM STATUS</div>
            <h3>Healthy</h3>
            <p class="card-sub">All services are operational</p>
        </div>
        """, unsafe_allow_html=True)

    with top2:
        st.markdown("""
        <div class="card">
            <div style="color:#2563eb;font-weight:800;">📊 LLM STATUS</div>
            <h3>Active</h3>
            <p class="card-sub">LLM is available and ready</p>
        </div>
        """, unsafe_allow_html=True)

    with top3:
        st.markdown("""
        <div class="card">
            <div style="color:#9333ea;font-weight:800;">🗄️ DATABASE</div>
            <h3>SQLite Connected</h3>
            <p class="card-sub">Incidents are being saved</p>
        </div>
        """, unsafe_allow_html=True)


def show_weather_output(data):
    st.markdown('<div class="section-title">Weather Output</div>', unsafe_allow_html=True)
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Temperature", f"{data.get('temperature', 'Missing')} °C")
    c2.metric("Humidity", f"{data.get('humidity', 'Missing')} %")
    c3.metric("Wind", f"{data.get('wind_speed', 'Missing')} km/h")
    c4.metric("Source", data.get("source", "unknown"))
    c5.metric("Latency", f"{data.get('latency_ms', 0)} ms")

    if data.get("healed"):
        st.warning("Primary provider failed. Self-healing returned recovered output.")
    else:
        st.success("Weather generated successfully.")


def show_drift(data):
    drift = data.get("drift", {})
    st.markdown('<div class="section-title">Drift Detection Layer</div>', unsafe_allow_html=True)

    drift_detected = drift.get("drift_detected", False)
    drift_status = "DRIFT DETECTED" if drift_detected else "NO DRIFT"
    drift_icon = "⚠️" if drift_detected else "✅"

    d1, d2, d3 = st.columns(3)

    with d1:
        st.markdown(f"""
        <div class="metric-card yellow">
            <div class="card-label">Drift Status</div>
            <div style="font-size:22px;font-weight:800;color:#92400E;">
                {drift_icon} {drift_status}
            </div>
        </div>
        """, unsafe_allow_html=True)

    with d2:
        st.markdown(f"""
        <div class="metric-card blue">
            <div class="card-label">Drift Type</div>
            <div style="font-size:22px;font-weight:800;color:#1D4ED8;">
                {drift.get("drift_type", "NONE")}
            </div>
        </div>
        """, unsafe_allow_html=True)

    with d3:
        st.markdown(f"""
        <div class="metric-card orange">
            <div class="card-label">Severity</div>
            <div style="font-size:22px;font-weight:800;color:#92400E;">
                {drift.get("severity", "LOW")}
            </div>
        </div>
        """, unsafe_allow_html=True)

    if drift_detected:
        st.warning(drift.get("message", "Drift detected"))
    else:
        st.success(drift.get("message", "No drift detected"))


def show_failure_flow(data):
    st.markdown('<div class="section-title">Failure Flow</div>', unsafe_allow_html=True)
    workflow = data.get("workflow", [])
    if workflow:
        cols = st.columns(min(5, len(workflow)))
        for idx, step in enumerate(workflow):
            status = step.get("status", "UNKNOWN")
            badge_class = "status-success" if status in ["SUCCESS", "SAVED"] else "status-failed"
            icon = "✅" if status in ["SUCCESS", "SAVED"] else "⚠️"

            with cols[idx % len(cols)]:
                st.markdown(f"""
                <div class="metric-card blue">
                    <h3>{icon} {step.get("step", "").title()}</h3>
                    <div class="{badge_class}">{status}</div>
                    <p class="card-sub">{step.get("message", "")}</p>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("No failure workflow was needed because provider succeeded.")


def show_backend_response(data):
    st.markdown('<div class="section-title">Full Backend Response</div>', unsafe_allow_html=True)
    st.json(data)


def show_incident_ticket(data):
    st.markdown('<div class="section-title">Incident + Ticket</div>', unsafe_allow_html=True)
    if data.get("incident_id"):
        st.json({
            "incident_id": data.get("incident_id"),
            "attempts": data.get("attempts"),
            "diagnosis": data.get("diagnosis"),
            "healing": data.get("healing"),
            "verification": data.get("verification"),
            "ticket": data.get("ticket"),
        })

        if data.get("ticket", {}).get("status") in ["NOT_SENT", "FAILED"]:
            st.error("Manual investigation needed.")
            st.text_area(
                "Manual investigation ticket body",
                data.get("ticket", {}).get("body", ""),
                height=300
            )
    else:
        st.info("No incident ticket was generated for this request.")


def show_health():
    health = safe_get(
        f"{API_BASE}/health",
        {"status": "Healthy", "total_incidents": 0, "total_healed": 0}
    )

    st.markdown('<div class="section-title">〽️ System Health</div>', unsafe_allow_html=True)
    h1, h2, h3 = st.columns(3)

    with h1:
        st.markdown(f"""
        <div class="health-card">
            <div class="card-label">Status</div>
            <div class="card-value" style="color:#16a34a;">● {health["status"]}</div>
        </div>
        """, unsafe_allow_html=True)

    with h2:
        st.markdown(f"""
        <div class="health-card">
            <div class="card-label">Total Incidents</div>
            <div class="card-value">{health["total_incidents"]}</div>
        </div>
        """, unsafe_allow_html=True)

    with h3:
        st.markdown(f"""
        <div class="health-card">
            <div class="card-label">Total Healed</div>
            <div class="card-value">{health["total_healed"]}</div>
        </div>
        """, unsafe_allow_html=True)


def show_metrics():
    metrics = safe_get(
        f"{API_BASE}/metrics",
        {
            "requests": 0,
            "success": 0,
            "self_healed": 0,
            "manual": 0,
            "average_latency_sec": 0,
            "llm_calls": 0,
            "emails_sent": 0,
        }
    )

    st.markdown('<div class="section-title">📊 Evaluation Metrics</div>', unsafe_allow_html=True)
    m1, m2, m3, m4 = st.columns(4)

    with m1:
        st.markdown(f"""
        <div class="metric-card purple">
            <div class="card-label">👥 Requests</div>
            <div class="card-value">{metrics["requests"]}</div>
            <div class="card-sub">Total requests processed</div>
        </div>
        """, unsafe_allow_html=True)

    with m2:
        st.markdown(f"""
        <div class="metric-card green">
            <div class="card-label">✅ Success</div>
            <div class="card-value">{metrics["success"]}</div>
            <div class="card-sub">Successfully completed</div>
        </div>
        """, unsafe_allow_html=True)

    with m3:
        st.markdown(f"""
        <div class="metric-card blue">
            <div class="card-label">🛡️ Self-Healed</div>
            <div class="card-value">{metrics["self_healed"]}</div>
            <div class="card-sub">Automatically recovered</div>
        </div>
        """, unsafe_allow_html=True)

    with m4:
        st.markdown(f"""
        <div class="metric-card orange">
            <div class="card-label">🧑‍🔧 Manual</div>
            <div class="card-value">{metrics["manual"]}</div>
            <div class="card-sub">Requires investigation</div>
        </div>
        """, unsafe_allow_html=True)

    m5, m6, m7 = st.columns(3)

    with m5:
        st.markdown(f"""
        <div class="metric-card yellow">
            <div class="card-label">⏱️ Average Latency</div>
            <div class="card-value">{metrics["average_latency_sec"]} sec</div>
            <div class="card-sub">Average response time</div>
        </div>
        """, unsafe_allow_html=True)

    with m6:
        st.markdown(f"""
        <div class="metric-card pink">
            <div class="card-label">🧠 LLM Calls</div>
            <div class="card-value">{metrics["llm_calls"]}</div>
            <div class="card-sub">Total LLM API calls</div>
        </div>
        """, unsafe_allow_html=True)

    with m7:
        st.markdown(f"""
        <div class="metric-card cyan">
            <div class="card-label">✉️ Emails Sent</div>
            <div class="card-value">{metrics["emails_sent"]}</div>
            <div class="card-sub">Incident notification emails</div>
        </div>
        """, unsafe_allow_html=True)


def show_load_testing():
    st.markdown('<div class="section-title">🚀 Load Testing</div>', unsafe_allow_html=True)

    with st.container():
        l1, l2, l3, l4 = st.columns(4)

        with l1:
            load_users = st.number_input("Virtual Users", min_value=1, max_value=100, value=10)

        with l2:
            total_requests = st.number_input("Total Requests", min_value=1, max_value=500, value=50)

        with l3:
            load_city = st.text_input("Load Test City", "Chennai")

        with l4:
            load_failure_type = st.selectbox(
                "Load Failure Type",
                [
                    "success",
                    "network_error",
                    "weather_api_down",
                    "api_timeout",
                    "rate_limit_429",
                    "invalid_json",
                    "llm_timeout",
                    "schema_drift",
                    "data_anomaly_drift",
                ],
                key="load_failure_type"
            )

        def run_single_load_request():
            start_time = time.perf_counter()

            try:
                response = requests.get(
                    f"{API_BASE}/weather",
                    params={
                        "city": load_city,
                        "mode": "mock",
                        "failure_type": load_failure_type,
                    },
                    timeout=30,
                )

                latency_ms = round((time.perf_counter() - start_time) * 1000, 2)

                return {
                    "status_code": response.status_code,
                    "success": response.status_code == 200,
                    "latency_ms": latency_ms,
                }

            except Exception as e:
                latency_ms = round((time.perf_counter() - start_time) * 1000, 2)

                return {
                    "status_code": "ERROR",
                    "success": False,
                    "latency_ms": latency_ms,
                    "error": str(e),
                }

        if st.button("🚀 Run Load Test", type="primary"):
            results = []
            start_test = time.perf_counter()

            with st.spinner("Running load test..."):
                with ThreadPoolExecutor(max_workers=load_users) as executor:
                    futures = [
                        executor.submit(run_single_load_request)
                        for _ in range(total_requests)
                    ]

                    for future in as_completed(futures):
                        results.append(future.result())

            total_time = round(time.perf_counter() - start_test, 2)
            success_count = sum(1 for r in results if r["success"])
            failure_count = total_requests - success_count
            avg_latency = round(sum(r["latency_ms"] for r in results) / len(results), 2)
            requests_per_sec = round(total_requests / total_time, 2)

            st.success("Load test completed.")
            r1, r2, r3, r4, r5 = st.columns(5)
            r1.metric("Total Requests", total_requests)
            r2.metric("Success", success_count)
            r3.metric("Failures", failure_count)
            r4.metric("Avg Latency", f"{avg_latency} ms")
            r5.metric("Req / Sec", requests_per_sec)

            load_df = pd.DataFrame(results)
            st.dataframe(load_df, use_container_width=True, hide_index=True)


def show_request_logs():
    st.markdown('<div class="section-title">📜 Request Logs - Self Healing Journey</div>', unsafe_allow_html=True)
    request_logs = safe_get(f"{API_BASE}/request-logs", [])

    if request_logs:
        logs_df = pd.DataFrame(request_logs)
        wanted_log_cols = [
            "id", "request_id", "city", "mode", "failure_type", "final_status",
            "error_type", "diagnosis", "healing_action", "validation_result",
            "incident_id", "latency_ms", "created_at",
        ]
        available_log_cols = [col for col in wanted_log_cols if col in logs_df.columns]
        logs_df = logs_df[available_log_cols]

        if "id" in logs_df.columns:
            logs_df.drop(columns=["id"], inplace=True)

        logs_df.reset_index(drop=True, inplace=True)
        logs_df.insert(0, "S.No", range(1, len(logs_df) + 1))

        def color_final_status(val):
            val = str(val).upper()
            if "SUCCESS" in val:
                return "background-color:#DCFCE7;color:#166534;font-weight:bold;"
            if "FAILED" in val or "ESCALATED" in val:
                return "background-color:#FEE2E2;color:#B91C1C;font-weight:bold;"
            return ""

        def color_failure(val):
            if str(val).lower() == "success":
                return "background-color:#DCFCE7;color:#166534;font-weight:bold;"
            return "background-color:#FEF3C7;color:#92400E;font-weight:bold;"

        def color_city(val):
            return "background-color:#DBEAFE;color:#1D4ED8;font-weight:bold;"

        styled_logs = logs_df.style
        if "city" in logs_df.columns:
            styled_logs = styled_logs.map(color_city, subset=["city"])
        if "failure_type" in logs_df.columns:
            styled_logs = styled_logs.map(color_failure, subset=["failure_type"])
        if "final_status" in logs_df.columns:
            styled_logs = styled_logs.map(color_final_status, subset=["final_status"])

        st.dataframe(styled_logs, use_container_width=True, hide_index=True)

        st.markdown("### 🔎 View / Delete Request Log")
        request_id = st.text_input("Enter or paste Request ID", placeholder="Paste request_id here...")

        if request_id:
            selected_log = logs_df[
                logs_df["request_id"].astype(str).str.strip() == request_id.strip()
            ]

            if not selected_log.empty:
                st.json(selected_log.iloc[0].to_dict())

                if st.button("🗑️ Delete Request Log"):
                    delete_response = requests.delete(
                        f"{API_BASE}/request-logs/{request_id.strip()}",
                        timeout=10,
                    )

                    if delete_response.status_code == 200:
                        result = delete_response.json()
                        if result.get("status") == "SUCCESS":
                            st.success("Request log deleted successfully.")
                            st.rerun()
                        else:
                            st.error(result.get("message", "Request log not found."))
                    else:
                        st.error("Failed to delete request log.")
            else:
                st.warning("Request ID not found.")
    else:
        st.info("No request logs yet. Generate weather output to create request logs.")


def show_sqlite_incidents():
    st.markdown('<div class="section-title">☷ Recent SQLite Incidents</div>', unsafe_allow_html=True)
    incidents = safe_get(f"{API_BASE}/incidents", [])

    if incidents:
        df = pd.DataFrame(incidents)
        wanted_cols = ["id", "city", "error_type", "severity", "message", "status", "action_taken"]
        available_cols = [col for col in wanted_cols if col in df.columns]
        df = df[available_cols]

        def color_status(val):
            val = str(val).upper()
            if "SUCCESS" in val or "SAVED" in val:
                return "background-color:#DCFCE7;color:#166534;font-weight:bold;"
            if "FAILED" in val or "MANUAL" in val:
                return "background-color:#FEE2E2;color:#B91C1C;font-weight:bold;"
            return ""

        def color_city(val):
            return "background-color:#DBEAFE;color:#1D4ED8;font-weight:bold;"

        def color_severity(val):
            val = str(val).upper()
            if val == "HIGH":
                return "background-color:#FECACA;color:#991B1B;font-weight:bold;"
            if val == "MEDIUM":
                return "background-color:#FEF3C7;color:#92400E;font-weight:bold;"
            if val == "LOW":
                return "background-color:#DCFCE7;color:#166534;font-weight:bold;"
            return ""

        styled_df = df.style
        if "status" in df.columns:
            styled_df = styled_df.map(color_status, subset=["status"])
        if "city" in df.columns:
            styled_df = styled_df.map(color_city, subset=["city"])
        if "severity" in df.columns:
            styled_df = styled_df.map(color_severity, subset=["severity"])

        st.dataframe(styled_df, use_container_width=True, hide_index=True)
    else:
        st.markdown("""
        <div class="card" style="text-align:center;padding:50px;">
            <h3>📭 No incidents found</h3>
            <p class="card-sub">Run a failure scenario to generate incidents</p>
        </div>
        """, unsafe_allow_html=True)


pages = [
    "🌦️ Weather Output",
    "🧭 Drift Detection",
    "🔁 Failure Flow",
    "🧾 Backend Response",
    "🎫 Incident + Ticket",
    "〽️ System Health",
    "📊 Evaluation Metrics",
    "🚀 Load Testing",
    "📜 Request Logs",
    "☷ SQLite Incidents",
    "ⓘ About",
]

with st.sidebar:
    st.markdown("## 🌦️ Self Healing<br>Weather API", unsafe_allow_html=True)
    st.caption("AI-Powered • Reliable • Self-Healing")
    st.divider()

    st.markdown("### Demo Controls")
    mode = st.radio("Provider Mode", ["live", "mock"], horizontal=True)

    st.markdown("### Failure Simulator")
    failure_type = st.selectbox(
        "Choose failure scenario",
        [
            "success",
            "network_error",
            "weather_api_down",
            "api_timeout",
            "rate_limit_429",
            "invalid_json",
            "llm_timeout",
            "invalid_api_key",
            "database_down",
            "schema_drift",
            "data_anomaly_drift",
        ],
    )

    st.markdown("### Output Tabs")
    selected_page = st.radio(
        "Choose output section",
        pages,
        label_visibility="collapsed",
        key="sidebar_output_tabs"
    )

st.markdown("""
<div class="main-title">🌦️ Self-Healing Weather Platform</div>
<div class="subtitle">Live weather + mock demo + LangGraph workflow + SQLite incident audit</div>
""", unsafe_allow_html=True)

show_top_cards()

st.markdown('<div class="section-title">Ask Weather</div>', unsafe_allow_html=True)
city = st.text_input("City", "Chennai", label_visibility="collapsed")

col1, col2, col3 = st.columns([3, 2, 3])
with col2:
    generate = st.button(
        "🌦️ Generate Weather Output",
        type="primary",
        use_container_width=True
    )

if "weather_data" not in st.session_state:
    st.session_state.weather_data = None

if generate:
    try:
        with st.spinner("Running self-healing workflow..."):
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
            st.session_state.weather_data = response.json()
    except Exception as exc:
        st.session_state.weather_data = None
        st.error(f"Request failed: {exc}")

weather_required_pages = [
    "🌦️ Weather Output",
    "🧭 Drift Detection",
    "🔁 Failure Flow",
    "🧾 Backend Response",
    "🎫 Incident + Ticket",
]

data = st.session_state.weather_data

if selected_page == "🌦️ Weather Output":
    if data:
        show_weather_output(data)
    else:
        st.info("Enter a city and click Generate Weather Output to view weather details here.")

elif selected_page == "🧭 Drift Detection":
    if data:
        show_drift(data)
    else:
        st.info("Run weather output to view drift detection details.")

elif selected_page == "🔁 Failure Flow":
    if data:
        show_failure_flow(data)
    else:
        st.info("Run weather output to view failure flow details.")

elif selected_page == "🧾 Backend Response":
    if data:
        show_backend_response(data)
    else:
        st.info("Run weather output to view the full backend response.")

elif selected_page == "🎫 Incident + Ticket":
    if data:
        show_incident_ticket(data)
    else:
        st.info("Run a failure scenario to view incident and ticket details.")

elif selected_page == "〽️ System Health":
    show_health()

elif selected_page == "📊 Evaluation Metrics":
    show_metrics()

elif selected_page == "🚀 Load Testing":
    show_load_testing()

elif selected_page == "📜 Request Logs":
    show_request_logs()

elif selected_page == "☷ SQLite Incidents":
    show_sqlite_incidents()

elif selected_page == "ⓘ About":
    st.markdown("""
    <div class="sidebar-box">
        <p><b>ⓘ About</b></p>
        <p>
        This system automatically detects failures, diagnoses root cause using LLM,
        heals itself using fallback strategies, verifies the fix, and logs everything
        for observability.
        </p>
        <hr>
        <p><b>Built with ❤️ using</b></p>
        <p>🔑 FastAPI</p>
        <p>🧠 LangGraph</p>
        <p>🔗 LangChain</p>
        <p>👑 Streamlit</p>
        <p>🗄️ SQLite</p>
        <p>✉️ Resend</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("""
<div class="footer">
    <b>Self Healing Weather API</b><br>
    AI-Powered Reliability
    <span style="float:right;">Built with ❤️ using FastAPI, LangGraph, LangChain & Streamlit</span>
</div>
""", unsafe_allow_html=True)
