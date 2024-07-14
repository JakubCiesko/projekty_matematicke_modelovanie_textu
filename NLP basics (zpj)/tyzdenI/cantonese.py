import argparse
import time
import re


def extract_token_and_info(string: str):
    return re.findall(r"^\s*(\w{2})\b.*?\w+?(\d).*?\w+(\d).*?\d{8}-(\w)\s*$", string)


def format_token_and_info(token_info: list) -> str:
    return '\t'.join(token_info[0])


def extract_token_and_info_from_file(file_path, new_file_path):
    lines_read = 0
    lines_wrote = 0
    with open(file_path, 'r', encoding='utf-8') as input_file:
        first_line = True
        with open(new_file_path, 'w', encoding='utf-8') as output_file:
            for line in input_file:
                lines_read += 1
                token_and_info_in_line = extract_token_and_info(line)
                if token_and_info_in_line:
                    formatted_token_and_info = format_token_and_info(token_and_info_in_line)
                    line_to_write = formatted_token_and_info
                    if not first_line:
                        line_to_write = "\n" + line_to_write
                    output_file.write(line_to_write)
                    lines_wrote += 1
                    first_line = False
    return lines_read, lines_wrote


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="extracts info from cantonese")
    parser.add_argument("cantonese_file", help="txt file with cantonese tokens and info")
    parser.add_argument("new_txt_file", help="new txt file")
    parser.add_argument("--t", dest="time", action="store_const", const=True, default=False, help="time execution")
    args = parser.parse_args()
    file_path = args.cantonese_file
    new_file_path = args.new_txt_file
    ts = time.time()
    lines_read, lines_wrote = extract_token_and_info_from_file(file_path=file_path, new_file_path=new_file_path)
    print(f"lines read:\t{lines_read}\tlines wrote:\t{lines_wrote}")
    te = time.time()

    if args.time:
        print(f'Time elapsed:\t{te - ts}s')
