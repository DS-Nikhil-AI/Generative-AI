import os
import json
import boto3
from PyPDF2 import PdfReader
import hashlib
from typing import List

def extract_text_from_pdf(pdf_path):
    """Extract text from PDF by page."""
    reader = PdfReader(pdf_path)
    text_data = {}

    for page_num in range(len(reader.pages)):
        page = reader.pages[page_num]
        page_text = page.extract_text()
        if page_text:
            text_data[page_num] = page_text.strip()
        else:
            text_data[page_num] = ""

    return text_data

def generate_doc_id(pdf_path):
    """Generate a unique document ID."""
    with open(pdf_path, "rb") as f:
        file_hash = hashlib.md5(f.read()).hexdigest()
    return file_hash

def chunk_text(text, max_length=500, overlap=200):
    words = text.split()
    chunks = []
    i = 0
    while i < len(words):
        chunk = words[i:i + max_length]
        chunks.append(" ".join(chunk))
        i += max_length - overlap
    return chunks
