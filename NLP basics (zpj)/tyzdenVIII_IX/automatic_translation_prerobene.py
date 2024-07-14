
import xml.etree.ElementTree as ET
import pandas
import string
import math


def strip_tag_name(element_tag):
    t = element_tag
    i = t.find("}")
    if i != -1:
        t = t[i+1:]
    return t

def remove_punct(text):
    return text.translate(str.maketrans('', '', string.punctuation))

def extract_sentences_from_pair(sentence_pair, orig_lan, target_lan):
    sent1, sent2 = sentence_pair
    lan1, sent1 = sent1
    lan2, sent2 = sent2
    orig_lan_sentence = sent1 if lan1 == orig_lan else sent2
    targ_lan_sentence = sent2 if lan2 == target_lan else sent1
    return orig_lan_sentence, targ_lan_sentence


def get_parallel_sents(translated_word, sent_element, orig_lan, target_lan, input_file, set_limit=None, reverse=False):
    context = ET.iterparse(input_file, events=('start', 'end'))
    new_dict = dict()
    translated_word = translated_word.lower()
    orig_lan_sent_tokens = None
    sentence_pair = []
    if reverse:
        orig_lan, target_lan = target_lan, orig_lan
    for index, (event, elm) in enumerate(context):
        if index == 0:
            root = elm
        element_tag = strip_tag_name(elm.tag)
        if event == 'start':
            if elm.attrib:
                sent_language = list(elm.attrib.values())[0]
            if elm.text and element_tag == sent_element:
                formatted_element_text = remove_punct(elm.text.lower())
                sentence_pair.append((sent_language, formatted_element_text))
                if len(sentence_pair) == 2:
                    orig_lan_sent, targ_lan_sent = extract_sentences_from_pair(sentence_pair,orig_lan,target_lan)
                    orig_lan_sent_tokens = orig_lan_sent.split()
                    sentence_pair = list()
                if orig_lan_sent_tokens and translated_word in orig_lan_sent_tokens:
                    new_dict[orig_lan_sent] = targ_lan_sent
                if set_limit and len(new_dict) >= set_limit:
                    break
        if event == 'end':
            if element_tag == 'tu':
                root.clear()
    return new_dict


def get_words(sents):
    words = set()
    for sent in sents:
        words.update(sent.split())
    return list(words)


def get_sent_bow(words, sents, binary=True):
    bow = pandas.DataFrame(index=sents, columns=words, data=[[0]*len(words)]*len(sents))
    for sent in sents:
        sent_token = sent.split()
        for token in sent_token:
            bow.loc[sent, token] += 1
    if binary:
        bow = 1 * (bow > 0)
    return bow


def get_sent_freq(bow):
    return bow.sum(axis=0)


def get_n_translation_candidates(n, sentences):
    words = get_words(sentences)
    bow = get_sent_bow(words, sentences, binary=True)
    sent_freq = get_sent_freq(bow)
    return list(sent_freq.nlargest(n).index), bow


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

def get_kw_bow(bow):
   sumdf = bow.sum(axis=1)
   probability_of_word_in_text = bow.loc[:, :].div(sumdf, axis=0)
   sumdf = bow.sum(axis=0)
   probability_of_word = sumdf / len(sumdf)
   kw_score_bow = probability_of_word_in_text / probability_of_word
   return kw_score_bow

def score_translation_candidates(translation_candidates, bow):
   scored_candidates = dict()
   kw_score_bow = get_kw_bow(bow)
   tf_idf_bow = get_tfidfbow(bow)
   number_of_documents = len(bow.index)
   for candidate in translation_candidates:
       kw_score = 0
       tf_idf_score = 0
       for document in bow.index:
           kw_score += kw_score_bow.loc[document, candidate] if candidate in tf_idf_bow else 0
           tf_idf_score += tf_idf_bow.loc[document, candidate] if candidate in tf_idf_bow else 0
       kw_score = kw_score / number_of_documents
       tf_idf_score = tf_idf_score / number_of_documents
       scored_candidates[candidate] = kw_score + tf_idf_score
   return scored_candidates

def split_dict(dictionary):
   return list(dictionary.keys()), list(dictionary.values())

def sort_dict_keys(dictionary, reverse=True):
   return [k for k, v in sorted(dictionary.items(), key=lambda item: item[1], reverse=reverse)]

def translate_and_score_candidate(candidate, candidate_num, *args):
   parallel_sents = get_parallel_sents(candidate, *args, reverse=True)
   candidate_target_sents, candidate_original_sents = split_dict(parallel_sents)
   candidate_candidates, candidate_bow = get_n_translation_candidates(candidate_num ** 2, candidate_original_sents)
   scored_candidate_candidates = score_translation_candidates(candidate_candidates, candidate_bow)
   sorted_scored_candidate_candidates = sort_dict_keys(scored_candidate_candidates)
   return sorted_scored_candidate_candidates, scored_candidate_candidates

def quick_test(candidates, translated_word, *args):
   sorted_candidates = sort_dict_keys(candidates)
   candidate_num = len(candidates)
   translation = None
   for candidate in sorted_candidates:
       sorted_scored_candidate_candidates, _ = translate_and_score_candidate(candidate, candidate_num, *args)
       if translated_word in sorted_scored_candidate_candidates:
           translation = candidate
           break
   return translation

def slow_test(candidates, translated_word, *args):
   sorted_candidates = sort_dict_keys(candidates)
   candidate_num = len(candidates)
   translation = (None, 0)
   for candidate in sorted_candidates:
       sorted_scored_candidate_candidates, scored_candidate_candidates = translate_and_score_candidate(candidate,
                                                                                                       candidate_num,
                                                                                                       *args)
       if translated_word in sorted_scored_candidate_candidates:
           score1, score2 = candidates[candidate], scored_candidate_candidates[translated_word]
           translated_word_index = sorted_scored_candidate_candidates.index(translated_word)
           score = score1 * score2 * translated_word_index
           translation = (candidate, score) if score >= translation[1] else translation    #score<=translation[1] bo: translated_word_index = 0 ?
   return translation[0]

def test_candidates(candidates, translated_word, fast_test=False, *args):
   test_function = quick_test if fast_test else slow_test
   return test_function(candidates, translated_word, *args)

def translate_word(translated_word, *parallel_sent_args, test_translation_candidates=False, fast_test=False):
   parallel_sents = get_parallel_sents(translated_word, *parallel_sent_args)
   orig_sents, target_sents = split_dict(parallel_sents)
   translation_candidates, translation_bow = get_n_translation_candidates(candidate_num, target_sents)
   translation_candidates = score_translation_candidates(translation_candidates, translation_bow)
   if test_translation_candidates:
       translation_candidates = test_candidates(translation_candidates, translated_word, fast_test,
                                                *parallel_sent_args)
   return translation_candidates
  
  
if __name__ == "__main__":
   translated_word = "voorstel" #"voorstel" "Europese" werking
   lang_orig = 'nl'
   lang_targ = 'sk'
   set_sample_limit = 10
   input_file = r"PATH"
   tag1, tag2 =  "tuv", "seg"
   candidate_num = 15
   parallel_sent_args = [tag2,lang_orig, lang_targ, input_file,set_sample_limit]
   translation = translate_word(translated_word, *parallel_sent_args,
                                test_translation_candidates=True,
                                fast_test=True)
   print(f'Translation of "{translated_word}" from {lang_orig} to {lang_targ} is:\n{translated_word} ~> {translation}')