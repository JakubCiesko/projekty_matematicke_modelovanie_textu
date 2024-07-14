import os
import pandas
import re
import numpy
import string


def get_global_dict(path, parsing_regex=rf" ", file_extension=".txt", encoding="utf-8",
                     stop_words=None, replace_substr=("\n","\t"), replace_for=" "):
    """Creates global dictionary from all txt files in folder. Returns python dict. Use small files in size only!"""
    global_dictionary = dict()
    for file in os.listdir(path=path):
        if file.endswith(file_extension):
            file_path = os.path.join(path, file)
            with open(file_path, 'r', encoding=encoding) as input_file:
                text_file = input_file.read()
                for replace_symbol in replace_substr:
                    text_file = text_file.replace(replace_symbol, replace_for)
                parsing_entities = re.split(pattern=parsing_regex, string=text_file)
                for parsing_entity in parsing_entities:
                    parsing_entity = parsing_entity.lower().strip()
                    parsing_entity = parsing_entity.translate(str.maketrans('', '', string.punctuation))
                    if parsing_entity not in global_dictionary:
                        if stop_words and parsing_entity in stop_words:
                                continue
                        global_dictionary[parsing_entity] = len(global_dictionary)
    return global_dictionary


def get_bow(path, parsing_regex=rf" ", gd_parsing_regex=rf" ", verbose=False, given_global_dict=None,
            stop_words=None, encoding='utf-8', file_extension='.txt', replace_substr=("\n","\t"),
            replace_for=" ", binary=False, transpose=False):
    """Creates Bag of Words representation of txt files in folder. Use small files in size only!"""
    trigger_warning = False
    omitted_counter = 0
    if not given_global_dict:
        if verbose:
            print('Creating global dictionary')
        global_dict = get_global_dict(path, parsing_regex=gd_parsing_regex, stop_words=stop_words,
                                      encoding=encoding, file_extension=file_extension,
                                      replace_substr=replace_substr, replace_for=replace_for)
    else:
        global_dict = given_global_dict
    bow = pandas.DataFrame(columns=global_dict.keys())
    if verbose:
        print(f'\nCreating sparse Bag of Words for path: {path}\n')
    for file in os.listdir(path=path):
        if file.endswith('.txt'):
            text_vector = [0]*len(global_dict)
            text_file = file
            file_path = os.path.join(path, text_file)
            if verbose:
                print(f'Processing file {text_file}')
            with open(file_path, 'r', encoding='utf-8') as input_file:
                text = input_file.read()
                for replace_symbol in replace_substr:
                    text = text.replace(replace_symbol, replace_for)
                parsing_entities = re.split(pattern=parsing_regex, string=text)
                for parsing_entity in parsing_entities:
                    if gd_parsing_regex != parsing_regex:
                        for reparsing_entity in re.split(gd_parsing_regex, parsing_entity):
                            reparsing_entity = reparsing_entity.lower().strip()
                            reparsing_entity = reparsing_entity.translate(str.maketrans('', '', string.punctuation))
                            if stop_words and reparsing_entity in stop_words:
                                continue
                            if reparsing_entity in global_dict:
                                original_value = text_vector[global_dict[reparsing_entity]]
                                text_vector[global_dict[reparsing_entity]] = original_value + 1 if not binary else 1
                            else:
                                omitted_counter += 1
                                trigger_warning = True
                    else:
                        parsing_entity = parsing_entity.lower().strip()
                        parsing_entity = parsing_entity.translate(str.maketrans('', '', string.punctuation))
                        if stop_words and parsing_entity in stop_words:
                                    continue
                        original_value = text_vector[global_dict[parsing_entity]]
                        text_vector[global_dict[parsing_entity]] = original_value + 1 if not binary else 1
                    bow.loc[parsing_entity] = text_vector
    if transpose:
        bow = bow.transpose()
    if trigger_warning:
        print(f'\nWARNING:\t{omitted_counter}/{len(global_dict)} tokens were omitted due to reparsing!\n')
    return bow


def PMI(word_A, word_B, bow):
    """Calculates PMI for wordA and wordB in BOW"""
    word_A, word_B = word_A.lower(), word_B.lower()
    number_of_sents = len(bow)
    rel_word_count = bow.sum(axis=0) / number_of_sents
    p_A, p_B = rel_word_count[word_A], rel_word_count[word_B]
    index_mask = bow[word_A] * bow[word_B] > 0
    p_A_B = sum(index_mask) / number_of_sents
    pApB = p_A*p_B
    if pApB == 0:
        return numpy.nan #numpy.nan
    if p_A_B == 0:
        return -numpy.inf #-numpy.inf
    return numpy.log(p_A_B/pApB)


def get_collocates(query_word, bow, top_num=None):
    """Return dict of query_word's collocates."""
    collocates = dict()
    for word in bow:
        collocates[word] = PMI(query_word, word, bow)
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


