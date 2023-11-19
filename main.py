import fitz
import os
import ocrmypdf
import scipdf
from PIL import Image, ImageOps
import cv2
import matplotlib.pyplot as plt
import numpy as np
import data_processing.data_processing as dp

PDFS_PATH = "pdfs"
SCANNED_PDFS_PATH = "scanned_pdfs"
OCR_PDFS_PATH = "ocr_pdfs"
OUT_PATH = "out"
OUT_FIGURES_PATH = f"{OUT_PATH}/figures"
PROCESSED_FIGURES_PATH = f"{OUT_PATH}/processed_figures"


# Converts normal pdf to "scanned" pdf (each page is an image)
def pdf_to_scanned_pdf(pdf_path, converted_pdf_path, dpi):
    pdf_document = fitz.open(pdf_path)
    pdf_writer = fitz.open()

    for page_number in range(pdf_document.page_count):
        page = pdf_document[page_number]
        image = page.get_pixmap(matrix=fitz.Matrix(dpi / 72.0, dpi / 72.0))

        pdf_page = pdf_writer.new_page(width=page.rect.width, height=page.rect.height)
        pdf_page.insert_image(rect=page.rect, pixmap=image)

    pdf_writer.save(converted_pdf_path)
    pdf_writer.close()

    pdf_document.close()


# Create "scanned" pdfs from pdfs with metadata
def create_scanned_pdfs(input_path, scanned_pdf_path, dpi=200):
    if os.path.isdir(input_path):
        for file in os.listdir(input_path):
            if file.endswith(".pdf"):
                if not os.path.exists(f"{scanned_pdf_path}/{file}"):
                    print(f"Creating scanned pdf from {file}")
                    pdf_to_scanned_pdf(
                        f"{input_path}/{file}", f"{scanned_pdf_path}/{file}", dpi
                    )


# Run OCR on scanned pdfs in a folder
def ocr_scanned_pdfs(scanned_pdf_path, ocr_pdf_path):
    if os.path.isdir(scanned_pdf_path):
        for file in os.listdir(scanned_pdf_path):
            if file.endswith(".pdf"):
                if not os.path.exists(f"{ocr_pdf_path}/{file}"):
                    print(f"Running OCR on {file}")
                    ocrmypdf.ocr(f"{scanned_pdf_path}/{file}", f"{ocr_pdf_path}/{file}")


# Creates paths if they don't exist
def create_paths(paths):
    for path in paths:
        if not os.path.exists(path):
            os.makedirs(path)


# Detects images and tables in pdfs if results don't exist
def detect(input_path, output_path):
    if not os.path.isdir(input_path):
        os.mkdir(input_path)

    for file in os.listdir(input_path):
        if file.endswith(".pdf"):
            figures = os.listdir(OUT_FIGURES_PATH)
            figures = [fig.split("-")[0] for fig in figures]
            if file.split(".")[0] not in figures:
                print(f"Detecting graphic elements in {file}")
                scipdf.parse_figures(f"{input_path}/{file}", output_folder=output_path)
            else:
                print(f"Graphic elements already detected in {file}")


def process_figures(input_path, output_path, padding, max_cropped_bottom):
    if not os.path.isdir(input_path):
        print("Input path is not a directory. Returning.")
        return

    if not os.path.exists(output_path):
        os.mkdir(output_path)

    for file in os.listdir(input_path):
        if file.endswith(".png"):
            if not os.path.exists(f"{output_path}/{file}"):
                print(f"Processing {file}")
                dp.crop_and_save(
                    f"{input_path}/{file}",
                    f"{output_path}/{file}",
                    padding=padding,
                    max_cropped_bottom=max_cropped_bottom,
                )


# import scipdf

# # article_dict = scipdf.parse_pdf_to_dict("scanned_pdfs/test2.pdf")
# # print(article_dict)

# # xml = scipdf.parse_pdf("scabbed_pdfs/test2.pdf", soup=True)
# # print(xml.prettify())

if __name__ == "__main__":
    create_paths(
        [PDFS_PATH, SCANNED_PDFS_PATH, OCR_PDFS_PATH, OUT_PATH, OUT_FIGURES_PATH]
    )

    create_scanned_pdfs(PDFS_PATH, SCANNED_PDFS_PATH, dpi=200)

    ocr_scanned_pdfs(SCANNED_PDFS_PATH, OCR_PDFS_PATH)

    detect(OCR_PDFS_PATH, OUT_PATH)

    process_figures(
        OUT_FIGURES_PATH,
        PROCESSED_FIGURES_PATH,
        padding=10,
        max_cropped_bottom=0.1,
    )
