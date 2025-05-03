from langchain.llms import HuggingFacePipeline
from transformers import pipeline
from app.handlers.reconciliation_handler import ReconciliationHandler

def load_local_llm():
    import torch
    pipe = pipeline(
        "text2text-generation",
        model="google/flan-t5-base",
        tokenizer="google/flan-t5-base",
        max_length=512,
        device=0 if torch.cuda.is_available() else -1
    )
    llm = HuggingFacePipeline(pipeline=pipe)
    return llm

def create_reconciliation_workflow():
    llm = load_local_llm()

    upload_path = ReconciliationHandler.preprocess_raw_data()
    summaries = ReconciliationHandler.handle_comments(llm)
    relative_path = upload_path[upload_path.lower().index('app'):]

    return {
        "upload_path": relative_path,
        "summaries": summaries
    }
