from dotenv import load_dotenv
load_dotenv()

import streamlit as st
import os
import base64
import io
import pdf2image
import google.generativeai as genai

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def get_gemini_response(input_text, pdf_content, prompt):
    """
    Generates a response from the Gemini Pro Vision model.

    Args:
        input_text (str): The job description or other input text.
        pdf_content (list): List containing the processed PDF image data.
        prompt (str): The prompt for the model.

    Returns:
        str: The generated text response.
    """
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    # Check if pdf_content is empty and handle accordingly
    if pdf_content:
        response = model.generate_content([input_text, pdf_content[0], prompt])
    else:
        response = model.generate_content([input_text, "", prompt])  # Pass an empty string if no PDF content
    
    return response.text

def input_pdf_setup(uploaded_file):
    """
    Converts a PDF file to a base64 encoded JPEG image.

    Args:
        uploaded_file (streamlit.UploadedFile): The uploaded PDF file.

    Returns:
        list: A list containing a dictionary with the image data.
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
st.set_page_config(page_title="AI-Powered-Resume-Analyser")
st.header("ATS Tracking System")

# Resume Analysis Section
uploaded_file = st.file_uploader("Upload Resume(PDF)", type=["pdf"])

if uploaded_file is not None:
    st.write("Resume Uploaded Successfully")

input_text = st.text_area("Job Description: ", key="input")

submit1 = st.button("Analyse my Resume")
submit2 = st.button("Skill Gap Analysis")
submit3 = st.button("Interview Preparation Insights")


input_prompt1 = """
You are an experienced HR with Tech Experience in the field of any one job role from Data Science, Full Stack web-development, Big Data
Engineering, DevOps, Data Analyst. Your task is to review the provided resume against the job description for these profiles.
Please share your professional evaluation on whether the candidate's profile aligns with the role.
Highlight the strengths and weaknesses of the applicant in relation to the specified job role.
"""

input_prompt3 = """
You are a skilled ATS (Applicant Tracking System) scanner with a deep understanding in any one job role of Data Science, Full Stack web-development, Big Data
Engineering, DevOps, Data Analyst. Your task is to review the provided resume against the job description for these profiles.
Your task is to evaluate the resume against the provided job description. Give me the percentage of match if the resume matches
the job description. First the output should come as percentage and then keywords missing and last final thoughts.
"""

if submit1:
    if uploaded_file is not None:
        pdf_content = input_pdf_setup(uploaded_file)
        response = get_gemini_response(input_text, pdf_content, input_prompt3)
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

# Chatbot Section
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

st.subheader("Chat with the AI")
user_input = st.text_input("You: ", key="chat_input")

if st.button("Send"):
    if user_input:
        # Append user input to chat history
        st.session_state.chat_history.append({"role": "user", "content": user_input})
    
        # Check if a resume is uploaded
        if uploaded_file is not None:
            pdf_content = input_pdf_setup(uploaded_file) 
            response = get_gemini_response(user_input, pdf_content, "")  # Pass the pdf_content
        else:
            response = "Please upload a resume to analyze."  # Handle case where no resume is uploaded
    
        st.session_state.chat_history.append({"role": "ai", "content": response})

# Display chat history
for chat in st.session_state.chat_history:
    if chat['role'] == 'user':
        st.write(f"You: {chat['content']}")
    else:
        st.write(f"AI: {chat['content']}")
