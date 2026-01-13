from fastapi import FastAPI
from pydantic import BaseModel
import pandas as pd
from typing import Literal

from llm import ask_llm
from llm_rag import RAGCodeGen
from executor import run_pandas_code

app = FastAPI(title="LLM CSV Analyzer")


# ---------- Request / Response Models ----------

class QueryRequest(BaseModel):
    csv_data: list[dict]
    question: str
    llm_provider: Literal["updated model", "base model",] = "updated model"


class QueryResponse(BaseModel):
    code: str
    result: object
    result_type: str


# ---------- Endpoint ----------

@app.post("/analyze", response_model=QueryResponse)
def analyze(req: QueryRequest):

    # Reconstruct DataFrame
    df = pd.DataFrame(req.csv_data)

    # Ask LLM for Pandas code
    if req.llm_provider == "updated model":
        code = RAGCodeGen(req.question).generate()
    else:
        code = ask_llm(req.question, df.columns.tolist())

    print(code)

    try:
        # First attempt
        output = run_pandas_code(df, code)

    except TypeError as e:
        # Auto-fix common pandas aggregation failure
        if "agg function failed" in str(e):
            fixed_code = code.replace(".mean()", ".mean(numeric_only=True)")
            output = run_pandas_code(df, fixed_code)
            code = fixed_code  # return corrected code to user
        else:
            raise

    except Exception as e:
        return {
            "code": code,
            "result": f"ERROR: {e}",
            "result_type": "error",
        }

    # ---------- Normalize Output for JSON ----------

    if isinstance(output, pd.DataFrame):
        result = output.to_dict(orient="records")
        result_type = "dataframe"

    elif isinstance(output, pd.Series):
        result = output.to_dict()
        result_type = "series"

    else:
        result = output
        result_type = "scalar"

    return {
        "code": code,
        "result": result,
        "result_type": result_type,
    }