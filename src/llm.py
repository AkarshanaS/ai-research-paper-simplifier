from dotenv import load_dotenv
import os
import streamlit as st
from openai import OpenAI
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY") or st.secrets["OPENAI_API_KEY"]
client = OpenAI(api_key=api_key)

def build_prompt(query, context_chunks):
    context = "\n\n".join(context_chunks)
    prompt = f"""
You are an AI assistant that simplifies research papers.

Rules:
-Use ONLY the provided context to answer the question.
-If the answer is not in the context, say you don't know.
-Explain complex terms in simple language.
-Use bullet points for lists and key information.

Context:{context}\n\nQuestion: {query}\nAnswer:"""
    return prompt

def generate_answer(query, context_chunks):
    prompt = build_prompt(query, context_chunks)
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "system", "content": "You simplify research papers."},
                  {"role": "user", "content": prompt}],
        temperature=0.3
    )
    return response.choices[0].message.content.strip()