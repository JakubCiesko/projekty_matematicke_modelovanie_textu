import argparse
import functools
import re
import time as tm


def extract_dmy_strings(date: str,
                        pattern=r"(\d+)\..*?(\w+).*?(\d+)") -> list:
    return re.findall(pattern, date)


def extract_time_string(time: str,
                        pattern = r"(\d+:\d+)") -> list:
    return re.findall(pattern, time)


def extract_headline_string(headline: str,
                            pattern=r"(^[\w,\.\s]*$)") -> list:
    return re.findall(pattern, headline)


def extract_info(string: str):
    result = [None]
    if extract_dmy_strings(string):
        result = extract_dmy_strings(string)
    if extract_time_string(string):
        result = extract_time_string(string)
    if extract_headline_string(string):
        result = extract_headline_string(string)
    return result[0]


def format_output(*strings: str) -> str:
    output_string = str()
    for string in strings:
        output_string += string + '\t'
    return output_string.strip('\t')


def format_headlines_file(file_name, new_file_name):
    with open(file_name, 'r', encoding='utf-8') as input_file:
        with open(new_file_name, 'w', encoding='utf-8') as output_file:
            while True:
                lines_read = list()
                dates, times, headlines = list(), list(), list()
                for _ in range(6):
                    line_read = input_file.readline()
                    lines_read.append(line_read)
                    if extract_dmy_strings(line_read):
                        dates.append(line_read)
                    if len(dates) > len(times) and extract_time_string(line_read):
                        times.append(line_read)
                    if len(times) > len(headlines) and extract_headline_string(line_read):
                        headlines.append(line_read)
                if not functools.reduce(lambda x, y: bool(x)+bool(y),lines_read):
                    break
                for i in range(len(headlines)):
                    y, m, d = extract_dmy_strings(dates[i])[0]
                    time = times[i].strip()
                    headline = headlines[i].strip()
                    print(headlines)
                    string_to_write = f'{y}\t{m}\t{d}\t{time}\t{headline}\n'
                    print(string_to_write)
                    output_file.write(f'{string_to_write}')
    return





if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Formats headline txt file.")
    parser.add_argument("original_file_path", help="(original) file to be formatted")
    parser.add_argument("new_file_path", help="new file")
    parser.add_argument("--t", dest="time", action="store_const", const=True, default=False, help="time execution")
    args = parser.parse_args()
    ts = tm.time()
    format_headlines_file(file_name=args.original_file_path, new_file_name=args.new_file_path)
    te = tm.time()
    if args.time:
        print(f'Time elapsed:\t{te - ts}s')
