# 🧾 Reconciliation Comment Classifier with LangGraph

This project classifies financial reconciliation comments using a language model and LangGraph agent framework.
It identifies whether a case is **Resolved** or **Unresolved**, saves relevant analysis, and provides next steps for unresolved cases.

---

## 📦 Features

- ✅ Classifies comments as **Resolved** or **Unresolved**.
- 📄 For resolved cases:
  - Saves resolution explanation.
  - Extracts repeatable resolution patterns.
- ⚠️ For unresolved cases:
  - Summarizes issue.
  - Suggests 3 actionable next steps.
- 👀 Includes a mock **Reviewer Agent** to simulate email verification.
- 🧠 Uses **LangGraph** to define a multi-step agent workflow.
- 📁 Organizes output files into appropriate folders.

---

## 📁 Folder Structure

reconciliation-agent/ ├── config.py # Configuration file with paths ├── reconciliation_handler.py # Main logic for handling comments
├── llm.py # Wrapper for LLM (e.g., OpenAI via LangChain) 
├── README.md # This readme file 
├── requirements.txt # Dependencies list 
│ ├── data/ # Data folder │ ├── raw_file.csv # Input raw reconciliation data 
│ └── reply_file.csv # Comments for classification 
│ └── output/ # Classification results 
  ├── resolved/ # Text files for resolved transactions
  ├── unresolved/ # Suggested next steps for unresolved 
  ├── pattern/ # Patterns extracted from resolved cases 
  └── summary/ # Unresolved issue summaries
