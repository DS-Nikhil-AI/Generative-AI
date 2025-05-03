import os
import json
import pandas as pd
from app.config import Config
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langchain_core.tools import tool
from typing import TypedDict, Annotated
import os
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
        return upload_path

    @staticmethod
    def handle_comments(llm):
        os.makedirs(os.path.dirname(Config.RESOLVED_FOLDER), exist_ok=True)
        os.makedirs(os.path.dirname(Config.UNRESOLVED_FOLDER), exist_ok=True)
        os.makedirs(os.path.dirname(Config.PATTERN_FOLDER), exist_ok=True)
        os.makedirs(os.path.dirname(Config.SUMMARY_FOLDER), exist_ok=True)

        df_comments = pd.read_csv(Config.REPLY_FILE, encoding='latin1')
        summaries = []
        c = 0
        df_comments = pd.read_csv(Config.REPLY_FILE, encoding='latin1')
        summaries = []
        c=0
        for idx, row in df_comments.iterrows():
            c=c+1
            if c<1000:
                transaction_id = str(row['Transaction ID'])
                comment = row['Comments']
                prompt = (
                    f"Transaction ID: {transaction_id}\n"
                    f"Comment: {comment}\n"
                    "Step 1: Determine if this case is Resolved or Unresolved.\n"
                    "Step 2: If Resolved, explain the reason shortly and suggest if similar cases can be closed automatically.\n"
                    "Step 3: If Unresolved, summarize why it is unresolved and suggest clear next steps.\n"
                    "Please think step-by-step like a human agent before giving the final response."
                )

                result = llm.invoke(prompt)
                print(f"llm_result for {transaction_id}: {result}")

                result_lower = result.lower()
                if "resolved" in result_lower:
                    save_path = os.path.join(Config.RESOLVED_FOLDER, f"{transaction_id}.txt")
                    with open(save_path, 'w', encoding='utf-8') as f:
                        f.write(f"Resolution Details:\n{result}\nOriginal Comment:\n{comment}")

                    pattern_path = os.path.join(Config.PATTERN_FOLDER, f"{transaction_id}_pattern.txt")
                    with open(pattern_path, 'w', encoding='utf-8') as f:
                        f.write(f"Identified Pattern:\n{result}")

                elif "unresolved" in result_lower:

                    unresolved_summary_path = os.path.join(Config.SUMMARY_FOLDER, f"{transaction_id}_summary.txt")
                    with open(unresolved_summary_path, 'w', encoding='utf-8') as f:
                        f.write(f"Summary Why Unresolved:\n{result}\nOriginal Comment:\n{comment}")

                    # Use Case 3: Suggest next steps
                    next_steps_prompt = (
                        f"Transaction ID: {transaction_id}\n"
                        f"Comment: {comment}\n"
                        "Since this case is Unresolved, list 3 actionable next steps a finance support agent should take to resolve it."
                    )
                    next_steps_result = llm.invoke(next_steps_prompt)

                    unresolved_steps_path = os.path.join(Config.UNRESOLVED_FOLDER, f"{transaction_id}_next_steps.txt")
                    with open(unresolved_steps_path, 'w', encoding='utf-8') as f:
                        f.write(f"Suggested Next Steps:\n{next_steps_result}")

                else:
                    print(f"[WARN] Could not clearly classify result for Transaction ID: {transaction_id}")

                summaries.append({
                    "Transaction ID": transaction_id,
                    "result": result
                })
                print()

            print("✅ Successfully processed all comments.")

            return summaries
