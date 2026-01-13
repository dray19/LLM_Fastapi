from rag_model.rag_multi_query import LLMPredictorRAG_MultiQuery



class RAGCodeGen:
    def __init__(self, message: str):
        self.message = message

    def build_messages(self):
        text = [
            {
                "role": "system",
                "content": (
            "You are a code generator. Respond with ONLY valid Python code. "
            "No explanations. No markdown. No imports. NO sample data.\n\n"
            "Rules:\n"
            "- You MUST assume a pandas DataFrame named df already exists in memory and is the ONLY input dataset.\n"
            "- Generate code that operates ONLY on df or intermediate objects derived directly from df.\n"
            "- Do NOT reference external variables, files, paths, configs, or objects not derived from df.\n"
            "- Do NOT read from or write to disk.\n"
            "- Do NOT make network calls.\n"
            "- Do NOT use randomness or non-deterministic behavior.\n"
            "- Do NOT use unsafe operations (eval, exec, compile, ast, subprocess, os, shell commands).\n"
            "- Do NOT mutate df unless explicitly requested; prefer creating new objects.\n"
            "- Avoid chained assignment; use .loc for assignments.\n"
            "- Do NOT assume column dtypes; handle numeric vs non-numeric safely.\n"
            "- For groupby aggregations, use numeric_only=True when appropriate.\n"
            "- Guard against missing columns: if required columns are missing, assign result to "
            "a clear error string like \"ERROR: missing columns: ['col1', 'col2']\".\n"
            "- Always assign the final output to a variable named result.\n"
            "- Do NOT print unless explicitly requested.\n"
            "- Keep the code minimal, deterministic, and directly executable."
                )
            },
            {
                "role": "user",
                "content": (
                    self.message
                )
            }
        ]
        return text

    @staticmethod
    def clean_response(answer: str) -> str:
        response = answer.replace("```python", "").replace("```", "").strip()
        # response = response.replace("result =", "").strip()
        return response

    def generate(self) -> str:
        code_docs = LLMPredictorRAG_MultiQuery.load_jsonl("/Users/drazenzack/Desktop/LLM_Fastapi/rag_data/train.jsonl")
        llm = LLMPredictorRAG_MultiQuery()
        llm.set_documents(code_docs)
        user_prompt = self.build_messages()  
        print("USER PROMPT:\n", user_prompt[1]['content'])
        answer = llm.generate_response_rag(user_prompt[1]['content'])
        return self.clean_response(answer)
