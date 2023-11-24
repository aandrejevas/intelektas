import json
from PIL import Image, ImageOps
import re


def crop_and_save(
    image_path, json_path, output_path, padding=10, max_cropped_bottom=0.1
):
    # Open the image
    original_image = Image.open(image_path)

    # Crop artifacts at the bottom
    cropped_image = crop_bottom(original_image)
    if (
        cropped_image.height
        < original_image.height - original_image.height * max_cropped_bottom
    ):
        cropped_image = original_image

    # Get bounding box of non-white region
    bbox = get_non_white_bbox(cropped_image)

    # Crop the image to the bounding box
    cropped_image = cropped_image.crop(bbox)

    # Add padding
    image = add_padding(cropped_image, padding)

    # Save image
    image.save(output_path)

    # Modify json data
    new_bounding_box = list(bbox)
    new_bounding_box[0] -= padding
    new_bounding_box[1] -= padding
    new_bounding_box[2] += padding
    new_bounding_box[3] += padding
    element_name = image_path.split("/")[-1].split(".")[0].split("-")[1]
    if "Figure" in element_name:
        element_name = element_name.replace("Figure", "")
        type = "Figure"
    if "Table" in element_name:
        element_name = element_name.replace("Table", "")
        type = "Table"

    update_data(
        json_path,
        new_bounding_box,
        element_name,
        (original_image.width, original_image.height),
        type,
    )


def crop_bottom(image, color=(255, 255, 255), ignore_first=10):
    # Find the first row from the bottom where a non-white pixel is encountered
    bottom_row = image.height - 1 - ignore_first
    while bottom_row >= 0:
        if any(image.getpixel((x, bottom_row)) != color for x in range(image.width)):
            bottom_row -= 1
        else:
            break

    # Crop the image to remove artifacts at the bottom
    cropped_image = image.crop((0, 0, image.width, bottom_row + 1))

    return cropped_image


def update_data(json_path, new_bounding_box, element_name, original_size, type):
    with open(json_path, "r+") as file:
        json_data = json.load(file)
        needed_index = None
        for index, element in enumerate(json_data):
            if element.get("name") == element_name and element.get("figType") == type:
                needed_index = index
                break
        boundary = json_data[needed_index]["regionBoundary"]
        scaling_factor = original_size[0] / (boundary["x2"] - boundary["x1"])
        boundary["x1"] = boundary["x1"] + new_bounding_box[0] / scaling_factor
        boundary["y1"] = boundary["y1"] + new_bounding_box[1] / scaling_factor
        boundary["x2"] = (
            boundary["x2"] - (original_size[0] - new_bounding_box[2]) / scaling_factor
        )
        boundary["y2"] = (
            boundary["y2"] - (original_size[1] - new_bounding_box[3]) / scaling_factor
        )

        json_data[needed_index]["regionBoundary"] = boundary

        file.seek(0)
        json.dump(json_data, file, indent=2)
        file.truncate()


def get_non_white_bbox(image):
    # Find bounding box of non-white region
    inverted_image = ImageOps.invert(image)
    bbox = inverted_image.getbbox()

    return bbox


def add_padding(image, padding, color=(255, 255, 255)):
    # Get the size of the cropped image
    original_width, original_height = image.size

    # Calculate the size of the new image with padding
    new_width = original_width + 2 * padding
    new_height = original_height + 2 * padding

    # Create a new image with white background
    padded_image = Image.new("RGB", (new_width, new_height), color)

    # Paste the cropped image onto the new image with padding
    padded_image.paste(image, (padding, padding))

    return padded_image
