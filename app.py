import os
import json
import re
import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

st.header('Chatbot to reverse unstructured data to a dictionary format')
user_input = st.text_area('Enter your unstructured data')

client = OpenAI(
    api_key=os.environ.get("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1",
)

system_instruction = """
Return ONLY valid JSON.
No explanation.
"""

def extract_json(text):
    try:
        # استخراج أول JSON من النص
        json_match = re.search(r'\{.*\}', text, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
    except:
        return None

if st.button('Send'):
    if user_input:
        response = client.responses.create(
            model="openai/gpt-oss-20b",
            input=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": user_input}
            ]
        )

        raw_text = response.output[0].content[0].text

        st.subheader("Result:")

        parsed = extract_json(raw_text)

        if parsed:
            st.json(parsed)
        else:
            st.error("⚠️ Failed to extract JSON")
            st.write(raw_text)

    else:
        st.warning("Please enter data first!")