import xml.etree.ElementTree as ET
import time
import argparse


def strip_tag_name(element_tag):
    t = element_tag
    i = t.find("}")
    if i != -1:
        t = t[i+1:]
    return t


def extract_element_content(element, input_file, output_file):
    context = ET.iterparse(input_file, events=('start', 'end'))
    counter = 0
    first_line = True
    with open(output_file, 'w', encoding='utf-8') as outfile:
        for index, (event, elm) in enumerate(context):
            if index == 0:
                root = elm
            element_tag = strip_tag_name(elm.tag)
            if event == 'start':
                if element_tag == element:
                    content_to_write = elm.text if first_line else '\n' + elm.text
                    first_line = False
                    outfile.write(content_to_write)
                    counter += 1
            if event == 'end':
                if element_tag == 'LM':
                    root.clear()
    return counter


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="extracts tag content from xml")
    parser.add_argument("element", help="element tag to be extracted")
    parser.add_argument("input_file", help="input xml file with language info database")
    parser.add_argument("output_file", help="output xml file")
    parser.add_argument("--t", dest="time", action="store_const", const=True, default=False, help="time execution")
    args = parser.parse_args()
    time_start = time.perf_counter()
    number_of_elements = extract_element_content(element=args.element, input_file=args.input_file, output_file=args.output_file)
    time_end = time.perf_counter()
    print(f'Total number of elements written:\t{number_of_elements}')
    if args.time:
        print(f'Total time elapsed: {time_end - time_start}s',
              f'Average time to process 1 element: {(time_end-time_start)/number_of_elements}')