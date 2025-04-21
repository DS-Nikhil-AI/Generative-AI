import os
import pickle
from sentence_transformers import SentenceTransformer, util
import torch

class VectorStore:
    def __init__(self, persist_dir="vector_store_data"):
        self.persist_dir = persist_dir
        os.makedirs(self.persist_dir, exist_ok=True)
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        self.docs_path = os.path.join(self.persist_dir, "documents.pkl")
        self.meta_path = os.path.join(self.persist_dir, "metadata.pkl")
        self.embed_path = os.path.join(self.persist_dir, "embeddings.pt")
        self.documents = []
        self.metadata = []
        self.embeddings = []
        self._load()

    def add_documents(self, docs, metadatas):
        new_embeddings = self.model.encode(docs, convert_to_tensor=True)
        if isinstance(new_embeddings, torch.Tensor):
            new_embeddings = list(new_embeddings)

        self.documents.extend(docs)
        self.metadata.extend(metadatas)
        self.embeddings.extend(new_embeddings)

        self._save()

    def search(self, query, top_k=5, rerank=True, hybrid=False):
        if not self.embeddings:
            return []

        query_embedding = self.model.encode(query, convert_to_tensor=True)

        if len(self.embeddings) == 1:
            scores = util.pytorch_cos_sim(self.embeddings[0], query_embedding).unsqueeze(0)
        else:
            embeddings_tensor = torch.stack(self.embeddings)
            scores = util.pytorch_cos_sim(embeddings_tensor, query_embedding).squeeze()

        # Ensure scores is iterable
        if isinstance(scores, float) or scores.dim() == 0:
            scores = torch.tensor([scores.item()])

        flat_scores = scores.squeeze().tolist()
        if isinstance(flat_scores, float):
            flat_scores = [flat_scores]
        scored_results = list(enumerate(flat_scores))
        scored_results.sort(key=lambda x: x[1], reverse=True)
        results = []
        for idx, score in scored_results[:top_k]:
            if isinstance(score, list):
                score = score[0]
            elif isinstance(score, torch.Tensor):
                score = score.item()
            results.append({
                "text": self.documents[idx],
                "score": float(score),
                "metadata": self.metadata[idx]
            })

        if hybrid:
            keyword_bonus = [1 if query.lower() in doc["text"].lower() else 0 for doc in results]
            for i in range(len(results)):
                results[i]["score"] += 0.1 * keyword_bonus[i]
            results.sort(key=lambda x: x["score"], reverse=True)

        if rerank:
            results.sort(key=lambda x: x["score"], reverse=True)

        return results

    def _save(self):
        with open(self.docs_path, "wb") as f:
            pickle.dump(self.documents, f)
        with open(self.meta_path, "wb") as f:
            pickle.dump(self.metadata, f)
        torch.save(self.embeddings, self.embed_path)
        print(f"💾 Vector store saved with {len(self.documents)} documents.")

    def _load(self):
        if all(os.path.exists(path) for path in [self.docs_path, self.meta_path, self.embed_path]):
            with open(self.docs_path, "rb") as f:
                self.documents = pickle.load(f)
            with open(self.meta_path, "rb") as f:
                self.metadata = pickle.load(f)
            self.embeddings = torch.load(self.embed_path)
            print(f"✅ VectorStore loaded with {len(self.documents)} documents.")
        else:
            print("⚠️ No persisted vector store found. Starting fresh.")
