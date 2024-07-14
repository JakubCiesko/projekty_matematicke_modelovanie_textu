import os
import argparse
import time
from heapq import nlargest
from bs4 import BeautifulSoup
import spacy


def get_token_by_dep(doc, dep_name):
    for token in doc:
        if dep_name in token.dep_:
            subtree = list(token.subtree)
            start = subtree[0].i
            end = subtree[-1].i + 1
            return doc[start:end]
    return None


def get_subject_phrase(doc):
    return get_token_by_dep(doc, 'subj')


def get_object_phrase(doc):
    return get_token_by_dep(doc, 'obj')


def get_root_verb(doc):
    for token in doc:
        if "ROOT" in token.dep_:
            return token
    return None


def add_lemma_to_dict(token, dct):
    if token is None:
        lemma = token
    else:
        lemma = token.lemma_.lower()
    if lemma in dct:
        dct[lemma] += 1
    else:
        dct[lemma] = 1


def extract_tag_contents(file_path, tag):
    with open(file_path, 'r', encoding='utf-8') as file:
        data = file.read()
        soup = BeautifulSoup(data)

    return soup.find_all(tag)


def remove_text_between_symbols(string, symbols):
    i = string.find(symbols[0])
    j = string.find(symbols[1])
    pre = string[:i]
    chars_to_end = len(string) - j
    if i == -1 or j == -1:
        return string
    if chars_to_end >= 3 and string[j + 2] == ' ':
        m = 2
    else:
        m = 1
    post = string[j + m:]
    return pre+post


def preprocess_text(text,
                    symbols=(['<', '>'],
                             ['(', ')'],
                             ['[', ']'],
                             ['&lt;', '>'],
                             ['/','/'])):
    for symbol in symbols:
        l, r = symbol
        text = remove_text_between_symbols(text, [l, r])
        text = remove_text_between_symbols(text, [l, r])
        text = remove_text_between_symbols(text, [l, r])
    return ' '.join(text.split())


def extract_svo(tags, s=dict(), v=dict(), o=dict()):
    for element in tags:
        text = preprocess_text(element.text)
        doc = nlp(text)
        add_lemma_to_dict(get_subject_phrase(doc), s)
        add_lemma_to_dict(get_object_phrase(doc), o)
        add_lemma_to_dict(get_root_verb(doc), v)
    return s, v, o


def extract_svo_from_folder(source_folder_path, tag, verbose=False):
    for file in os.listdir(path=source_folder_path):
        if verbose:
            print(f'Processing file: {file}')
        source = source_folder_path + file
        try:
            tag_contents = extract_tag_contents(source, tag)
            s, v, o = extract_svo(tag_contents)
        except UnicodeDecodeError:
            pass
    return s, v, o


def write_n_most_freq_svo(n, s,v,o, file = f'most_frequent_svo.txt'):
    with open(file,'w',encoding='utf-8') as output_file:
        output_file.write(f'{n} MOST FREQUENT SUBJECTS\tFREQUENCY\n')
        for subject in nlargest(n,s,key=s.get):
            output_file.write(f'{subject}\t{s[subject]}\n')
        output_file.write(f'{n} MOST FREQUENT VERBS\tFREQUENCY\n')
        for verb in nlargest(n,v,key=v.get):
            output_file.write(f'{verb}\t{v[verb]}\n')
        output_file.write(f'{n} MOST FREQUENT OBJECTS\tFREQUENCY\n')
        for obj in nlargest(n,o,key=o.get):
            output_file.write(f'{obj}\t{o[obj]}\n')


if __name__ == '__main__':
    nlp = spacy.load('en_core_web_md', disable=['ner', 'textcat'])
    parser = argparse.ArgumentParser(description="extracts n-most frequent subjects, verbs and objects from folder with sgm")
    parser.add_argument("tag", help="tag to be extracted")
    parser.add_argument("n", type=int, default=15, help="n most frequent")
    parser.add_argument("input_folder", help="input sgm file with reuters database")
    parser.add_argument("output_file", help="output txt file")
    parser.add_argument("--t", dest="time", action="store_const", const=True, default=False, help="time execution")
    parser.add_argument("--v", dest="verbose", action="store_const", const=True, default=False, help="verbose")
    args = parser.parse_args()

    time_start = time.perf_counter()
    s, v ,o = extract_svo_from_folder(source_folder_path=args.input_folder, tag=args.tag, verbose=args.verbose)
    write_n_most_freq_svo(args.n, s, v, o, file=args.output_file)
    time_end = time.perf_counter()

    if args.time:
        print(f'time elapsed: {time_end - time_start}s')



