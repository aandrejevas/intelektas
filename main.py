import json
import fitz
import os
import ocrmypdf
import scipdf
import data_processing.data_processing as dp
import re
from data_processing.output import OutputXML, process_json_files
from xml.etree.ElementTree import ElementTree

PDFS_PATH = "pdfs"
SCANNED_PDFS_PATH = "scanned_pdfs"
OCR_PDFS_PATH = "ocr_pdfs"
OUT_PATH = "out"
OUT_FIGURES_PATH = f"{OUT_PATH}/figures"
OUT_DATA_PATH = f"{OUT_PATH}/data"
PROCESSED_FIGURES_PATH = f"{OUT_PATH}/processed_figures"
PDFS_WITH_REGIONS = f"region_pdfs"


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
                else:
                    print(f"Scanned pdf already created from {file}")


# Run OCR on scanned pdfs in a folder
def ocr_scanned_pdfs(scanned_pdf_path, ocr_pdf_path):
    if os.path.isdir(scanned_pdf_path):
        for file in os.listdir(scanned_pdf_path):
            if file.endswith(".pdf"):
                if not os.path.exists(f"{ocr_pdf_path}/{file}"):
                    print(f"Running OCR on {file}")
                    ocrmypdf.ocr(f"{scanned_pdf_path}/{file}", f"{ocr_pdf_path}/{file}")
                else:
                    print(f"OCR already run on {file}")


# Creates paths if they don't exist
def create_paths(paths):
    for path in paths:
        if not os.path.exists(path):
            os.makedirs(path)


# Detects images and tables in pdfs if results don't exist
def detect(input_path, output_path):
    if not os.path.isdir(input_path):
        os.mkdir(input_path)

    figures = os.listdir(OUT_FIGURES_PATH)
    # creates a list of unique figure names
    unique_figures = set()
    pattern = r"-(Figure|Table)([IVXLCDM\d]*)-\d+\.png$"
    for file_name in figures:
        match = re.search(pattern, file_name)
        if match:
            # If the pattern is found, remove it and add to the set
            unique_figures.add(re.sub(pattern, "", file_name))

    for file in os.listdir(input_path):
        if file.endswith(".pdf"):
            if file.split(".")[0] not in unique_figures:
                print(f"Detecting graphic elements in {file}")
                scipdf.parse_figures(f"{input_path}/{file}", output_folder=output_path)
            else:
                print(f"Graphic elements already detected in {file}")


# Cuts image from bottom, crops to bounding box, adds padding and saves image
def process_figures(
    figure_path, data_path, output_path, padding, max_crop, ignore_first
):
    if not os.path.exists(output_path):
        os.mkdir(output_path)

    pattern = r"-(Figure|Table)([IVXLCDM\d]*)-\d+\.png$"
    for file in os.listdir(figure_path):
        if file.endswith(".png"):
            pdf_name = re.sub(pattern, "", file)
            if not os.path.exists(f"{output_path}/{file}"):
                print(f"Processing {file}")
                dp.crop_and_save(
                    f"{figure_path}/{file}",
                    f"{data_path}/{pdf_name}.json",
                    f"{output_path}/{file}",
                    padding=padding,
                    max_crop=max_crop,
                    ignore_first=ignore_first,
                )
            else:
                print(f"{file} already processed")


# Draws region boundaries on pdfs
def draw_region_boundaries(pdf_path, xml_path, pdf_out_path):
    if not os.path.exists(pdf_out_path):
        os.mkdir(pdf_out_path)
    if not os.path.exists(pdf_path):
        os.mkdir(pdf_path)
    if not os.path.exists(xml_path):
        os.mkdir(xml_path)

    for file in os.listdir(pdf_path):
        if file.endswith(".pdf"):
            if not os.path.exists(f"{pdf_out_path}/{file}"):
                print(f"Drawing region boundaries on {file}")

                curr_file_path = f"{pdf_path}/{file}"
                curr_xml_path = f"{xml_path}/{file.split('.')[0]}.xml"

                pdf_document = fitz.open(curr_file_path)

                tree = ElementTree()
                tree.parse(curr_xml_path)
                root = tree.getroot()

                for page_element in root.findall(".//element"):
                    page_number = int(
                        page_element.get("source_page")
                    )  # Adjust for zero-based indexing
                    if 0 <= page_number < pdf_document.page_count:
                        page = pdf_document.load_page(page_number - 1)

                        x1 = float(page_element.get("x1"))
                        y1 = float(page_element.get("y1"))
                        x2 = float(page_element.get("x2"))
                        y2 = float(page_element.get("y2"))

                        rect = fitz.Rect(x1, y1, x2, y2)

                        # Determine the type and set the border color accordingly
                        element_type = page_element.get("type", "")
                        if element_type == "t":  # Table
                            annot = page.add_rect_annot(rect)
                            annot.set_colors(colors={"stroke": (0, 0, 1)})
                            annot.update()
                        elif element_type == "f":  # Figure
                            annot = page.add_rect_annot(rect)
                            annot.set_colors(colors={"stroke": (0, 1, 0)})
                            annot.update()

                        # Add label to top-left corner
                        target_name = page_element.get("target_name", "")
                        if target_name:
                            text_length = fitz.get_text_length(
                                target_name, fontname="Times-Roman", fontsize=8
                            )
                            text_rect = fitz.Rect(
                                x1, y1 - 8 - 5, x1 + text_length + 5, y1
                            )
                            page.draw_rect(text_rect, color=(0, 0, 0), fill=(1, 1, 1))
                            rc = page.insert_textbox(
                                text_rect,
                                target_name,
                                fontsize=8,
                                fontname="Times-Roman",
                                align=1,
                            )

                pdf_document.save(f"{pdf_out_path}/{file}")
                pdf_document.close()
            else:
                print(f"Region boundaries already drawn on {file}")


# import scipdf

# # article_dict = scipdf.parse_pdf_to_dict("scanned_pdfs/test2.pdf")
# # print(article_dict)

# # xml = scipdf.parse_pdf("scabbed_pdfs/test2.pdf", soup=True)
# # print(xml.prettify())

if __name__ == "__main__":
    create_paths(
        [
            PDFS_PATH,
            SCANNED_PDFS_PATH,
            OCR_PDFS_PATH,
            OUT_PATH,
            OUT_FIGURES_PATH,
            PDFS_WITH_REGIONS,
        ]
    )

    create_scanned_pdfs(PDFS_PATH, SCANNED_PDFS_PATH, dpi=200)

    ocr_scanned_pdfs(SCANNED_PDFS_PATH, OCR_PDFS_PATH)

    detect(OCR_PDFS_PATH, OUT_PATH)

    process_figures(
        OUT_FIGURES_PATH,
        OUT_DATA_PATH,
        PROCESSED_FIGURES_PATH,
        padding=10,
        max_crop=0.1,
        ignore_first=5,
    )

    process_json_files(OUT_DATA_PATH)

    draw_region_boundaries(OCR_PDFS_PATH, OUT_DATA_PATH, PDFS_WITH_REGIONS)
