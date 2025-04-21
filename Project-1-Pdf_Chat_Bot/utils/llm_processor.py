from transformers import pipeline

# Load a larger T5 model
summarizer = pipeline("summarization", model="t5-large", tokenizer="t5-large")  # Use t5-large

def summarize_text(text, max_length=512):
    """Summarize text using a larger T5 model."""
    summary = summarizer(text, max_length=max_length, min_length=100, do_sample=False)
    return summary[0]['summary_text']




from transformers import pipeline

# Load the summarizer pipeline
summarizer = pipeline("summarization", model="t5-large", tokenizer="t5-large")

# Chain-of-Thought Prompt Template
COT_PROMPT_TEMPLATE = """
Summarize the following commodity commentary using structured reasoning. Preserve all key information and ensure the summary can stand alone for retrieval or analysis. Follow these steps strictly:

1. Identify the **main commodity or commodities** being discussed.
2. Extract and list all **key commentary points**, including factual updates, market observations, or analyst opinions.
3. Highlight any **price trends**, **production forecasts**, **supply-demand dynamics**, or **policy/regulatory impacts**.
4. Capture relevant **time references** (e.g., "in March", "this month", "2023/24") to anchor insights temporally.
5. Mention any **geographic details** (countries, regions) associated with the commentary.
6. End with a **concise summary paragraph** that integrates the above insights into a coherent conclusion for downstream retrieval.

Text:
{text}


Text:
{text}
"""

def summarize_text(text, max_length=512):
    """Summarize text using T5 with chain-of-thought prompting."""
    prompt = COT_PROMPT_TEMPLATE.format(text=text.strip())
    
    summary = summarizer(
        text,
        max_length=max_length,
        min_length=100,
        do_sample=False
    )
    
    return summary[0]['summary_text']







# from transformers import pipeline

# # Load the summarization model
# summarizer = pipeline("summarization", model="t5-small")

# def chunk_text(text, max_length=500):
#     """Split text into smaller chunks to fit within model constraints."""
#     words = text.split()  # Split text by words
#     chunks = []
    
#     for i in range(0, len(words), max_length):
#         chunks.append(" ".join(words[i:i + max_length]))
    
#     return chunks

# def summarize_text(text, max_length=200):
#     """Summarize text using T5 model with chunking."""
#     text_chunks = chunk_text(text, max_length=500)  # Split long text

#     summaries = []
#     for chunk in text_chunks:
#         summary = summarizer(chunk, max_length=max_length, min_length=50, do_sample=False)
#         summaries.append(summary[0]['summary_text'])
    
#     return " ".join(summaries)  # Combine summaries of chunks
