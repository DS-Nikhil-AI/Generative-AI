from flask import Flask, jsonify
from app.agents.reconciliation_agent import create_reconciliation_workflow

app = Flask(__name__)

@app.route('/start_reconciliation', methods=['GET'])
def start_reconciliation():
    try:
        result = create_reconciliation_workflow()
        return jsonify({"status": "success", "details": result}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5000)
    # app.run(debug=False, use_reloader=False)
