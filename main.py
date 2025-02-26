from dotenv import load_dotenv
load_dotenv()

import streamlit as st
import os
import base64
import io
from PIL import Image
import pdf2image
import google.generativeai as genai

# Place st.set_page_config() at the very top
st.set_page_config(page_title="AI-Powered-Resume-Analyser")

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# ... (rest of your code, including functions and Streamlit elements)
def get_gemini_response(input_text, pdf_content, prompt, chat_history=None):
    """
    Generates a response from the Gemini Pro Vision model, considering chat history.
    """
    model = genai.GenerativeModel('gemini-1.5-flash')
    messages = []
    if chat_history:
        messages.extend(chat_history)
    messages.extend([input_text, pdf_content, prompt])
    response = model.generate_content(messages)
    return response.text

def input_pdf_setup(uploaded_file):
    """
    Converts a PDF file to a base64 encoded JPEG image.
    """
    if uploaded_file is not None:
        images = pdf2image.convert_from_bytes(uploaded_file.read())
        first_page = images[0]
        img_byte_arr = io.BytesIO()
        first_page.save(img_byte_arr, format='JPEG')
        img_byte_arr = img_byte_arr.getvalue()
        pdf_parts = [
            {
                "mime_type": "image/jpeg",
                "data": base64.b64encode(img_byte_arr).decode()
            }
        ]
        return pdf_parts
    else:
        raise FileNotFoundError("File not uploaded")

# Streamlit App
st.header("ATS Tracking System")

if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

input_text = st.text_area("Job Description: ", key="input")
uploaded_file = st.file_uploader("Upload Resume(PDF)", type=["pdf"])

if uploaded_file is not None:
    st.write("Resume Uploaded Successfully")

submit1 = st.button("Analyse my Resume")
submit2 = st.button("Skill Gap Analysis")
submit3 = st.button("Interview Preparation Insights")

input_prompt1 = """
You are an experienced HR with Tech Experience in the field of any one job role from Data Science, Full Stack web-development,Big Data
Engineering, DevOps, Data Analyst. Your task is to review the provided resume against the job description for these profiles.
Please share your professional evaluation on wether the candidate's profile aligns with the role.
Highlight the strengths and weaknesses of the applicant in relation to the specified job role
"""

input_prompt3 = """
You are an skilled ATS (Applicant Tracking System) scanner with a deep understanding in any one job role  of Data Science, Full Stack web-development,Big Data
Engineering, DevOps, Data Analyst.Your task is to review the provided resume against the job description for these profiles.
your task is to evaluate the resume against the provided job description. give me the percentage of match if the resume matches
the job description. First the output should come as percentage and then keywords missing and last final thoughts.
"""

if submit1:
    if uploaded_file is not None:
        pdf_content = input_pdf_setup(uploaded_file)
        response = get_gemini_response(input_text, pdf_content, input_prompt1)
        st.subheader("The response is:")
        st.write(response)
    else:
        st.write("Please upload a file")
elif submit2:
    if uploaded_file is not None:
        pdf_content = input_pdf_setup(uploaded_file)
        response = get_gemini_response(input_text, pdf_content, input_prompt1)
        st.subheader("The response is:")
        st.write(response)
    else:
        st.write("Please upload a file")
elif submit3:
    if uploaded_file is not None:
        pdf_content = input_pdf_setup(uploaded_file)
        response = get_gemini_response(input_text, pdf_content, input_prompt3)
        st.subheader("The response is:")
        st.write(response)
    else:
        st.write("Please upload a file")

# Chatbot Interface
st.subheader("Chat with the Resume Analyzer")
user_message = st.text_input("Your message:", key="chat_input")
send_button = st.button("Send")

if send_button:
    if uploaded_file is not None:
        pdf_content = input_pdf_setup(uploaded_file)
        user_input = user_message
        st.session_state.chat_history.append({"role": "user", "parts": [user_input]})
        response = get_gemini_response(user_input, pdf_content, "Continue the conversation.", st.session_state.chat_history)
        st.session_state.chat_history.append({"role": "model", "parts": [response]})
        # Correctly append image data
        st.session_state.chat_history.append({"role": "image", "parts": pdf_content})

        for message in st.session_state.chat_history:
            if message['role'] == 'user':
                st.write(f"**You:** {message['parts']}")
            elif message['role'] == 'model':
                st.write(f"**Bot:** {message['parts']}")
            elif message['role'] == 'image':
                # you can add a display of the image here
                pass
    else:
        st.write("Please upload a file first.")