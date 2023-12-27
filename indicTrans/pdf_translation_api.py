from fastapi import FastAPI, File, UploadFile, Response, HTTPException, Form
from pydantic import BaseModel
from pdf2image import convert_from_path
import easyocr
import fitz
import httpx
import fasttext
from inference.engine import Model
from PIL import Image
import io
import os
import textwrap


app = FastAPI()
 
# Language Dictionary
indic_language_dict = {
    'assamese': 'as',
    'hindi': 'hi',
    'marathi': 'mr',
    'tamil': 'ta',
    'bengali': 'bn',
    'kannada': 'kn',
    'oriya': 'or',
    'telugu': 'te',
    'gujarati': 'gu',
    'malayalam': 'ml',
    'punjabi': 'pa',
    'english': 'en',
}

translation_model = Model(expdir='../indic-en')

def translate_text(text, source_language):
    translation = translation_model.translate_paragraph(text, source_language, 'en')
    return f"Translated: {translation}"

def convert_to_int_list(input_string):
    return [int(x) for x in input_string.split(",") if x.isdigit()]

def pdf_to_images(pdf_path, image_folder, vernacular_pages):
    # Create the image folder if it doesn't exist
    os.makedirs(image_folder, exist_ok=True)

    images = convert_from_path(pdf_path, fmt='png', dpi=300)

    for i, image in enumerate(images, start=1):
        if i in vernacular_pages:
            image_path = f"{image_folder}/page_{i}.png"
            image.save(image_path, "PNG")

@app.post("/translate_pdf")
async def translate_pdf(file: UploadFile = File(...), vernacular_pages_num: str = Form(...), language: str = Form(...)):
    input_pdf_path = f"/tmp/{file.filename}"
    image_folder = "/tmp/images"
    
    with open(input_pdf_path, "wb") as pdf_file:
        pdf_file.write(file.file.read())
    
    vernacular_pages = convert_to_int_list(vernacular_pages_num)
    lang = indic_language_dict[language.lower()]
    
    reader = easyocr.Reader([lang, 'en'])
    
    # Open the input PDF
    input_pdf = fitz.open(input_pdf_path)
    number_of_pages = input_pdf.page_count

    # Create a new PDF
    output_pdf = fitz.open()
    # Convert pdf pages into high definition images
    pdf_to_images(input_pdf_path, image_folder, vernacular_pages)

    try:
        for page_num in range(number_of_pages):
            if page_num + 1 in vernacular_pages:
                txt = reader.readtext(f'{image_folder}/page_{page_num + 1}.png', detail=0)
                paragraph = " ".join(txt)
                
                # Translate it into English
                translation = translate_text(paragraph, lang)
                
                # Add a new page with a paragraph
                new_page = output_pdf.new_page()
                # Specify the starting position for the text
                x, y = 50, 50
                # Wrap the input paragraph into multiple lines
                wrapped_paragraphs = textwrap.wrap(translation, width=100)  # Adjust the width as needed

                # Write each wrapped line on a new line
                for wrapped_line in wrapped_paragraphs:
                    new_page.insert_text((x, y), wrapped_line)
                    y += 20  # Adjust the vertical position for the next line
            else:
                output_pdf.insert_pdf(input_pdf, from_page=page_num, to_page=page_num)

    finally:
        # Close the PDF files
        input_pdf.close()

        # Save the translated PDF content to a BytesIO object
        pdf_content = io.BytesIO()
        output_pdf.save(pdf_content)
        output_pdf.close()

        # Clean up: remove temporary image files
        for i in vernacular_pages:
            image_path = f"{image_folder}/page_{i}.png"
            if os.path.exists(image_path):
                os.remove(image_path)

    # Set response headers for file download
    response = Response(content=pdf_content.getvalue())
    response.headers["Content-Disposition"] = "attachment; filename=translated_pdf.pdf"
    response.headers["Content-Type"] = "application/pdf"

    return response
