import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

def generate_report(chunks):

    combined_text = "\n\n".join(chunks[:8])

    prompt = f"""
    You are REMA, an AI research assistant.

    Analyze the following research material and generate:
    - key insights
    - summary
    - important findings
    - contradictions if any
    - startup/founder insights

    Research Material:
    {combined_text}
    """

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.3,
    )

    return response.choices[0].message.content