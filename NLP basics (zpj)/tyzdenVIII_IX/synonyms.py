import os
import pandas
import spacy
import numpy
import cython


@cython.cdivision(True)
def PMI(word_A, word_B, bow, px_bow=None, pxpy_bow=None, lower=True):
    """Calculates PMI for wordA and wordB in BOW"""
    if lower:
        word_A, word_B = word_A.lower(), word_B.lower()
    number_of_sents = len(bow)

    if number_of_sents == 0:
        return

    if px_bow is not None:
        p_A, p_B = px_bow[word_A], px_bow[word_B]
    else:
        rel_word_count = bow.sum(axis=0) / number_of_sents
        p_A, p_B = rel_word_count[word_A], rel_word_count[word_B]

    index_mask = bow[word_A] * bow[word_B] > 0
    p_A_B = sum(index_mask) / number_of_sents

    if pxpy_bow is not None:
        pApB = pxpy_bow.loc[word_A,word_B]
    else:
        pApB = p_A*p_B
    if pApB == 0:
        return 0 # should be numpy.nan
    if p_A_B == 0:
        return 0 #0 works better than -numpy.inf (WHY!?)
    return numpy.log(p_A_B/pApB)


def get_collocates(query_word, bow, top_num=None, lower=True, px_bow=None, pxpy_bow=None):
    """Return dict of query_word's collocates."""
    collocates = dict()
    for word in bow:
        score = PMI(query_word, word, bow, lower=lower,px_bow=px_bow, pxpy_bow=pxpy_bow)
        if score > 0:
            collocates[word] = score
    collocates = dict(sorted(collocates.items(), key=lambda item: item[1], reverse=True))
    if top_num:
        top_n = dict()
        i = 0
        for k, v in collocates.items():
            if i == top_num or i == len(collocates):
                return top_n
            top_n[k] = v
            i += 1
    return collocates


def get_global_dict(path, spacy_model, file_extension=".txt", encoding="utf-8", sents=False, verbose=False, stop=False):
    f"""returns dictionary of all {file_extension} files in folder using given spacy model"""
    global_dictionary = dict()
    for file in os.listdir(path=path):
        if file.endswith(file_extension):
            file_path = os.path.join(path, file)
            with open(file_path, 'r', encoding=encoding) as input_file:
                if verbose:
                    print(f'Processing {file}')
                for line in input_file:
                    line_doc = spacy_model(line)
                    if sents:
                        for sent in line_doc.sents:
                            global_dictionary[sent.text] = len(global_dictionary)
                    else:
                        for word in line_doc:
                            dict_entry = (word.lemma_, word.dep_)
                            if stop and word.is_stop:
                                continue
                            if dict_entry not in global_dictionary:
                                global_dictionary[dict_entry] = len(global_dictionary)
    return global_dictionary


def get_bow(model, columns, index, binary=False, verbose=False):
    """Returns bow representation with frequencies of columns in rows"""
    bow = pandas.DataFrame(data=[[0]*len(columns)], columns=columns, index=index)
    if verbose:
        total_row_num = len(bow.index)
        row_count = 0
        infix = "binary " if binary else ""
        print(f'Creating sparse {infix}BoW representation.')
    for row in bow.index:
        if verbose:
            if row_count%100 == 0:
                print(f'{row_count} / {total_row_num} BoW rows processed')
            row_count += 1
        row_doc = model(row)
        for token in row_doc:
            column_index = (token.lemma_, token.dep_)
            if column_index in bow:
                if binary:
                    bow.loc[row, column_index] = 1
                else:
                    bow.loc[row, column_index] += 1
    return bow


