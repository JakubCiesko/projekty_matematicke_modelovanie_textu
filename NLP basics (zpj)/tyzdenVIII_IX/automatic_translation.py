import xml.etree.ElementTree as ET
import pandas
import string
import random
import math
import numpy
import cython

#Prepisat cele


#numba
@cython.cdivision(True)
def PMI(word_A, word_B, bow, bowB, px_bow=None, pxpy_bow=None, lower=True):
    """Calculates PMI for wordA and wordB in BOW"""
    if lower:
        word_A, word_B = word_A.lower(), word_B.lower()
    number_of_sentsA = len(bow)
    number_of_sentsB = len(bowB)
    if number_of_sentsA == 0 or number_of_sentsB == 0:
        return

    if px_bow is not None:
        p_A, p_B = px_bow[word_A], px_bow[word_B]
    else:
        rel_word_countA = bow.sum(axis=0) / number_of_sentsA
        rel_word_countB = bowB.sum(axis=0) / number_of_sentsB
        p_A, p_B = rel_word_countA[word_A], rel_word_countB[word_B]

    coincidence = list()
    for i in range(min(len(bow.index),len(bowB.index))):
        coincidence.append(bow.iloc[i].loc[word_A] * bowB.iloc[i].loc[word_B] > 0)
    p_A_B = sum(coincidence) / (min(number_of_sentsA,number_of_sentsB))

    if pxpy_bow is not None:
        pApB = pxpy_bow.loc[word_A, word_B]
    else:
        pApB = p_A*p_B
    if pApB == 0:
        return 0 # should be numpy.nan
    if p_A_B == 0:
        return 0 #0 works better than -numpy.inf (WHY!?)
    return numpy.log(p_A_B) - numpy.log(pApB)


def get_topN_in_dict(dictionary, topn, i=1, j=None, reverse=True):
    def f_selector(item):
        return item[i][j] if j else item[i]
    sorted_dict = dict(sorted(dictionary.items(), key=f_selector, reverse=reverse))
    top_n = dict()
    i = 0
    for k, v in sorted_dict.items():
        if i == topn or i == len(sorted_dict):
            return top_n
        top_n[k] = v
        i += 1
    return top_n


def strip_tag_name(element_tag):
    t = element_tag
    i = t.find("}")
    if i != -1:
       t = t[i+1:]
    return t


def remove_punct(text):
    return text.translate(str.maketrans('', '', string.punctuation))


#bez input_file, output_file (to riesene na inom mieste [predtym])
def get_parallel_sents(word, lang_element, sent_element, orig_lan, targ_lan, input_file, output_file, set_limit=None,
                            random_sample=False):
    context = ET.iterparse(input_file, events=('start', 'end'))
    new_dict = dict()
    found_word = None
    if random_sample and set_limit:
        old_limit = set_limit   #prec
        set_limit *= 4
    if output_file:
        first_line = True
        with open(output_file, 'w', encoding='utf-8') as outfile:
            outfile.write(f'Phrases in {orig_lan} containing "{word}" & and their aligned phrases in {targ_lan}\n\n')
            for index, (event, elm) in enumerate(context):
                if index == 0:
                    root = elm
                element_tag = strip_tag_name(elm.tag)
                if event == 'start':
                    if element_tag == lang_element:
                        if elm.attrib[list(elm.attrib.keys())[0]] == orig_lan:
                            original_lan = True         #da sa previest original_lan na target_lan? zredukovat
                            target_lan = False
                        if elm.attrib[list(elm.attrib.keys())[0]] == targ_lan:
                            target_lan = True
                            original_lan = False

                    if element_tag == sent_element:
                        if elm.text:
                            text_without_punct = remove_punct(elm.text)
                            if original_lan:
                                if word in text_without_punct.split():
                                    new_dict[elm.text] = None
                                    found_word = elm.text
                            elif target_lan and found_word:
                                new_dict[found_word] = elm.text
                                found_word = None
                                if set_limit:
                                    if len(new_dict) >= set_limit:
                                        if random_sample:
                                            new_dict = dict(random.sample(new_dict.items(), old_limit))
                                        break
                            content_to_write = elm.text if first_line else '\n' + elm.text
                            outfile.write(content_to_write)
                            first_line = False

                if event == 'end':
                    if element_tag == 'tu':
                        root.clear()
    else:   #dve funkcie v if
        for index, (event, elm) in enumerate(context):
            if index == 0:
                root = elm
            element_tag = strip_tag_name(elm.tag)
            if event == 'start':
                if element_tag == lang_element:
                    if elm.attrib[list(elm.attrib.keys())[0]] == orig_lan:
                        original_lan = True
                        target_lan = False
                    if elm.attrib[list(elm.attrib.keys())[0]] == targ_lan:
                        target_lan = True
                        original_lan = False

                if element_tag == sent_element:
                    if elm.text:
                        text_without_punct = remove_punct(elm.text)
                        if original_lan:
                            if word in text_without_punct.split():
                                new_dict[elm.text] = None
                                found_word = elm.text
                        elif target_lan and found_word:
                            new_dict[found_word] = elm.text
                            found_word = None
                            if set_limit:
                                if len(new_dict) >= set_limit:
                                    if random_sample:
                                        new_dict = dict(random.sample(new_dict.items(), old_limit))
                                    break


            if event == 'end':
                if element_tag == 'tu':
                    root.clear()

    return new_dict


