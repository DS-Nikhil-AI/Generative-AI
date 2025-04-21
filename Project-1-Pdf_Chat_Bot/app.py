import streamlit as st
import requests
import hashlib

API_URL_UPLOAD = "http://localhost:8000/upload/"
API_URL_QUERY = "http://localhost:8000/query/"

# File hash function to detect file changes
def file_hash(file_bytes):
    return hashlib.md5(file_bytes).hexdigest()

st.title("📚 PDF Commodity Summarizer")

# File Upload
st.subheader("Upload PDF for Processing")
uploaded_file = st.file_uploader("Choose a PDF...", type="pdf")

if uploaded_file:
    file_bytes = uploaded_file.read()

    # Compute hash of uploaded file
    current_file_hash = file_hash(file_bytes)

    # Check if file already uploaded using session state
    if "last_uploaded_file_hash" not in st.session_state or \
       st.session_state.last_uploaded_file_hash != current_file_hash:
        
        with st.spinner("Uploading and processing..."):
            files = {"file": (uploaded_file.name, file_bytes, "application/pdf")}
            response = requests.post(API_URL_UPLOAD, files=files)

        if response.status_code == 200:
            st.success("✅ PDF uploaded and processed successfully!")
            st.session_state.last_uploaded_file_hash = current_file_hash
            st.session_state.uploaded = True
        else:
            st.error("❌ Error uploading the PDF!")
            st.session_state.uploaded = False
    else:
        st.info("ℹ️ This PDF has already been uploaded and processed.")
else:
    st.session_state.uploaded = False

# Query Section
st.subheader("Search Across Uploaded PDFs")
query = st.text_input("Enter your query")

if st.button("Search"):
    if not st.session_state.get("uploaded"):
        st.warning("Please upload a PDF first.")
    elif query.strip() == "":
        st.warning("Enter a query before searching.")
    else:
        with st.spinner("Generating answer..."):
            headers = {"Content-Type": "application/json"}
            response = requests.post(API_URL_QUERY, json={"query": query}, headers=headers)
            

        if response.status_code == 200:
            results = response.json()
            st.markdown(f"### 🤖 Answer:\n{results['answer']}")
            st.markdown("**📎 Citations:**")
            for doc in results["citations"]:
                st.write(f"• {doc}")    
        else:
            st.text(response.text)
            st.error("❌ No relevant data found.")
