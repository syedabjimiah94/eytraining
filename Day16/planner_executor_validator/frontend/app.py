import requests
import streamlit as st

st.title("Multi-Agent AI")

query = st.text_area(
    "Enter your Question"
)

if st.button("Run Agents"):

    response = requests.post(
        "http://localhost:8000/chat",
        json={
            "query": query
        }
    )

    data = response.json()

    st.subheader("Planner")

    st.write(data["plan"])

    st.subheader("Final Answer")

    st.write(data["answer"])

    st.subheader("Verification")

    st.write(data["verification"])