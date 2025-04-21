
from transformers import pipeline
from utils.vector_store import VectorStore
from fastapi import  HTTPException
from processing.text_processing import clean_text
from constant.constant import doc_list, QUERY_PROMPT_TEMPLATE

class QuerySearch:
    def __init__(self, query: str)->None:
        self.model = None
        self.vector_db = None
        self.retrieved_docs = None
        self.query = query
        self.answer = None
        self.response = None
        self.vector_db = VectorStore()
        self.doc_list = doc_list
    def query_search(self):
        self.model = pipeline("text2text-generation", model="google/flan-t5-large", tokenizer="google/flan-t5-large")
        # Load persisted vector store (it auto-loads on init)
        self.vector_db = VectorStore(persist_dir="vector_store_data")
        # 🔍 Vector search with rerank & hybrid
        self.retrieved_docs = self.vector_db.search(self.query, top_k=5, rerank=True, hybrid=True)
        if not self.retrieved_docs:
            raise HTTPException(status_code=404, detail="No relevant documents found.")
        for i, doc in enumerate(self.retrieved_docs):
            clean_chunk = clean_text(doc["text"])
            self.doc_list += f"[Doc {i+1}]: {clean_chunk}\n"
            print(f"\n[Doc {i+1}]:\n{doc['text'][:500]}")

        prompt = QUERY_PROMPT_TEMPLATE.format(query=self.query, docs=doc_list.strip())

        self.response = self.model(prompt, max_length=2863, do_sample=False)
        self.answer = self.response[0]["generated_text"]
        return self.retrieved_docs, self.answer