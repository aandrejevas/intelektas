import fitz
import os


def extract_images(pdf_path, pages_path, figure_path):
    """Explores given path and processes all pdfs in the folder, if a pdf is given it processes the pdf"""
    if os.path.isdir(pdf_path):
        for file in os.listdir(pdf_path):
            if file.endswith(".pdf"):
                extract_images(f"{pdf_path}/{file}", pages_path, figure_path)
    else:
        process_pdf(figure_path, pages_path, pdf_path)


def process_pdf(figure_path, pages_path, pdf_path):
    """Extracts the images from the pdf and saves them as png files, marks figures in the pages as png files"""
    pdf_document = fitz.open(pdf_path)
    for page_number in range(pdf_document.page_count):
        page = pdf_document.load_page(page_number)
        image_list = page.get_images(full=True)
        file_name = pdf_document.name.split("/")[-1].split(".")[0]
        for img_index, img in enumerate(image_list):
            save_image_png(figure_path, img, img_index, page_number, pdf_document, file_name)
            draw_rect_images(img, page)
        page_list = page.get_pixmap()
        page_list.save(f"{pages_path}/{file_name}_{page_number + 1}.png")
    pdf_document.close()


def draw_rect_images(img, page):
    """Draws a rectangle around the image"""
    image_box = page.get_image_bbox(img)
    rect = fitz.Rect(image_box)
    shape = page.new_shape()
    shape.draw_rect(rect)
    shape.finish(color=(1, 0, 0), width=2, dashes=None)
    shape.commit()


def save_image_png(figure_path, img, img_index, page_number, pdf_document, file_name):
    """Extracts the image from the pdf and saves it as a png file"""
    xref = img[0]
    base_image = pdf_document.extract_image(xref)
    image_bytes = base_image["image"]
    image_format = base_image["ext"]
    image_extension = image_format.lower() if image_format else "png"
    image_filename = f"{figure_path}/{file_name}_page_{page_number + 1}_img_{img_index}.{image_extension}"
    with open(image_filename, "wb") as f:
        f.write(image_bytes)


if __name__ == "__main__":
    pdf_path = "../pdfs/"
    output_folder = "../out/metadata/"
    pages_path = f"{output_folder}pages"
    if not os.path.exists(pages_path):
        os.makedirs(pages_path)
    figure_path = f"{output_folder}figures"
    if not os.path.exists(figure_path):
        os.makedirs(figure_path)
    extract_images(pdf_path, pages_path, figure_path)
