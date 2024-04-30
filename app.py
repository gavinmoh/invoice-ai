# Import All the Required Libraries
import streamlit as st
import google.generativeai as genai
import os
import fitz
from dotenv import load_dotenv
load_dotenv()

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Set up the model
generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 0,
    "max_output_tokens": 8192,
}

# Load the Gemini Pro Vision Model
model = genai.GenerativeModel(model_name="gemini-1.5-pro-latest",
                              generation_config=generation_config)


def get_gemini_respone(input_prompt, images):
    response = model.generate_content(
        [input_prompt] + images)
    return response.text


def get_images_from_pdf(pdf):
    doc = fitz.open(stream=pdf.read(), filetype="pdf")
    images = []
    for page_number in range(len(doc)):
        page = doc[page_number]
        pixmap = page.get_pixmap(dpi=600)
        images.append(
            {
                "data": pixmap.tobytes(),
                "mime_type": "image/png"
            }
        )

    return images


# Initialize the Streamlit App
st.set_page_config(page_title="Invoice AI")
default_input_prompt = """
You are an expert in processing invoices. Your task is to extract the line items from the invoice.
Output the extracted line items in a tabular format. Do not include any HTML tags in the output.
Please beware that the invoice may contain multiple pages and some of the cells may be empty.
Extract the following fields: Object Description, Malaysia HS code, Component quantity, Price MYR
"""
user_input_prompt = st.text_area(
    "User Input Prompt", key="input", value=default_input_prompt.strip(), height=150)
upload_file = st.file_uploader(
    "Upload a PDF", type=["PDF"])
if upload_file is not None:
    images = get_images_from_pdf(upload_file)
    for i, image in enumerate(images):
        st.image(image["data"], caption=f"Page {i+1}")

submit = st.button("Extract!")
if submit:
    response = get_gemini_respone(user_input_prompt, images)
    st.subheader("Response")
    st.write(response)
