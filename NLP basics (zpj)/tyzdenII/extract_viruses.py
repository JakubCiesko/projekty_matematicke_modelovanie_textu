import xml.etree.ElementTree as ET
import time
import argparse


def strip_tag_name(element_tag):
    t = element_tag
    i = t.find("}")
    if i != -1:
        t = t[i+1:]
    return t


def extract_viruses_info(input_file, output_file):
    source = input_file
    context = ET.iterparse(source, events=("start", "end"))
    is_virus, in_comment_function, first_line = False, False, True
    counter = 0
    with open(output_file, "w", encoding="utf-8") as output_file:
        for index, (event, element) in enumerate(context):
            tag_name = strip_tag_name(element.tag)
            if index == 0:
                root = element
            if event == "start":
                if tag_name == "comment" and element.attrib == {'type': 'function'}:
                    in_comment_function = True
                if tag_name == "taxon" and element.text == "Viruses":
                    is_virus = True
                    content_to_write = f"{protein_id}\t" if first_line else f"\n{protein_id}\t"
                    first_line = False
                    output_file.write(content_to_write)
                    counter += 1
                if tag_name == "accession":
                    protein_id = element.text
                if in_comment_function and tag_name == "text" and is_virus:
                    comment_text = element.text

            if event == "end":
                if tag_name == "entry":
                    is_virus = False
                    protein_id = None
                    comment_text = ""
                    root.clear()
                if tag_name == "comment" and element.attrib == {'type': 'function'}:
                    if type(comment_text) == str:
                        output_file.write(comment_text)
                    in_comment_function = False
    return counter


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="extracts viruses text info from xml")
    parser.add_argument("input_file", help="input xml file with protein database")
    parser.add_argument("output_file", help="output xml file")
    parser.add_argument("--t", dest="time", action="store_const", const=True, default=False, help="time execution")
    args = parser.parse_args()
    time_start = time.perf_counter()
    number_of_viruses = extract_viruses_info(input_file=args.input_file, output_file=args.output_file)
    time_end = time.perf_counter()
    print(f'Total number of viruses:\t{number_of_viruses}')
    if args.time:
        print(f'time elapsed: {time_end-time_start}s')
