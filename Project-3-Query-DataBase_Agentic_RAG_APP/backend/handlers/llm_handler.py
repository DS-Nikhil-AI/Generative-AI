from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
import torch
import pandas as pd

class LLMHandler:
    def __init__(self, model_name="mistralai/Mistral-7B-Instruct-v0.1"):
        self.embedder = SentenceTransformer("all-MiniLM-L6-v2")
        self.model = AutoModelForCausalLM.from_pretrained(model_name, torch_dtype=torch.float16, device_map="auto")
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.rag_chunks = []

    def index_data(self, dataframes):
        self.rag_chunks.clear()
        for name, df in dataframes.items():
            for _, row in df.iterrows():
                text = f"{name}: " + ", ".join(f"{col}: {val}" for col, val in row.items())
                embedding = self.embedder.encode(text)
                self.rag_chunks.append({"text": text, "embedding": embedding})

    def query(self, question):
        query_vec = self.embedder.encode(question)
        ranked = sorted(
            self.rag_chunks,
            key=lambda x: cosine_similarity([query_vec], [x["embedding"]])[0][0],
            reverse=True
        )
        top_k_texts = "\n".join(chunk["text"] for chunk in ranked[:5])
        prompt = f"Context:\n{top_k_texts}\n\nQuestion: {question}\nAnswer:"
        inputs = self.tokenizer(prompt, return_tensors="pt", truncation=True).to("cuda")
        outputs = self.model.generate(**inputs, max_new_tokens=150)
        return self.tokenizer.decode(outputs[0], skip_special_tokens=True)
