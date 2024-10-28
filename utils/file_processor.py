import fitz  # PyMuPDF for PDF processing
from pdf2image import convert_from_bytes
from PIL import Image
import io
import easyocr
import numpy as np
import ssl
from pptx import Presentation

# Create an unverified SSL context
ssl._create_default_https_context = ssl._create_unverified_context

# Initialize EasyOCR reader (English as the language)
reader = easyocr.Reader(['en'])

def extract_text_and_images(file_type,file):
    """Extracts text and images from an uploaded file."""
    try:
        if file_type == "application/pdf":
            return extract_text_from_pdf(file)
        elif file_type == "application/vnd.openxmlformats-officedocument.presentationml.presentation":
            return extract_text_from_ppt(file)
    except Exception as e:
        print(f"Error processing file: {e}")
        raise RuntimeError(f"Failed to process file: {e}")

#KANISHK'S CODE    
def extract_text_from_pdf(file):
    """Extracts text and images from an uploaded PDF using EasyOCR."""
    text_content = []

    # Open the PDF from the uploaded file-like object
    with fitz.open(stream=file.read(), filetype="pdf") as pdf:
        for page_num in range(pdf.page_count):
            page = pdf.load_page(page_num)

            # Extract text from the PDF page
            text = page.get_text()
            text_content.append(text)

            # Extract images from the PDF page
            for img_index, img in enumerate(page.get_images(full=True)):
                xref = img[0]
                base_image = pdf.extract_image(xref)
                image_bytes = base_image["image"]

                # Convert image bytes to a PIL Image and validate
                try:
                    image = Image.open(io.BytesIO(image_bytes))
                    image_np = np.array(image)  # Convert to numpy array

                    # Ensure the image is valid (non-empty)
                    if image_np.size == 0:
                        raise ValueError("Empty image data encountered.")

                    # Apply OCR on the image using EasyOCR
                    ocr_results = reader.readtext(image_np)

                    # Collect OCR results
                    extracted_text = "\n".join([res[1] for res in ocr_results])
                    text_content.append(extracted_text)

                except Exception as e:
                    print(f"Error processing image on page {page_num}: {e}")
                    text_content.append(
                        f"[Error processing image on page {page_num}]")

    return text_content

#ALISHA'S CODE
def extract_text_from_ppt(file):
    """Extracts text from an uploaded PPTX file."""
    text_content = []
    #Loading the presentation file
    try:
        prs = Presentation(file)
    except Exception as e:
        raise RuntimeError(f"Error processing PPTX file: {e}")
    
    #Looping through all slides to extract text from each slide
    for slide_num,slide in enumerate(prs.slides):
        
        for shape in slide.shapes:
            
            #Extracting text from text frames if present
            if hasattr(shape, "text_frame") and shape.text_frame:
                for paragraph in shape.text_frame.paragraphs:
                    for run in paragraph.runs:
                        text_content.append(run.text)
            
            #Extracting text from images if present
            #Checking if the shape is an image
            if shape.shape_type == 13:
                try:
                    image_bytes = shape.image_blob
                    image = Image.open(io.BytesIO(image_bytes))
                    image_np_array = np.array(image)

                    if image_np_array.size == 0:
                        raise ValueError("Empty image found.")
                    
                    ocr_response = reader.readtext(image_np_array)
                    text_extracted = "\n".join([i[1] for i in ocr_response])
                    text_content.append(text_extracted)
                except Exception as e:
                    print(f"Error occured while extracting text from image on slide {slide_num+1}: {e}")
                    raise RuntimeError(f"Error occured while extracting text from image on slide {slide_num+1}: {e}")

    # #Removing duplicates
    # text_content = list(dict.fromkeys(text_content)) 
    return text_content


