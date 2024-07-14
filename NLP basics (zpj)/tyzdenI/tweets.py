import argparse
import time


def extract_hashtags(string: str) -> list:
    import re
    return re.findall(r"(#.+?)\b", string)


def get_hashtags_from_file(file_path, new_file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        first_line = True
        with open(new_file_path, 'w', encoding='utf-8') as g:
            for line in f:
                hashtags = extract_hashtags(line)
                if hashtags:
                    g.write("\t".join(hashtags)) if first_line else g.write("\n" + "\t".join(hashtags))
                    first_line = False



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extracts # from tweets")
    parser.add_argument("tweets_txt_file", help="txt file with tweets")
    parser.add_argument("new_file", help="new file")
    parser.add_argument("--t", dest="time", action="store_const", const=True, default=False, help="time execution")
    args = parser.parse_args()

    ts = time.time()
    get_hashtags_from_file(file_path=args.tweets_txt_file, new_file_path=args.new_file)
    te = time.time()
    if args.time:
        print(f'Time elapsed:\t{te - ts}s')
