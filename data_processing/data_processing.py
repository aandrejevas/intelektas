from PIL import Image, ImageOps


def crop_and_save(image_path, output_path, padding=10, max_cropped_bottom=0.1):
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
