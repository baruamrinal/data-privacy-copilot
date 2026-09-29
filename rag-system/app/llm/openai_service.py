from openai import OpenAI
import os

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)


def generate_compliance_answer(
    question: str,
    retrieved_chunks: list
):

    context = "\n\n".join([
        f"Clause {idx+1}:\n{chunk['text']}"
        for idx, chunk in enumerate(retrieved_chunks)
    ])

    prompt = f"""
You are an enterprise AI Privacy and Compliance Copilot.

Answer the user's question ONLY using the retrieved clauses below.

If the answer is not clearly stated, say:
"The document does not explicitly specify this."

Question:
{question}

Retrieved Clauses:
{context}

Instructions:
- Be precise
- Be legally cautious
- Do not hallucinate
- Cite clause numbers when possible
- Explain reasoning briefly
"""

    response = client.chat.completions.create(
        model="gpt-4.1",
        messages=[
            {
                "role": "system",
                "content": "You are a legal compliance AI assistant."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.1
    )

    return response.choices[0].message.content