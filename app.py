import os
import base64
import io
import streamlit as st
from dotenv import load_dotenv
from PIL import Image
import pdf2image
import google.generativeai as genai

# Load environment variables
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Function to get response from Gemini Pro Vision model
def get_gemini_response(input_text, pdf_content, prompt):
    model = genai.GenerativeModel('gemini-1.5-flash')  # Use 'gemini-1.5-flash' or 'gemini-pro-vision' based on availability
    response = model.generate_content([input_text, pdf_content[0], prompt])
    return response.text

# Function to prepare PDF input (convert first page to image)
def input_pdf_setup(uploaded_file):
    if uploaded_file is not None:
        # Convert PDF to image
        images = pdf2image.convert_from_bytes(uploaded_file.read())
        first_page = images[0]
        # Convert to bytes
        img_byte_arr = io.BytesIO()
        first_page.save(img_byte_arr, format='JPEG')
        img_byte_arr = img_byte_arr.getvalue()
        # Encode to base64
        pdf_parts = [
            {
                "mime_type": "image/jpeg",
                "data": base64.b64encode(img_byte_arr).decode()
            }
        ]
        return pdf_parts
    else:
        raise FileNotFoundError("No file uploaded")

# Streamlit app configuration
st.set_page_config(page_title="Simple ATS Scanner", layout="wide")
st.header("Applicant Tracking System (ATS) Scanner")

# Input fields
job_description = st.text_area("Job Description:", height=150)
uploaded_resume = st.file_uploader("Upload Resume (PDF only):", type=["pdf"])

if uploaded_resume is not None:
    st.success("Resume uploaded successfully!")

# Buttons for actions
button_review = st.button("Review Resume Against Job")
button_match = st.button("Calculate Match Percentage")

# Prompts for Gemini
prompt_review = """
You are an experienced HR Manager with expertise in applicant tracking. Review the resume against the job description.
Highlight strengths, weaknesses, and provide a professional evaluation of the candidate's fit.
"""
prompt_match = """
You are an ATS scanner with deep knowledge of resume parsing and job matching.
Evaluate the resume against the job description. Output:
1. Percentage match (e.g., 75%).
2. Missing keywords.
3. Final thoughts and improvement suggestions.
"""

# Handle button clicks
if button_review:
    if uploaded_resume is not None:
        pdf_content = input_pdf_setup(uploaded_resume)
        response = get_gemini_response(job_description, pdf_content, prompt_review)
        st.subheader("Resume Review:")
        st.write(response)
    else:
        st.error("Please upload a resume.")

if button_match:
    if uploaded_resume is not None:
        pdf_content = input_pdf_setup(uploaded_resume)
        response = get_gemini_response(job_description, pdf_content, prompt_match)
        st.subheader("Match Analysis:")
        st.write(response)
    else:
        st.error("Please upload a resume.")