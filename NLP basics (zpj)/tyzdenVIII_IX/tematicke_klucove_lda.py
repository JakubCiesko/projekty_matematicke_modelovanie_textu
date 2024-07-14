import os
import pandas
import numpy as np
import gensim
from gensim.corpora.dictionary import Dictionary
from sklearn.decomposition import LatentDirichletAllocation as LDA
from matplotlib import pyplot as plt


class NoModelGiven(Exception):
    """Raised when no model was given."""
    def __init__(self, message =  "No Spacy Model was passed as an argument to the function."):
        self.message = message
        super().__init__(self.message)


def get_freq_dict(path, use_spacy=False, file_extension=".txt", encoding="utf-8", spacy_model=None):
    """Return freq dictionary of text files in given folder"""
    global_dictionary = dict()
    if use_spacy:
        if spacy_model:
            nlp = spacy_model
        else:
            raise NoModelGiven

    for file in os.listdir(path=path):
        if file.endswith(file_extension):
            this_file_dict = dict()
            file_path = os.path.join(path, file)
            with open(file_path, 'r', encoding=encoding) as input_file:
                for line in input_file:
                    if not use_spacy:
                        words = line.split()
                        for word in words:
                            word = word.lower()
                            if word not in this_file_dict:
                                this_file_dict[word] = 1
                            else:
                                this_file_dict[word] += 1
                    else:
                        line_doc = nlp(line)
                        for token in line_doc:
                            word = token.text.lower()
                            if word not in this_file_dict:
                                this_file_dict[word] = 1
                            else:
                                this_file_dict[word] += 1
                global_dictionary[file] = this_file_dict
    return global_dictionary


def load_stop_words(stop_words_path):
    """Loads stop words from file, returns list"""
    with open(stop_words_path, 'r', encoding='utf-8') as input_file:
        stop_words = list()
        for line in input_file:
            stop_words.append(line[:-1])
    return stop_words


def get_global_dict(path, use_spacy=False, file_extension=".txt", encoding="utf-8", spacy_model=None, stop_words=None):
    """Creates global dictionary from all txt files in folder. Returns python dict."""
    global_dictionary = dict()
    if use_spacy:
        if spacy_model:
            nlp = spacy_model
        else:
            raise NoModelGiven

    for file in os.listdir(path=path):
        if file.endswith(file_extension):
            file_path = os.path.join(path, file)
            with open(file_path, 'r', encoding=encoding) as input_file:
                for line in input_file:
                    if not use_spacy:
                        words = line.split()
                        for word in words:
                            word = word.lower()
                            if word not in global_dictionary:
                                if stop_words and word in stop_words:
                                        continue
                                global_dictionary[word] = len(global_dictionary)
                    else:
                        line_doc = nlp(line)
                        for token in line_doc:
                            word = token.text.lower()
                            if word not in global_dictionary:
                                if stop_words and word in stop_words:
                                    continue
                                global_dictionary[word] = len(global_dictionary)

    return global_dictionary


def get_bow(path, verbose=False, use_spacy=False, given_global_dict=None, spacy_model=None, stop_words=None):
    """Creates Bag of Words representation of txt files in folder."""
    if verbose:
        print('Creating global dictionary')
    if use_spacy:
        if spacy_model:
            nlp = spacy_model
        else:
            raise NoModelGiven("No Spacy Model was passed as an argument to the function.")
    if not given_global_dict:
        global_dict = get_global_dict(path, use_spacy=use_spacy, spacy_model=spacy_model, stop_words=stop_words)
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
                for line in input_file:
                    if not use_spacy:
                        words = line.split()
                        for word in words:
                            word = word.lower()
                            if stop_words and word in stop_words:
                                continue
                            text_vector[global_dict[word]] += 1
                    else:
                        line_doc = nlp(line)
                        for token in line_doc:
                            word = token.text.lower()
                            if stop_words and word in stop_words:
                                continue
                            text_vector[global_dict[word]] += 1
            bow.loc[file] = text_vector
    return bow


def get_rel_frequency(word, text):
    return text.loc[word]/text.sum()


def get_rel_BOW(bow):
    """Tranforms BOW with absolute frequencies into BOW with relative frequencies"""
    sumdf = bow.sum(axis=1)
    bow = bow.loc[:,:].div(sumdf, axis=0)
    return bow


def get_keywordness_score(word, text, reference_corpus, rf=False):
    """Calculates keywordness score"""
    p = get_rel_frequency
    if rf:
        return text.loc[word]/reference_corpus.loc[word]
    score = p(word, text)/p(word,reference_corpus)
    return score


def get_keyword_bow(bow, given_reference_corpus=None , rf=False):
    """Returns pandasdataframe with keywords of given bow"""
    keyword_bow = bow.copy()
    reference_corpus = given_reference_corpus
    for text_label in bow.index:
        if given_reference_corpus.empty:
            reference_corpus = bow.drop(text_label).sum(axis=0)
        text = bow.loc[text_label]
        for word in bow:
            score = get_keywordness_score(word, text, reference_corpus, rf=rf)
            keyword_bow.loc[text_label, word] = score
    return keyword_bow


