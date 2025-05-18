import streamlit as st
import requests

st.title("📊 DataBase Quering using Mistral LLM + RAG")

st.sidebar.header("Upload CSV Files")
uploaded_files = st.sidebar.file_uploader("Choose CSV files", type="csv", accept_multiple_files=True)

if st.sidebar.button("Upload to Backend"):
    files = [("files", (f.name, f, "text/csv")) for f in uploaded_files]
    res = requests.post("http://localhost:5000/upload", files=files)
    st.success(f"Upload Result: {res.json()}")

st.header("Ask a Question")
question = st.text_input("Enter your question:")

if st.button("Submit Question") and question:
    response = requests.post("http://localhost:5000/query", json={"question": question})
    answer = response.json().get("answer")
    st.subheader("Answer")
    st.write(answer)
