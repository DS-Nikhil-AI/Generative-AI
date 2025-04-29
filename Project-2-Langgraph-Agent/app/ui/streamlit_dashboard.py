import streamlit as st
import requests

st.title("Financial Reconciliation")

if st.button("Start Reconciliation Process"):
    with st.spinner("Processing..."):
        try:
            response = requests.get("http://127.0.0.1:5000/start_reconciliation")
            data = response.json()
            # st.text("data", data)
            if data["status"] == "success":
                st.success("Reconciliation Completed ✅")
                st.json(data["details"])
            else:
                st.error(f"Error: {data['message']}")
        except Exception as e:
            st.error(f"Server not reachable or error: {str(e)}")
