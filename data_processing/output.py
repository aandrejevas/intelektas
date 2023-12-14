import os
import json
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom import minidom


class OutputXML:
    def __init__(self, source_page, target_name, type, number, x1, y1, x2, y2):
        self.source_page = source_page
        self.target_name = target_name
        self.type = type
        self.number = number
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2


def convert_to_xml(json_data, general_counter, total_figures, total_tables):
    root = Element("root")

    # Sort json_data based on page and location
    sorted_json_data = sorted(
        json_data, key=lambda entry: (entry["page"], entry["regionBoundary"]["y1"])
    )

    for entry in sorted_json_data:
        element = SubElement(root, "element")
        element.set("source_page", str(entry["page"] + 1))

        # Convert Roman numerals to normal numbers
        try:
            number = int(entry["name"])
        except ValueError:
            # Handle Roman numerals
            number = roman_to_number(entry["name"])

        element.set(
            "target_name",
            f"{general_counter:04d}{entry['figType'][0].lower()}{number:02d}",
        )

        element.set("type", "f" if entry["figType"] == "Figure" else "t")
        element.set("number", str(number))
        element.set("x1", str(entry["regionBoundary"]["x1"]))
        element.set("y1", str(entry["regionBoundary"]["y1"]))
        element.set("x2", str(entry["regionBoundary"]["x2"]))
        element.set("y2", str(entry["regionBoundary"]["y2"]))

        general_counter += 1
        if entry["figType"] == "Figure":
            total_figures += 1
        elif entry["figType"] == "Table":
            total_tables += 1

    return root, general_counter, total_figures, total_tables


def save_xml(root, file_path):
    xml_str = minidom.parseString(tostring(root)).toprettyxml(indent="    ")
    with open(file_path, "w") as xml_file:
        xml_file.write(xml_str)


def roman_to_number(roman):
    roman_dict = {"I": 1, "V": 5, "X": 10, "L": 50, "C": 100, "D": 500, "M": 1000}
    result = 0

    prev_value = 0
    for numeral in reversed(roman):
        value = roman_dict[numeral]
        if value < prev_value:
            result -= value
        else:
            result += value
        prev_value = value

    return result


def process_json_files(folder_path):
    for filename in os.listdir(folder_path):
        if filename.endswith(".json"):
            general_counter = 0
            total_figures = 0
            total_tables = 0

            json_path = os.path.join(folder_path, filename)

            with open(json_path, "r") as json_file:
                json_data = json.load(json_file)

            xml_root, general_counter, total_figures, total_tables = convert_to_xml(
                json_data, general_counter, total_figures, total_tables
            )

            xml_filename = filename.replace(".json", ".xml")
            xml_path = os.path.join(folder_path, xml_filename)
            save_xml(xml_root, xml_path)