def get_frequencies(sent_sent_dict):
    original_freq = dict()
    target_freq = dict()
    for sentA, sentB in sent_sent_dict.items():
        if sentA:
            sentA_words = remove_punct(sentA).lower().split()
            for wordA in sentA_words:
                if not wordA in original_freq:
                    original_freq[wordA] = 0
                original_freq[wordA] += 1
        if sentB:
            sentB_words = remove_punct(sentB).lower().split()
            for wordB in sentB_words:
                if wordB in target_freq:
                    target_freq[wordB] += 1
                else:
                    target_freq[wordB] = 1
    return original_freq, target_freq


def get_sentences_bow(words, sents, binary=True):
    bow = pandas.DataFrame(columns=words, index=sents, data=[[0]*len(words)]*len(sents))
    for sent in bow.index:
        if sent:
            tokens = remove_punct(sent).lower().split()
            for token in tokens:
                if binary:
                    bow.loc[sent, token] = 1
                else:
                    bow.loc[sent, token] += 1
    return bow


def get_everpresent_words(binary_bow, n, relative=False):
    word_counts = binary_bow.sum(axis=0)
    if relative:
        word_counts = word_counts/len(binary_bow.index)
    return word_counts.nlargest(n)


def tf_idf(bow, word, text):
    """Returns TF-IDF score of word in BOW"""
    freq = bow[word][text]
    no_of_documents = len(bow.index)
    no_of_documents_with_word = sum(bow[word].apply(lambda x: x > 0))
    tfidfscore = freq*(math.log10(no_of_documents)-math.log10(no_of_documents_with_word))
    return tfidfscore


def get_tfidfbow(bow, threshold=0, verbose=False):
    """Transforms BoW to TF-IDF BoW. Returns BoW with TF-IDF scores instead of frequencies."""
    if verbose:
        print('\nCreating TF-IDF Bag of Words out of sparse Bag of Words\n')
    bow_tfidfsc = pandas.DataFrame(columns=bow.columns, index=bow.index)
    texts = bow.index
    for text in texts:
        if verbose:
            print(f'Processing: {text}')
        for word in bow:
            bow_tfidfsc.loc[text, word] = tf_idf(bow, word, text)
    return bow_tfidfsc.loc[:, (bow_tfidfsc > threshold).any(axis=0)]


