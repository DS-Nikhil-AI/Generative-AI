
import os
import uvicorn
from fastapi import FastAPI
from fastapi import UploadFile, File
from pydantic import BaseModel
from fastapi import FastAPI, UploadFile, File
from utils.query import QuerySearch
from utils.upload import UploadPdf

from sentence_transformers import SentenceTransformer
from utils.vector_store import VectorStore
from utils.pdf_processor import extract_text_from_pdf, generate_doc_id, chunk_text


app = FastAPI()

class QueryRequest(BaseModel):
    query: str
vector_store = VectorStore()
UPLOAD_DIR = "/tmp/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/upload/")
async def upload(file: UploadFile = File(...)):
    """Upload and process PDF file into retrievable vector chunks."""
     # use await for async
    temp_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(temp_path, "wb") as f:
        f.write(await file.read())
    text_data = extract_text_from_pdf(temp_path)
    full_text = "\n".join(text_data.values())
    chunks = chunk_text(full_text, max_length=2000, overlap=300)
    doc_id = generate_doc_id(temp_path)
    print(f"📄Chunking complete. Total chunks: {len(chunks)}")
    for i, chunk in enumerate(chunks):
        metadata = {
            "doc_id": doc_id,
            "filename": file.filename,
            "chunk_num": i}
        vector_store.add_documents([chunk], [metadata])
        print("✅ All chunks stored successfully.")
        return {"status": "success", "doc_id": doc_id, "chunks_stored": len(chunks)}

@app.post("/query/")
def query_docs_api(query_request: QueryRequest):
    query = query_request.query.strip()
    retrieved_docs, answer = QuerySearch(query).query_search()
    return {
        "answer": answer,
        "citations": [
            {
                "doc_id": doc["metadata"]["doc_id"],
                "chunk_num":doc["metadata"].get("chunk_num"),
                "score": doc["score"]
            }
            for doc in retrieved_docs
        ]
    }


# Now start this main app
if __name__ == "__main__":
    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=True)


