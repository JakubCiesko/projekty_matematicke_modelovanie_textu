import argparse
import time
import re


def extract_email_address(string: str):
    #email_pattern = r'([^\.\s\[,;<(][^@\s:=]+@[^@\s\[\]:,;\.<>()=]+\.[^@\s\]:"\',;\.>)=]+[^\.\s\],;>)\\])'
    #email_pattern = r'([^@\s\'<:(/)]+@[^@\s,;?]+\.[^@\s>\'()\.,;:"]+)'
    #email_pattern = r'([^@\s]+@[^@\s]+\.[^@\s]+)'
    email_pattern = r'([^@\s\[:"\',<(?=]+@[^@"\':\s,]+\.[^@\s\]\."\',>:)+A-Z;/]+)'
    matches = re.findall(email_pattern, string)
    nmatches = list()
    if matches:
        for match in matches:
            if not re.search(r'(http://)|(http%)', match) and not match.endswith('cc'):
                nmatches.append(match)
    return nmatches


def format_emails(emails):
    return '\t'.join(emails)


def cache_email(emails: list, cache = {}) -> dict:
    for email in emails:
        if email in cache.keys():
            cache[email] += 1
        else:
            cache[email] = 1
    return cache


def extract_emails_from_txt_file(file_path, new_file_path):
    lines_read = 0
    lines_wrote = 0
    ignore_first_new_line = False
    with open(file_path, 'r', encoding='utf-8') as input_file:
        with open(new_file_path, 'w', encoding='utf-8') as output_file:
            second_line = input_file.readline()
            while True:
                first_line = second_line
                second_line = input_file.readline()
                line = first_line.strip()+second_line.strip()
                lines_read += 1
                emails_in_line = extract_email_address(line)
                if emails_in_line:
                    #cache_email(emails_in_line,cache)
                    formatted_emails = format_emails(emails_in_line)
                    content = formatted_emails if not ignore_first_new_line else "\n" + formatted_emails
                    output_file.write(content)
                    lines_wrote += 1
                    ignore_first_new_line = True
                if not first_line or not second_line:
                    break
    return lines_read, lines_wrote, cache


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="extracts email addresses from txt")
    parser.add_argument("emails_file", help="txt file with emails to be extracted")
    parser.add_argument("new_txt_file", help="new txt file")
    parser.add_argument("--t", dest="time", action="store_const", const=True, default=False, help="time execution")
    args = parser.parse_args()
    ts = time.time()
    lines_read, lines_wrote, cache = extract_emails_from_txt_file(file_path=args.emails_file, new_file_path=args.new_txt_file)
    te = time.time()
    print(lines_read, '\t', lines_wrote)

    with open(args.new_txt_file + '_cache', 'w', encoding='utf-8') as g:
        for k,v in cache.items():
            g.write(f'{k} :\t{v}\n')

    if args.time:
        print(f'Time elapsed:\t{te - ts}s')