#parallel_sents von, tam predspracovane veci uz
def get_translation_candidates(word, lang_element, sent_element, orig_lan, targ_lan, Ncandidates, input_file, output_file, set_limit=None,
                            random_sample=False):

    parallel_sents = get_parallel_sents(word, lang_element, sent_element, orig_lan, targ_lan,
                                        input_file,
                                        output_file, set_limit=set_limit, random_sample=random_sample)
    # Determining frequency of each word in extracted parralel sentences
    original, target = get_frequencies(parallel_sents)
    target_words = [word for word in target.keys()]
    original_words = [word for word in original.keys()]
    # Binary BOWS
    binary_target_bow = get_sent_presence(target_words, parallel_sents.values())
    # BOW
    target_bow = get_sent_presence(target_words, parallel_sents.values(), binary=False)
    original_bow = get_sent_presence(original_words, parallel_sents.keys(), binary=False)
    # words with highest sentence occurrence
    everpresent_target_word = get_everpresent_words(binary_target_bow, Ncandidates, relative=True)
    tfidf_target_bow = get_tfidfbow(target_bow)
    topN_candidates = set(everpresent_target_word.index).union(set(get_topN_in_dict(target, Ncandidates).keys()))
    topN_candidates_scored = dict()
    #Determining candidates' scores
    sumdf = target_bow.sum(axis=1)
    probability_of_word_in_text = target_bow.loc[:, :].div(sumdf, axis=0)
    sumdf = target_bow.sum(axis=0)
    probability_of_word = sumdf/len(sumdf)
    kw_score_bow = probability_of_word_in_text/probability_of_word

    for candidate in topN_candidates:
        tf_idf_score = 0
        kw_score = 0
        number_of_documents = len(tfidf_target_bow.index)
        second_metric = 0
        for document in tfidf_target_bow.index:
            if candidate in tfidf_target_bow.loc[document,:]:
                second_metric += 1
                tf_idf_score += tfidf_target_bow.loc[document, candidate]
                kw_score += kw_score_bow.loc[document, candidate]
        PMI_score = PMI(word, candidate, original_bow, target_bow)
        #topN_candidates_scored[candidate] = (tf_idf_score / number_of_documents, kw_score/number_of_documents, PMI_score)
        topN_candidates_scored[candidate] = tf_idf_score / number_of_documents + kw_score/number_of_documents - PMI_score
    return get_topN_in_dict(topN_candidates_scored,Ncandidates, reverse=False)


def check_translation(translation_candidates, word, lang_element, sent_element, orig_lan, targ_lan,
                      input_file, output_file=None, set_limit=None,random_sample=False):
    for translation_candidate in translation_candidates:
        parallel_sents = get_parallel_sents(translation_candidate, lang_element, sent_element, targ_lan, orig_lan,
                                            input_file,
                                            output_file=output_file, set_limit=set_limit, random_sample=random_sample)

        # Determining frequency of each word in extracted parralel sentences
        target, original = get_frequencies(parallel_sents)
        original_words = [word for word in target.keys()]
        target_words = [word for word in original.keys()]

        # Binary BOWS
        binary_target_bow = get_sent_presence(target_words, parallel_sents.values())
        binary_original_bow = get_sent_presence(original_words, parallel_sents.keys())
        results = dict()
        if word in binary_original_bow:
            target_in_document_freq = binary_target_bow.sum(axis=0)[translation_candidate]
            word_in_doc_freq = binary_original_bow.sum(axis=0)[word]
            results[translation_candidate] = word_in_doc_freq/target_in_document_freq
        else:
            results[translation_candidate] = 0
    return get_topN_in_dict(results, len(results))

if __name__ == "__main__":
    translated_word = "voorstel" #"voorstel" "Europese"
    # translated_word = "voorstel" --> {'návrh': 1.0163178649287705, 'a': 1.278520474043821};
    # translated_word = "Europese" --> {'európskej': 0.9948814635512102, 'a': 1.7383387846634166};
    number_of_candidates = 2
    lang_orig = 'nl'
    lang_targ = 'sk'
    set_sample_limit = 20
    random_sample = True
    input_file = r"D:\kody\data\lng\opus_nlp\nl-sk.tmx"

    args = (translated_word, "tuv", "seg",
            lang_orig, lang_targ, number_of_candidates,
            input_file,
            "D:\kody\data\lng\opus_nlp\\new.txt")

    translation_candidates = get_translation_candidates(*args, set_limit=set_sample_limit, random_sample=random_sample)
    results = check_translation(translation_candidates, translated_word,'tuv','seg',lang_targ, lang_orig,
                                input_file,set_limit=set_sample_limit,random_sample=random_sample)

    


