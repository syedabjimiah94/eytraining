import streamlit as st
import requests

# ---------------------------------------------------
# Page Config
# ---------------------------------------------------
st.set_page_config(
    page_title="AutoHealAI",
    page_icon="🌦",
    layout="wide"
)

# ---------------------------------------------------
# Custom CSS
# ---------------------------------------------------
st.markdown("""
<style>

/* Background */
.main {
    background-color: #F5F7FA;
}

/* Main Container */
.block-container{
    padding-top:2rem;
    padding-bottom:2rem;
}

/* Main Title */
h1{
    color:#0F172A;
    font-size:42px;
    font-weight:800;
    text-align:center;
}

/* Subtitle (st.caption) */
div[data-testid="stCaptionContainer"]{
    text-align:center;
    color:#64748B;
    font-size:18px;
}

/* Labels (Select Demo Mode, Enter City) */
label{
    color:#1E3A8A !important;
    font-weight:600 !important;
    font-size:16px !important;
}

/* Selectbox & Textbox */
.stSelectbox div[data-baseweb="select"],
.stTextInput input{
    border-radius:10px;
}

/* Button */
.stButton>button{
    width:220px;
    height:52px;
    border-radius:10px;
    background:#2563EB;
    color:white;
    font-size:20px;
    font-weight:bold;
    border:none;
}

.stButton>button:hover{
    background:#1D4ED8;
    color:white;
}

/* Metric Cards */
div[data-testid="metric-container"]{
    background:white;
    border-radius:15px;
    padding:18px;
    box-shadow:0px 3px 12px rgba(0,0,0,.10);
}

/* Metric Label */
div[data-testid="metric-container"] label{
    color:#475569 !important;
}

/* Metric Value */
div[data-testid="metric-container"] div[data-testid="stMetricValue"]{
    color:#2563EB;
    font-size:30px;
    font-weight:bold;
}

/* Expander */
.streamlit-expanderHeader{
    color:#1E3A8A;
    font-weight:bold;
}

/* Success Box */
div[data-testid="stAlert"]{
    border-radius:12px;
}

/* Horizontal Line */
hr{
    border:1px solid #E2E8F0;
}

</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------
# Header
# ---------------------------------------------------

# st.title("🌦 AutoHealAI - Weather Monitoring System")
st.markdown("""
<h1>🌦 AutoHealAI</h1>
<h4 style='text-align:center;color:#64748B;'>
AI-powered Self-Healing Weather Monitoring Platform
</h4>
""", unsafe_allow_html=True)


st.divider()

# ---------------------------------------------------
# Input Section
# ---------------------------------------------------

col1, col2 = st.columns(2)

with col1:

    mode = st.selectbox(
        "🎮 Select Demo Mode",
        [
            "SUCCESS",
            "TIMEOUT",
            "SLOW_RESPONSE",
            "API_DOWN",
            "INVALID_RESPONSE"
        ]
    )

with col2:

    city = st.text_input(
        "📍 Enter City",
        "Chennai"
    )

st.write("")

left, center, right = st.columns([2,1,2])

with center:
    get_weather = st.button("☁ Get Weather")

st.divider()

# ---------------------------------------------------
# Weather Button
# ---------------------------------------------------

if get_weather:

    try:

        url = f"http://localhost:8000/weather/{city}?mode={mode}"

        response = requests.get(url, timeout=20)

        result = response.json()

        user = result["user_response"]

        # -------------------------------------
        # SUCCESS
        # -------------------------------------

        if user["status"] == "SUCCESS":

            st.success(user["message"])

            weather = user["weather"]

            st.markdown("## 🌤 Weather Details")

            c1,c2,c3,c4 = st.columns(4)

            with c1:
                st.metric(
                    "📍 City",
                    weather["city"]
                )

            with c2:
                st.metric(
                    "🌡 Temperature",
                    weather["temperature"]
                )

            with c3:
                st.metric(
                    "☁ Condition",
                    weather["condition"]
                )

            with c4:
                st.metric(
                    "💧 Humidity",
                    weather["humidity"]
                )

        # -------------------------------------
        # FAILURE
        # -------------------------------------

        else:

            st.error(user["message"])

        st.write("")
        st.divider()

        # -------------------------------------
        # Workflow
        # -------------------------------------

        workflow = result["workflow"]
        monitor = workflow["monitoring"]
        diagnosis = workflow["diagnosis"]
        healing = workflow["healing"]
        verification = workflow["verification"]

        with st.expander("🔍 View Self-Healing Workflow", expanded=False):

            # ---------------- Monitoring ----------------
            st.markdown("### 🛰 Monitoring Agent")

            if monitor:
                st.info(
        f"""
        **Status :** {monitor['status']}

        **Severity :** {monitor.get('severity','-')}

        **Message :** {monitor.get('message','-')}
        """
                )

            # ---------------- Diagnosis ----------------
            if diagnosis:

                st.markdown("### 🧠 Diagnosis Agent")

                st.warning(
        f"""
        **Root Cause :** {diagnosis['root_cause']}

        **Confidence :** {diagnosis['confidence']}

        **Healable :** {diagnosis['healable']}

        **Recommendation :**
        {diagnosis['recommended_action']}
        """
                )

            # ---------------- Healing ----------------
            if healing:

                st.markdown("### 🔧 Healing Agent")

                if healing["status"] == "SUCCESS":

                    st.success(
        f"""
        ✅ **Auto-Healed Successfully**

        Retry Attempt : {healing['retry_attempt']}

        Action : {healing['action']}
        """
                    )

                else:

                    st.error(
        f"""
        ❌ **Healing Failed**

        Retry Attempt : {healing['retry_attempt']}

        Action : {healing['action']}
        """
                    )

            # ---------------- Verification ----------------
            if verification:

                st.markdown("### ✅ Verification Agent")

                if verification["status"] == "SUCCESS":

                    st.success(
                        "Weather API verified successfully."
                    )

                else:

                    st.error(
                        "Verification failed. API is still unhealthy."
                    )

    except Exception as e: st.error(f"Unable to connect to FastAPI server.\n\n{e}")