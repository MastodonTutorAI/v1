
import fitz  # PyMuPDF for PDF processing
from pdf2image import convert_from_bytes
from PIL import Image
import io
import easyocr
import numpy as np
import ssl

# Create an unverified SSL context
ssl._create_default_https_context = ssl._create_unverified_context

# Initialize EasyOCR reader (English as the language)
reader = easyocr.Reader(['en'])


def extract_text_and_images(file):
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
