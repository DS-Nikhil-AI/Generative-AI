import os
import json
from typing import TypedDict
from app.config import Config
from langgraph.graph import StateGraph, END
import pandas as pd


class CommentState(TypedDict):
    transaction_id: str
    comment: str
    result: str
    status: str  # "resolved" or "unresolved"
    email_verified: bool

class ReconciliationHandler:

    @staticmethod
    def preprocess_raw_data():
        df = pd.read_csv(Config.RAW_FILE)
        df['recon_sub_status'] = df['recon_sub_status'].apply(json.loads)
        expanded_cols = df['recon_sub_status'].apply(pd.Series)
        expanded_cols = expanded_cols.rename(lambda x: f'recon_sub_status_{x}', axis=1)
        df = pd.concat([df.drop(columns=['recon_sub_status']), expanded_cols], axis=1)
        df = df[df['recon_sub_status_amount'] == 'Not Found-SysB']
        df = df[['txn_ref_id', 'sys_a_amount_attribute_1', 'sys_a_date']]
        upload_path = (Config.UPLOAD_FOLDER)
        os.makedirs(os.path.dirname(upload_path), exist_ok=True)
        df.to_csv(upload_path, index=False)
        print("### preprocessing completed..")
        return upload_path


    @staticmethod
    def handle_comments(llm):
        # Ensure output directories exist
        os.makedirs(Config.RESOLVED_FOLDER, exist_ok=True)
        os.makedirs(Config.UNRESOLVED_FOLDER, exist_ok=True)
        os.makedirs(Config.PATTERN_FOLDER, exist_ok=True)
        os.makedirs(Config.SUMMARY_FOLDER, exist_ok=True)

        df_comments = pd.read_csv(Config.REPLY_FILE, encoding='latin1')

        # === NODE 1: Classifier ===
        def classify_node(state: CommentState) -> CommentState:
            prompt = (
                f"Transaction ID: {state['transaction_id']}\n"
                f"Comment: {state['comment']}\n"
                "Step 1: Determine if this case is Resolved or Unresolved.\n"
                "Step 2: If Resolved, explain briefly and suggest if similar cases can be closed automatically.\n"
                "Step 3: If Unresolved, summarize the reason and suggest next steps.\n"
                "Think step-by-step like a human agent."
            )
            result = llm.invoke(prompt)
            print(f"classify_node for : {result}")
            status = "resolved" if "resolved" in result.lower() else "unresolved"
            return {**state, "result": result, "status": status}

        # === NODE 2: Handle Resolved ===
        def handle_resolved_node(state: CommentState) -> CommentState:
            txn = state["transaction_id"]
            result = state["result"]
            comment = state["comment"]

            with open(os.path.join(Config.RESOLVED_FOLDER, f"{txn}.txt"), 'w', encoding='utf-8') as f:
                f.write(f"Resolution Details:\n{result}\nOriginal Comment:\n{comment}")

            with open(os.path.join(Config.PATTERN_FOLDER, f"{txn}_pattern.txt"), 'w', encoding='utf-8') as f:
                f.write(f"Identified Pattern:\n{result}")

            return state

        # === NODE 3: Handle Unresolved ===
        def handle_unresolved_node(state: CommentState) -> CommentState:
            txn = state["transaction_id"]
            result = state["result"]
            comment = state["comment"]

            with open(os.path.join(Config.SUMMARY_FOLDER, f"{txn}_summary.txt"), 'w', encoding='utf-8') as f:
                f.write(f"Summary Why Unresolved:\n{result}\nOriginal Comment:\n{comment}")

            prompt = (
                f"Transaction ID: {txn}\n"
                f"Comment: {comment}\n"
                "Since unresolved, list 3 next actions a support agent should take."
            )
            next_steps = llm.invoke(prompt)

            with open(os.path.join(Config.UNRESOLVED_FOLDER, f"{txn}_next_steps.txt"), 'w', encoding='utf-8') as f:
                f.write(f"Suggested Next Steps:\n{next_steps}")

            return state

        # === Conditional Router ===
        def router(state: CommentState) -> str:
            return "handle_resolved" if state["status"] == "resolved" else "handle_unresolved"

        # === LangGraph ===
        graph = StateGraph(CommentState)
        graph.add_node("classify", classify_node)
        graph.add_node("handle_resolved", handle_resolved_node)
        graph.add_node("handle_unresolved", handle_unresolved_node)

        graph.set_entry_point("classify")
        graph.add_conditional_edges("classify", router, {
            "handle_resolved": "handle_resolved",
            "handle_unresolved": "handle_unresolved"
        })

        graph.add_edge("handle_resolved", END)
        graph.add_edge("handle_unresolved", END)

        app = graph.compile()

        summaries = []
        for idx, row in df_comments.iterrows():
            txn_id = str(row["Transaction ID"])
            comment = row["Comments"]
            input_state = {
                "transaction_id": txn_id,
                "comment": comment,
                "result": "",
                "status": ""
            }
            

            final_state = app.invoke(input_state)
            summaries.append({
                "Transaction ID": final_state["transaction_id"],
                "status": final_state["status"],
                "result": final_state["result"]
            })
            print(f"summaries { txn_id}: {final_state}")

        print("✅ All comments processed via LangGraph branching.")
        return summaries