def sort_freq_dict(freq_dicts):
    """Sorts frequency dictionary from largest to smallest"""
    sorted_freq_dict = dict()
    for text, freq_dict in freq_dicts.items():
        sorted_freq_dict[text] = {x: freq_dict[x] for x in sorted(freq_dict, key=freq_dict.get, reverse=True)}
    return sorted_freq_dict


def get_h_point(sorted_freq_dicts):
    """Returns dictionary with h-point values for dictionary of sorted frequency dictionaries"""
    h_point_dict = dict()
    for text, freq_dict in sorted_freq_dicts.items():
        h_point = 0
        for rank, freq in enumerate(freq_dict.values()):
                if rank == freq:
                    h_point = rank
                elif rank < freq:
                    ri, rj = rank, rank + 1
                    fi, fj = freq, list(freq_dict.values())[rj]
                    h_point = (fi*rj-fj*ri)/(rj-ri+fi-fj)
        h_point_dict[text] = h_point
    return h_point_dict


def get_autosemantic_words(sorted_freq_dicts):
    """Return autosemantic words above h-point"""
    autosemantic_words = dict()
    h_points = get_h_point(sorted_freq_dicts)
    for text, h_point in h_points.items():
        autosemantic_words[text] = list(sorted_freq_dicts[text].keys())[int(h_point):]
    return autosemantic_words



if __name__ == "__main__":
    verbose = True
    use_spacy = False
    use_gensim = False
    if use_spacy:
        import spacy
    from gensim.models import CoherenceModel

    path = r"D:\kody\data\korpus\korpus_knihy\ceske\ddskal\LDA"
    stop_words_path = r"D:\kody\data\korpus\korpus_knihy\ceske\stop_words.txt"

    #Loading file with stop words
    stop_words = load_stop_words(stop_words_path)
    #Creating Sparse BOW representation of texts in folder & Frequency dictionary
    if use_spacy:
        model = spacy.load('en_core_web_md')
        my_bow = get_bow(path=path, spacy_model=model, use_spacy=True, verbose=verbose, stop_words=stop_words)
        freq_dict = get_freq_dict(path=path, spacy_model=model, use_spacy=True)
    else:
        my_bow = get_bow(path=path, verbose=verbose, stop_words=stop_words)
        freq_dict = get_freq_dict(path=path)

    #Sorting Frequency dictionary by freq, getting h-points and auto-semantic words for each text in folder
    sorted_freq_dict = sort_freq_dict(freq_dict)
    hp = get_h_point(sorted_freq_dict)
    awords = get_autosemantic_words(sorted_freq_dict)


    if not use_gensim:
        #Performing LDA on BOW to get given number of topics and topic words
        given_num_topics = 4
        x = np.array(my_bow)
        model = LDA(n_components=given_num_topics)
        model.fit_transform(x)

        for topicid, topic in enumerate(model.components_):
            topic_words = my_bow.columns[topic.argsort()[-10:]]
            print("Topic no: ", topicid, "\n", topic_words)

        #Adding additional column to BOW with LDA ascribed topic results
        topic_results = model.transform(x)
        my_bow['Topic Result'] = topic_results.argmax(axis=1)
        print(my_bow)

    else:
        #Creating custom common corpus (from dense BOW text representation), global dictionary
        common_texts = list()
        for text in my_bow.index:
            sparse_bow = my_bow.loc[text]
            text = list()
            for index, word in enumerate(sparse_bow.index):
                freq = sparse_bow[index]
                for i in range(freq):
                    text.append(word)
            common_texts.append(text)
        global_dictionary = Dictionary(list([my_bow.columns]))
        common_corpus = [global_dictionary.doc2bow(text) for text in common_texts]

        #Getting coherence result for different number of topics & deciding on the best number of topics
        coherence_results = dict()
        for num_topics in range(2,10):
            model = gensim.models.LdaModel(common_corpus, id2word=global_dictionary, num_topics=num_topics)
            coherence_model_lda = CoherenceModel(model=model, texts=common_texts, dictionary=global_dictionary)
            coherence_lda = coherence_model_lda.get_coherence()
            coherence_results[num_topics] = coherence_lda
        #Plotting coherence results against number of topics used
        plt.plot(coherence_results.keys(), coherence_results.values())
        plt.show()

    # Splitting my_bow into: reference corpus for text1 and text2 & bow of text1 and text2
    text1, text2 = "Filosofie_vedy_final.txt", "Kundera Milan - Nesmrtelnost.txt"
    new_bow = my_bow.loc[[text1, text2]]
    reference_corpus = my_bow.drop([text1, text2]).sum(axis=0)

    # Creating Reference corpus with relative frequencies
    rf_reference_corpus = reference_corpus.div(reference_corpus.sum(), axis=0)

    # Creating Keyword Bow for text1 and text2 and printing top_n most frequent.
    top_n = 15
    keyword_bow = get_keyword_bow(new_bow, rf_reference_corpus, rf=True)
    print(keyword_bow.loc[text1].nlargest(top_n))
    print(keyword_bow.loc[text2].nlargest(top_n))
