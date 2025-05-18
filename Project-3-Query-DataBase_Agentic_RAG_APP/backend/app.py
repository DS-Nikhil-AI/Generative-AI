from flask import Flask, request, jsonify
from handlers.data_handler import DataHandler
from handlers.llm_handler import LLMHandler
import os

app = Flask(__name__)
data_handler = DataHandler()
llm_handler = LLMHandler()

@app.route("/upload", methods=["POST"])
def upload():
    files = request.files.getlist("files")
    paths = []
    for file in files:
        path = os.path.join("/tmp", file.filename)
        file.save(path)
        paths.append(path)
    keys = data_handler.load_csvs(paths)
    llm_handler.index_data(data_handler.get_all_data())
    return jsonify({"message": "Files uploaded", "dataframes": keys})

@app.route("/query", methods=["POST"])
def query():
    question = request.json.get("question")
    answer = llm_handler.query(question)
    return jsonify({"answer": answer})

if __name__ == "__main__":
    app.run(debug=True, port=5000)
