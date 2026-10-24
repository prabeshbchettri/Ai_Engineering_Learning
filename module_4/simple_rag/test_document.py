from pathlib import Path
import requests
import time

document = Path("data/college_rules.txt").read_text(encoding="utf-8")

question = "How many marks are allocated to internal assessment?"

prompt = f"""
Answer the question using the document below.

Document:
{document}

Question: {question}
Answer:
"""

start = time.time()

response = requests.post(
    "http://localhost:11434/api/generate",
    json={
        "model": "qwen2.5:3b",
        "prompt": prompt,
        "stream": False
    },
    timeout=300
)

response.raise_for_status()
result = response.json()

print("Answer:", result["response"])
print("Elapsed seconds:", round(time.time() - start, 2))
print("Prompt tokens:", result.get("prompt_eval_count"))
print("Output tokens:", result.get("eval_count"))