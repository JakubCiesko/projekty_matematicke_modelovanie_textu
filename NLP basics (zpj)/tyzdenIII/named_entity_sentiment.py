import os
import re
from bs4 import BeautifulSoup
from heapq import nlargest
from heapq import nsmallest
from spacytextblob.spacytextblob import SpacyTextBlob
import spacy
import argparse
import time


def timeit(fn):
    def timeit_wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        result = fn(*args, **kwargs)
        end_time = time.perf_counter()
        print(f'\nFunction {fn.__name__}\nProvided args and kwargs:\t{args} {kwargs}:\n\t\tTime elapsed: {end_time-start_time}')
        return result
    return timeit_wrapper


def extract_tag_contents(file_path, tag):
    file = open(file_path, 'r', encoding='utf-8')
    data = file.read()
    soup = BeautifulSoup(data)
    file.close()
    return soup.find_all(tag)


def add_lemma_to_dict(*tokens, value, dct, thorough=False):
    for token in tokens[0]:
        if token is None:
            lemma = token
        else:
            lemma = token.lemma_.lower().strip()
        if thorough:
            if lemma.endswith('\'s'):
                lemma = lemma[:-2]
            for k, v in dct.items():
                if k.startswith(lemma):
                    lemma = k
                    break
        if lemma in dct:
            value_to_be_added = (dct[lemma][1] * dct[lemma][0] + value) / (dct[lemma][0] + 1)
            limit_value = 1 if value_to_be_added > 0 else -1
            dct[lemma][1] = value_to_be_added if abs(dct[lemma][1] + value_to_be_added) <= 1 else limit_value
            dct[lemma][0] += 1
        else:
            dct[lemma] = [1, value]




def remove_pattern(string, pattern=r'<.*?>'):
    if type(string) == str:
        match = re.search(pattern, string)
        if match:
            i = match.start()
            j = match.end()
            return string[:i - 1] + string[j:]
    return str(None)


def merge_tuples(*tuples):
    merged_tuples = []
    for this_tuple in tuples:
        merged_tuples.extend(this_tuple)
    return list(set(merged_tuples))


def remove_entity_from_str(entity, string):
    i = string.strip().lower().find(entity.strip().lower())
    j = len(entity)
    pre = string[:i]
    post = string[i+j:]
    text = pre+post
    return ' '.join(text.split())


def get_named_entity_by_label(entities, labels=['ORG', 'GPE']):
    return [entity for entity in entities if entity.label_ in labels]


def get_named_entity(doc, polarity_string):
    doc1 = nlp(doc.text.title().lower())
    doc2 = nlp(doc.text.lower().title())
    entities = get_named_entity_by_label(merge_tuples(doc1.ents, doc2.ents))
    for entity in entities:
        polarity_string = remove_entity_from_str(entity.text, polarity_string)
    polarity = nlp(polarity_string)._.blob.polarity
    return entities, polarity


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
    return pre + post


def preprocess_text(text,
                    symbols=(['<', '>'],
                             ['(', ')'],
                             ['[', ']'],
                             ['&lt;', '>'],
                             ['/', '/'])):
    for symbol in symbols:
        l, r = symbol
        text = remove_text_between_symbols(text, [l, r])
        text = remove_text_between_symbols(text, [l, r])
        text = remove_text_between_symbols(text, [l, r])
    return ' '.join(text.split())


def extract_named_entity(tags, ne=dict(), thorough=False, regex=False):
    for tag in tags:
        text = remove_pattern(tag.text) if regex else preprocess_text(tag.text)
        doc = nlp(text)
        lemma, value = get_named_entity(doc, text)
        add_lemma_to_dict(lemma, value=value, dct=ne, thorough=thorough)
    return ne


@timeit
def extract_named_entities_from_folder(source_folder_path, tag, verbose=False, thorough=False, regex=False):
    ne = None
    for file in os.listdir(path=source_folder_path):
        if verbose:
            print(f'Processing file: {file}')
        source = source_folder_path + file
        try:
            tag_contents = extract_tag_contents(source, tag)
            ne = extract_named_entity(tag_contents, thorough=thorough, regex=regex)
        except UnicodeDecodeError:
            pass
    return ne


def write_n_most_freq_ne(n, ne, m = 0, file = f'most_frequent_ne.txt'):
    with open(file, 'w' , encoding='utf-8') as output_file:
        output_file.write(f'{n - m} MOST FREQUENT NAMED ENTITIES\tSENTIMENT\n\n')
        for named_entity in nlargest(n, ne, key=ne.get)[m:]:
            output_file.write(f'{named_entity}\t{ne[named_entity]}\n')
        output_file.write(f'\n\n{n - m} LEAST FREQUENT NAMED ENTITIES\tSENTIMENT\n')
        for named_entity in nsmallest(n, ne, key=ne.get)[m:]:
            output_file.write(f'{named_entity}\t{ne[named_entity]}\n')
    return


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='sentiment analysis of sentences with [ORG, GPE] named entities')
    parser.add_argument("input_folder", help="input sgm file with reuters database")
    parser.add_argument("output_file", help="output txt file")
    parser.add_argument("tag", help="tag to be extracted")
    parser.add_argument("n", type=int, default=15, help="n most frequent")
    parser.add_argument("m", type=int, default=0, help="number of omitted results")
    parser.add_argument("--t", dest="thorough", action="store_const", const=True, default=False, help="thorough data polishing")
    parser.add_argument("--v", dest="verbose", action="store_const", const=True, default=False, help="verbose")
    parser.add_argument("--r", dest="regex", action="store_const", const=True, default=False, help="use regex to preprocess")
    args = parser.parse_args()


    nlp = spacy.load('en_core_web_md')
    nlp.add_pipe('spacytextblob')
    ne = extract_named_entities_from_folder(args.input_folder,
                                            args.tag,
                                            verbose=args.verbose,
                                            thorough=args.thorough,
                                            regex=args.regex)
    ne = {k: v[1] for k, v in ne.items()}
    write_n_most_freq_ne(args.n, ne, args.m, args.output_file)