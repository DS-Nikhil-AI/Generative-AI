QUERY_PROMPT_TEMPLATE = """
You are an expert analyst assistant. Use the following context from documents to answer the user’s question with clarity and reasoning. Do not repeat the documents — generate a concise, helpful answer.

Question: {query}
Context:
{docs}

Answer:
# """
doc_list = ""
