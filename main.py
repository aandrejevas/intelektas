import fitz
import os
import ocrmypdf
import scipdf


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
                    pdf_to_scanned_pdf(
                        f"{input_path}/{file}", f"{scanned_pdf_path}/{file}", dpi
                    )


# Run OCR on scanned pdfs in a folder
def ocr_scanned_pdfs(scanned_pdf_path, ocr_pdf_path):
    if os.path.isdir(scanned_pdf_path):
        for file in os.listdir(scanned_pdf_path):
            if file.endswith(".pdf"):
                if not os.path.exists(f"{ocr_pdf_path}/{file}"):
                    ocrmypdf.ocr(f"{scanned_pdf_path}/{file}", f"{ocr_pdf_path}/{file}")


# Creates paths if they don't exist
def create_paths(paths):
    for path in paths:
        if not os.path.exists(path):
            os.makedirs(path)


# import scipdf

# # article_dict = scipdf.parse_pdf_to_dict("scanned_pdfs/test2.pdf")
# # print(article_dict)

# # xml = scipdf.parse_pdf("scabbed_pdfs/test2.pdf", soup=True)
# # print(xml.prettify())

if __name__ == "__main__":
    create_paths(["pdfs", "scanned_pdfs", "ocr_pdfs", "out"])

    create_scanned_pdfs("pdfs", "scanned_pdfs", 200)

    ocr_scanned_pdfs("scanned_pdfs", "ocr_pdfs")

    # scipdf.parse_figures("ocr_pdfs/test1.pdf", output_folder="out")
    # scipdf.parse_figures("ocr_pdfs/test2.pdf", output_folder="out")
    scipdf.parse_figures("ocr_pdfs/test3.pdf", output_folder="out")
