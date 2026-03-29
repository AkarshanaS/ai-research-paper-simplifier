from dotenv import load_dotenv
import os
import streamlit as st
from openai import OpenAI
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY") or st.secrets["OPENAI_API_KEY"]
client = OpenAI(api_key=api_key)

MODE_INSTRUCTIONS = {
    "Simple": "Explain in very simple terms for a beginner. Avoid jargon.",
    "Normal": "Explain clearly with balanced technical depth.",
    "Technical": "Provide a detailed technical explanation including methods, assumptions, and specifics."
}

def build_prompt(query, context_chunks, mode):
    context = "\n\n".join(context_chunks)
    mode_instruction = MODE_INSTRUCTIONS.get(mode, MODE_INSTRUCTIONS["Normal"])
    prompt = f"""
You are an AI assistant that simplifies research papers.

Style Instruction:
{mode_instruction}

Rules:
-Use ONLY the provided context to answer the question.
-If the answer is not in the context, say you don't know.
-Explain clearly and structure your response
-Use bullet points for lists and key information.


Context:{context}\n\nQuestion: {query}\nAnswer:"""
    return prompt

def generate_answer(query, context_chunks, mode):
    prompt = build_prompt(query, context_chunks, mode)
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "system", "content": "You simplify research papers."},
                  {"role": "user", "content": prompt}],
        temperature=0.3
    )
    return response.choices[0].message.content.strip()