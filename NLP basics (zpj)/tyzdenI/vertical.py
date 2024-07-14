import argparse
import time


def extract_token_postag(string: str):
    import re
    return re.findall(r"(\w+|\d+)\t.*\t(.).*", string)


def format_postag_list(postag_list: list, glue_string="_")->str:
    return glue_string.join(postag_list[0])


def format_vertical_file(file_path, new_file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        first_line = True
        with open(new_file_path, 'w', encoding='utf-8') as g:
            for line in f:
                token_postag_in_line = extract_token_postag(line)
                if token_postag_in_line:
                    formatted_string = format_postag_list(token_postag_in_line)
                    g.write(formatted_string) if first_line else g.write("\n" + formatted_string)
                    first_line = False




if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="extracts token postag from vertical format.")
    parser.add_argument("vertical_txt_file", help="txt file with vertical format")
    parser.add_argument("new_txt_file", help="new txt file")
    parser.add_argument("--t", dest="time", action="store_const", const=True, default=False, help="time execution")
    args = parser.parse_args()
    ts = time.time()
    format_vertical_file(file_path=args.vertical_txt_file, new_file_path=args.new_txt_file)
    te = time.time()
    if args.time:
        print(f'Time elapsed:\t{te - ts}s')