if __name__ == "__main__":
    #Path to folder of recent DennikN articles
    path = r"D:\kody\data\korpus\korpus_knihy\ceske\ddskal\LDA\articles"
    sent_pattern = rf"[.!?;]+"
    words = ["moderátor", "netflix", "Zuzana", "cena", "babiš"]
    N_collocates = 20
    #Creating global dictionary of words (tokens seperated by " ")
    global_dictionary = get_global_dict(path, parsing_regex=' ')
    #Creating BOW with sentence rows and word columns. Each position contains binary value 0/1.
    my_bow = get_bow(path, parsing_regex=sent_pattern, given_global_dict=global_dictionary, binary=True, verbose=True)
    #N words with highest PMI value.
    for word in words:
        print(f'\n{word}', f'\n\tTop {N_collocates} collocates:')
        topN_collocates = get_collocates(word, my_bow, N_collocates)
        print(topN_collocates)

    """
moderátor
	Top 20 collocates:
{'moderátor': 3.833460682925044, 'popoludňajšej': 3.833460682925044, 'televíznej': 3.833460682925044, 'šou': 3.833460682925044, 'dali': 3.833460682925044, 'take': 3.833460682925044, 'that': 3.833460682925044, 'chlapčenské': 3.833460682925044, 'stvorili': 3.833460682925044, 'vplyvní': 3.833460682925044, 'hudobní': 3.833460682925044, 'manažéri': 3.833460682925044, '„poznali': 3.833460682925044, 'skôr': 3.833460682925044, 'tancovali': 3.833460682925044, 'spievali': 3.833460682925044, 'spriatelili': 3.833460682925044, '1996': 3.8334606829250437, 'ony': 3.8334606829250437, 'vydali': 3.8334606829250437}

netflix
	Top 20 collocates:
{'netflix': 0.17561333805883617, 'očakávajte': 0.17561333805883617, 'vyrezané': 0.17561333805883617, 'srdcia': 0.17561333805883617, 'tragickú': 0.17561333805883617, 'lásku': 0.17561333805883617, 'krajinu': 0.17561333805883617, 'ponorenú': 0.17561333805883617, 'hmly': 0.17561333805883617, 'mihotavé': 0.17561333805883617, 'svetlo': 0.17561333805883617, 'sviečok': 0.17561333805883617, 'tvorcovia': 0.17561333805883617, 'inšpiračné': 0.17561333805883617, 'zdroje': 0.17561333805883617, 'neskrývajú': 0.17561333805883617, 'asistenta': 0.17561333805883617, 'detektívovi': 0.17561333805883617, 'robí': 0.17561333805883617, 'kadetov': 0.17561333805883617}

Zuzana
	Top 20 collocates:
{'2106': 0.20763936477824455, 'zuzana': 0.20763936477824455, 'čaputová': 0.20763936477824455, 'linharttomáš': 0.20763936477824455, 'vodrážkaprokop': 0.20763936477824455, 'ndeník': 0.20763936477824455, 'ngabriel': 0.20763936477824455, 'kuchta': 0.20763936477824455, 'prezidentky': 0.20763936477824455, 'zuzany': 0.20763936477824455, 'zvolení': 0.20763936477824455, 'petra': 0.20763936477824455, 'nového': 0.20763936477824455, 'bola': 0.20763936477824455, 'veľkým': 0.20763936477824455, 'prekvapením': 0.20763936477824455, 'panovala': 0.20763936477824455, 'celé': 0.20763936477824455, 'sobotné': 0.20763936477824455, 'popoludnie': 0.20763936477824455}

cena
	Top 20 collocates:
{'radí': 0.287682072451781, 'finančné': 0.287682072451781, 'trhy': 0.287682072451781, 'rozkývať': 0.287682072451781, 'spor': 0.287682072451781, 'dlhový': 0.287682072451781, 'usa': 0.287682072451781, 'pôžičky': 0.287682072451781, 'menej': 0.287682072451781, 'trest': 0.287682072451781, 'deficity': 0.287682072451781, 'príde': 0.287682072451781, '1834': 0.287682072451781, 'hegerova': 0.287682072451781, 'malé': 0.287682072451781, 'podniky': 0.287682072451781, 'vydýchnuť': 0.287682072451781, '16': 0.287682072451781, 'vďaka': 0.287682072451781, 'predĺženiu': 0.287682072451781}

babiš
	Top 20 collocates:
{'shemesh': 0.14042321866244403, 'prušová': 0.14042321866244403, 'zaplnil': 0.14042321866244403, 'námestie': 0.14042321866244403, 'stretol': 0.14042321866244403, 'stalinistom': 0.14042321866244403, 'výsledok': 0.14042321866244403, 'wirnitzer': 0.14042321866244403, 'ceste': 0.14042321866244403, 'stať': 0.14042321866244403, 'českým': 0.14042321866244403, 'ficom': 0.14042321866244403, 'predpovedajú': 0.14042321866244403, 'politológ': 0.14042321866244403, 'i': 0.14042321866244403, 'novinárka': 0.14042321866244403, 'alžbeta': 0.14042321866244403, 'kyselicová': 0.14042321866244403, 'výsledky': 0.14042321866244403, 'druhého': 0.14042321866244403}
"""
