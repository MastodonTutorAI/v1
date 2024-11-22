import fitz  # PyMuPDF for PDF processing
from pdf2image import convert_from_bytes
from PIL import Image
import io
import easyocr
import numpy as np
import ssl
from pptx import Presentation
import Document
from multiprocessing import Pool, cpu_count

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
        elif file_type == "text/plain":
            return extract_text_from_text(file)
        elif file_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            return extract_text_from_doc(file)
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
                        continue        #Ignoring empty images , no need for raising error

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
    try:
        prs = Presentation(file)
    except Exception as e:
        raise RuntimeError(f"Error processing PPTX file:{e}")

    slides = list(enumerate(prs.slides))
    with Pool(cpu_count()) as pool:
        results = pool.map(process_slide, slides)

    for slide_processed in results:
      text_content.append(slide_processed)

    return text_content

def process_slide(slide_data):
    slide_num, slide = slide_data
    slide_content = []
    try:
      for shape in slide.shapes:
          if hasattr(shape, "text_frame") and shape.text_frame:
              for paragraph in shape.text_frame.paragraphs:
                  for run in paragraph.runs:
                      slide_content.append(run.text)

          if shape.shape_type == 13:  #Check if the shape is an image
              try:
                  image_bytes = shape.image_blob
                  image = Image.open(io.BytesIO(image_bytes))
                  image_np_array = np.array(image)

                  if image_np_array.size > 0:
                    ocr_response = reader.readtext(image_np_array)
                    for img in ocr_response:
                      slide_content.append(img[1])
              except Exception as e:
                  print(f"Error processing image on slide {slide_num + 1}: {e}")
    except Exception as e:
        print(f"Error occurred while processing slide {slide_num + 1}: {e}")
        raise RuntimeError(f"Error occurred while extracting text from image on slide {slide_num + 1}: {e}")
    return slide_content 

def extract_text_from_doc(file):
    """Extracts text form an uploaded document file. """
    text_content = []
    try:
        doc=Document(file)
        for para in doc.paragraphs:
            text_content.append(para.text)

        for table in doc.tables:
            for row in table.rows:
                for col in row.cells:
                    text_content.append(col.text)

        for i in doc.part.rels.values():
            if i.reltype == 13:
                image_data=doc.part.get_blob(i.target)
                image=Image.open(io.BytesIO(image_data))
                image_np_array = np.array(image)

                if image_np_array.size == 0:
                    continue        #Ignoring empty images , no need for raising error

                ocr_response = reader.readtext(image_np_array)
                text_extracted = "\n".join([i[1] for i in ocr_response])
                text_content.append(text_extracted)
    except Exception as e:
        raise RuntimeError(f"Error processing text file: {e}")

    return text_content

def extract_text_from_text(file):
    """Extracts text from an uploaded text file."""
    text_content = []
    try:
        text_content=file.read().decode('utf-8')
    except Exception as e:
        raise RuntimeError(f"Error processing text file: {e}")

    return text_content