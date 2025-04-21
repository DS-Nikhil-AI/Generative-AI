from utils.vector_store import VectorStore
from utils.pdf_processor import extract_text_from_pdf, generate_doc_id, chunk_text
from sentence_transformers import SentenceTransformer



class UploadPdf:
    def __init__(self, path, file):
        self.text_data = None
        self.temp_path = path
        self.full_text = None
        self.chunks  = None
        self.temp_path = None
        self.vector_store = VectorStore()
        self.file = file

    def vector_db_upload(self):
        self.text_data = extract_text_from_pdf(self.temp_path)
        self.full_text = "\n".join(self.text_data.values())
        self.chunks = chunk_text(self.full_text, max_length=1000, overlap=300)
        doc_id = generate_doc_id(self.temp_path)
        print(f"📄Chunking complete. Total chunks: {len(self.chunks)}")

        for i, chunk in enumerate(self.chunks):
            metadata = {
                "doc_id": doc_id,
                "filename": self.file.filename,
                "chunk_num": i
            }
            self.vector_store.add_documents([chunk], [metadata])
        print("✅ All chunks stored successfully.")
        return {"status": "success", "doc_id": doc_id, "chunks_stored": len(self.chunks)}