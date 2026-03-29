import os
import json
import re
import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv

# شحن مفاتيح البيئة
load_dotenv()

# إعدادات الصفحة الأساسية
st.set_page_config(
    page_title="AI Data Extractor", 
    page_icon="🪄", 
    layout="wide"
)

# ------------------- CSS متطور لتجميل الواجهة بالكامل -------------------
st.markdown("""
    <style>
    /* خلفية متدرجة فخمة */
    .stApp {
        background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
        color: #ffffff;
    }

    /* تأثير الزجاج للحاويات */
    div[data-testid="stVerticalBlock"] > div:has(div.stTextArea) {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        padding: 25px;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }

    /* تنسيق العنوان الرئيسي */
    .main-title {
        font-size: 3.5rem !important;
        font-weight: 800 !important;
        background: -webkit-linear-gradient(45deg, #f3a712, #e43f5a);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 5px;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }

    /* نصوص الوصف */
    .sub-text {
        color: #b0b3b8;
        text-align: center;
        font-size: 1.2rem;
        margin-bottom: 30px;
    }

    /* منطقة النص (Text Area) */
    .stTextArea textarea {
        background-color: rgba(10, 10, 30, 0.7) !important;
        color: #00ffcc !important;
        border: 1px solid #444 !important;
        border-radius: 15px !important;
        font-size: 16px !important;
        line-height: 1.6;
    }

    /* زرار الإرسال المودرن */
    .stButton > button {
        width: 100%;
        background: linear-gradient(90deg, #e43f5a 0%, #ff6b6b 100%);
        color: white !important;
        border: none !important;
        padding: 15px 0px;
        border-radius: 12px;
        font-weight: bold;
        font-size: 20px;
        transition: all 0.4s ease;
        box-shadow: 0 4px 15px rgba(228, 63, 90, 0.3);
        margin-top: 10px;
    }

    .stButton > button:hover {
        transform: scale(1.02);
        box-shadow: 0 8px 25px rgba(228, 63, 90, 0.5);
        color: white !important;
    }

    /* تحسين شكل الـ JSON والنتائج */
    .stJson {
        background-color: rgba(0, 0, 0, 0.3) !important;
        border-radius: 10px;
        padding: 10px;
    }
    
    hr {
        border-top: 1px solid rgba(255,255,255,0.1);
        margin: 2rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# ------------------- واجهة المستخدم (UI) -------------------
st.markdown('<h1 class="main-title">AI Data Extractor</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-text">Turn messy text into structured JSON in seconds ⚡</p>', unsafe_allow_html=True)

st.markdown("---")

# تقسيم الصفحة لعمودين
col1, col2 = st.columns([1.2, 1], gap="large")

with col1:
    st.markdown("### 📝 Input Data")
    user_input = st.text_area(
        "What text should I analyze?", 
        height=400, 
        placeholder="Paste receipts, logs, profiles, or any unstructured text here..."
    )
    send_btn = st.button('🚀 Extract Structure')

# ------------------- OpenAI Client (Groq) -------------------
# تأكد أن GROQ_API_KEY موجود في ملف .env
client = OpenAI(
    api_key=os.environ.get("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1",
)

system_instruction = """
You are a data extraction expert. 
Return ONLY valid JSON.
No talk, no markdown (no ```json blocks), no explanation.
If a value is missing, use null.
"""

def extract_json_safe(text):
    try:
        # تنظيف النص من أي علامات Markdown لو الموديل أضافها بالخطأ
        clean_text = re.sub(r'```json|```', '', text).strip()
        return json.loads(clean_text)
    except:
        # محاولة البحث عن أي شيء بين الأقواس { }
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except:
                return None
        return None

# ------------------- منطق المعالجة -------------------
with col2:
    st.markdown("### ✨ Structured Result")
    if send_btn:
        if user_input:
            with st.spinner('Thinking...'):
                try:
                    # تم استخدام الموديل الأحدث llama-3.3-70b-versatile
                    response = client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=[
                            {"role": "system", "content": system_instruction},
                            {"role": "user", "content": user_input}
                        ],
                        temperature=0.1
                    )

                    raw_content = response.choices[0].message.content
                    parsed_json = extract_json_safe(raw_content)

                    if parsed_json:
                        st.success("Data parsed successfully!")
                        st.json(parsed_json)
                        # إضافة زر لتحميل النتيجة كملف JSON
                        json_str = json.dumps(parsed_json, indent=4)
                        st.download_button(
                            label="📥 Download JSON",
                            data=json_str,
                            file_name="extracted_data.json",
                            mime="application/json"
                        )
                    else:
                        st.error("I got the data but couldn't format it as clean JSON.")
                        with st.expander("Show raw response"):
                            st.code(raw_content)
                except Exception as e:
                    st.error(f"Error communicating with AI: {e}")
        else:
            st.info("Waiting for your input in the left panel... 👈")
    else:
        st.info("Results will appear here once you click 'Extract Structure'")