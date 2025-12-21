from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline

MODEL_NAME = "Qwen/Qwen2-1.5B-Instruct"  # small + fast
# MODEL_NAME = "Qwen/Qwen2-7B-Instruct"  # better quality

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME,
    device_map="auto",
    torch_dtype="auto"
)

llm = pipeline(
    "text-generation",
    model=model,
    tokenizer=tokenizer,
    max_new_tokens=200,
    temperature=0.1,
)


def clean_code(text: str) -> str:
    """
    Extract only valid executable pandas code.
    """
    lines = []

    for line in text.splitlines():
        line = line.strip()

        # Skip empty or non-code lines
        if not line:
            continue

        # Hard filters
        if line.startswith(("import", "from")):
            continue
        if "read_csv" in line:
            continue
        if "answer" in line.lower():
            continue
        if line.startswith(("```", '"""', "'''")):
            continue

        # Only allow result statements
        if line.startswith(("result","return")):
            lines.append(line)

    return "\n".join(lines)


def ask_llm(question: str, columns: list[str]) -> str:
    prompt = f"""
You are a Python data analyst.

The dataframe is named df.
Columns: {columns}

STRICT RULES:
- Output ONLY Python code
- No explanations
- No markdown
- No comments
- No imports
- Use pandas only
- Assign the final output to a variable named result
- Begin code with: result = Do not write anything before it.

Question:
{question}
""".strip()

    response = llm(prompt)[0]["generated_text"]

    print("RAW MODEL OUTPUT:\n", response)
    print("-" * 60)

    return clean_code(response)
