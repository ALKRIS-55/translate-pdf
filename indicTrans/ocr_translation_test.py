import easyocr
import fitz
from PIL import Image
from inference.engine import Model
import fasttext
import os
import fitz
import textwrap
from pdf2image import convert_from_path


detection_model = '../lid.176.bin'
translation_model = Model(expdir='../indic-en')

def detect_language(text):
    model = fasttext.load_model(detection_model)
    LANG = model.predict(text)
    language = LANG[0][0].split("__label__")[1]
    return language

def translate_text(text, source_language):
    translation = translation_model.translate_paragraph(text, source_language,'en')
    return translation


def pdf_to_images(pdf_path, image_folder, vernacular_pages):
    # Create the image folder if it doesn't exist
    os.makedirs(image_folder, exist_ok=True)

    images = convert_from_path(pdf_path, fmt='png', dpi=300)

    for i, image in enumerate(images, start=1):
        if i in vernacular_pages:
            image_path = f"{image_folder}/page_{i}.png"
            image.save(image_path, "PNG")
        

def process_pdf(input_pdf_path, output_pdf_path, vernacular_pages, image_folder):
    reader = easyocr.Reader(['hi', 'en'])
    # Open the input PDF
    input_pdf = fitz.open(input_pdf_path)
    number_of_pages = input_pdf.page_count
    # Create a new PDF
    output_pdf = fitz.open()
    # Convert pdf pages into high definition image
    pdf_to_images(input_pdf_path, image_folder, vernacular_pages)

    try:
        for page_num in range(number_of_pages):
            if page_num + 1 in vernacular_pages:
                txt = reader.readtext(f'{image_folder}/page_{page_num + 1}.png', detail=0)
                paragraph = " ".join(txt)
                # print(paragraph)
                # Translate it into English
                translation = translate_text(paragraph, 'hi')
                # print(translation)
                # Add a new page with a paragraph
                print(translation)
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
        output_pdf.save(output_pdf_path)
        output_pdf.close()
        for i in vernacular_pages:
            image_path = f"{image_folder}/page_{i}.png"
            if os.path.exists(image_path):
                os.remove(image_path)


if __name__ == "__main__":
    input_pdf_path = "/home/ubuntu/Translation/indicTrans/sampl.pdf"  # Replace with the actual path to your input PDF file
    output_pdf_path = "/home/ubuntu/Translation//indicTrans/output.pdf"  # Replace with the desired output path
    image_folder = "/home/ubuntu/Translation/indicTrans/images"
    vernacular_pages = [2]

    process_pdf(input_pdf_path, output_pdf_path, vernacular_pages, image_folder)
    print(f"Translated PDF saved to: {output_pdf_path}")
    