@cython.cdivision(True)
def calculate_word_similarity(wordA, wordB, bow, given_collocates=None,
                              lower=True, correction_element=lambda x,y: -((x-y)**2)/50, px_bow=None, pxpy_bow=None):
    """Calculates word similarity"""

    wordA_collocates = get_collocates(wordA, bow, lower=lower, px_bow=px_bow, pxpy_bow=pxpy_bow)
    if given_collocates:
        wordB_collocates = given_collocates
    else:
        wordB_collocates = get_collocates(wordB, bow, lower=lower, px_bow=px_bow, pxpy_bow=pxpy_bow)
    numerator = 0
    denominator = sum(wordA_collocates.values()) + sum(wordB_collocates.values())
    for collocate, collocate_score in wordA_collocates.items():
        if collocate in wordB_collocates:
            a, b = collocate_score, wordB_collocates[collocate]
            numerator += a+b+correction_element(a,b)
    return numerator/denominator


def get_topN_in_dict(dictionary, topn):
    sorted_dict = dict(sorted(dictionary.items(), key=lambda item: item[1], reverse=True))
    top_n = dict()
    i = 0
    for k, v in sorted_dict.items():
        if i == topn or i == len(sorted_dict):
            return top_n
        top_n[k] = v
        i += 1
    return topn


def find_synonyms(query_word, bow, same_pos=False, topn=None, lower=True, correction_element=lambda x,y: -((x-y)**2)/50,
                 px_bow=None, pxpy_bow=None, verbose=False):
    """Returns words with highest similarity to query_word from given bow"""
    i = 0
    similar_words = dict()
    query_word_lemma, query_word_pos = query_word
    query_word_collocates = get_collocates(query_word, bow, lower=lower, top_num=topn, px_bow=px_bow,pxpy_bow=pxpy_bow)
    for token in bow:
        token_lemma, token_pos = token
        if query_word_lemma == token_lemma:
            continue
        if same_pos:
            if query_word_pos == token_pos:
                similar_words[token] = calculate_word_similarity(token, None, bow=bow,
                                                                 given_collocates=query_word_collocates, lower=False,
                                                                 correction_element=correction_element,
                                                                 px_bow=px_bow, pxpy_bow=pxpy_bow)
        else:
            similar_words[token] = calculate_word_similarity(token, None, bow=bow,
                                                   given_collocates=query_word_collocates, lower=False,
                                                             correction_element=correction_element,
                                                             px_bow=px_bow, pxpy_bow=pxpy_bow)
        i += 1
        if verbose and len(similar_words) > 0 and i%100 == 0:
            print(i, '\ttokens processed\nBest match so far:')
            print(max(similar_words, key=similar_words.get))

    similar_words = get_topN_in_dict(similar_words, topn) if topn else similar_words
    return similar_words


if __name__ == "__main__":
    #Path to folder with some dutch Wiki-articles
    path = r"D:\Nový priečinok\dutch\dutch"
    #Loading Spacy dutch model
    nlp_dutch = spacy.load("nl_core_news_sm")
    #Creating dictionary of tokens, sentences and BOW
    token_global_dict = get_global_dict(path, nlp_dutch, verbose=True, stop=True)
    sent_global_dict = get_global_dict(path, nlp_dutch, sents=True, verbose=True)
    bow = get_bow(nlp_dutch, columns=token_global_dict.keys(), index=sent_global_dict, verbose=True, binary=True)
    print(bow)


    #Creating:  1. pandas dataframe with relative frequencies of tokens (probability_bow)
    #           2. pandas dataframe with probabilities of random TokenX-TokenY occurrence (pxpy_bow)
    #Both are passed to find_synonyms function to avoid repetitive calculations and enhance speed.
    probability_bow = bow.sum(axis=0)/len(bow)
    pxpy_bow = pandas.DataFrame(index=probability_bow.index, columns=probability_bow.index,
                                data=[[px*py for px in probability_bow] for py in probability_bow])
    #Determining synonym of word stad (city/town)
    word = ('stad', 'nsubj')
    synonyms = find_synonyms(word, bow, topn=15, lower=False, same_pos=True,
                       px_bow=probability_bow, pxpy_bow=pxpy_bow, verbose=True)
    print(synonyms)

    """
    amsterdam, gemeente, groot-amsterdam, aantal, plaats, toestroom, zuidelijke, bezienswaardigheid....
    """