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
    "temperature": 0,
    "top_p": 0.1,
    "top_k": 1,
    "max_output_tokens": 8192,
}

# Load the Gemini Pro Vision Model
model = genai.GenerativeModel(model_name="gemini-1.5-pro-latest",
                              generation_config=generation_config)


def get_gemini_respone(input_prompt, images):
    content = [input_prompt] + images
    response = model.generate_content(
        content, request_options={"timeout": 1000})
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
You are an expert in processing invoices and extracting relevant data from them. 
Your task is to extract the line items from the provided invoice(s) in the following tabular format:

Invoice Number: [Invoice Number]
| Object Description | Malaysia HS Code | Component Quantity | Price MYR |
|---------------------|-------------------|---------------------|------------|
| [Description]       | [HS Code]         | [Quantity]          | [Price]    |
| ...                 | ...               | ...                 | ...        |

Please note the following:

1. Do not include any HTML tags in the output.
2. The invoice may contain multiple pages, and some cells may be empty. Handle these cases accordingly.
3. If multiple invoices are present in the PDF, separate the output for each invoice with the respective invoice number.
4. Preserve the order of the line items as they appear in the invoice.
5. If a cell contains multiple lines of text, append them together without any line break characters.

The fields to extract are:

- Object Description
- Malaysia HS Code
- Component Quantity
- Price MYR

Ensure that the extracted data is accurate and aligned correctly in the tabular format.
"""
user_input_prompt = st.text_area(
    "User Input Prompt", key="input", value=default_input_prompt.strip(), height=160)
upload_file = st.file_uploader(
    "Upload a PDF", type=["PDF"])
if upload_file is not None:
    images = get_images_from_pdf(upload_file)
    for i, image in enumerate(images):
        st.image(image["data"], caption=f"Page {i+1}")

submit = st.button("Extract!")
if submit:
    if upload_file is None:
        st.error("Please upload a PDF with images.")
        st.stop()
    else:
        response = get_gemini_respone(user_input_prompt, images)
        st.subheader("Response")
        st.write(response)
