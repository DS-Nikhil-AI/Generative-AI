# Query DataBase Agentic RAG  App with Mistral LLM

This project allows you to upload multiple CSV files, embed them with `sentence-transformers`, and ask questions using an open-source LLM (`mistralai/Mistral-7B-Instruct-v0.1`) with Retrieval-Augmented Generation (RAG).

---

## 📦 Features

- Multiple CSV Uploads
- Embedding-based Retrieval using `all-MiniLM-L6-v2`
- Mistral 7B Instruct LLM for natural language answers
- Flask API backend
- Streamlit frontend

---

## 🚀 Run the App

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Start the Flask Backend

```bash
cd backend
python app.py
```

### 3. Start the Streamlit Frontend

```bash
cd ../frontend
streamlit run app.py
```

---

## 📁 File Structure

```
rag_csv_app/
├── backend/
│   ├── app.py
│   └── handlers/
│       ├── data_handler.py
│       └── llm_handler.py
├── frontend/
│   └── app.py
├── requirements.txt
└── README.md
```

---
