import matplotlib.pyplot as plt
import spacy
import argparse


def save_histogram(x, file_name):
    plt.hist(x, bins=60)
    plt.savefig(file_name)


def read_file(file_path):
    with open(file_path,'r', encoding='utf-8') as input_file:
        data = input_file.read()
    return data


def get_sent_lens(text_string):
    doc = nlp(text_string)
    sent_lengths = list()
    for sent in doc.sents:
        sent_lengths.append(len(sent))
    return sent_lengths


def print_results(sent_lens):
    print('AVG SEN LEN:\t', sum(sent_lens)/len(sent_lens))
    print('MAX SEN LEN:\t', max(sent_lens), '\nMIN SEN LEN:\t', min(sent_lens))


def main(input_file, output_file):
    nlp = spacy.load('en_core_web_md', exclude=["parser"])
    nlp.enable_pipe('senter')
    sen_lens = get_sent_lens(read_file(input_file))
    save_histogram(sen_lens, output_file)
    print_results(sen_lens)
    return


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="measures average sentence length in file and saves histogram.")
    parser.add_argument("input_file", help="input txt file")
    parser.add_argument("output_file_path", help="output png file")
    args = parser.parse_args()
    main(args.input_file, args.output_file)
