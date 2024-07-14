import os
import pandas
import math
import matplotlib.pyplot as plt
import argparse
import spacy


def get_global_dict(path, use_spacy=False):
    """Creates global dictionary from all txt files in folder. Returns python dict."""
    global_dictionary = dict()
    for file in os.listdir(path=path):
        if file.endswith('.txt'):
            text_file = file
            file_path = os.path.join(path, text_file)
            with open(file_path, 'r', encoding='utf-8') as input_file:
                for line in input_file:
                    if not use_spacy:
                        words = line.split()
                        for word in words:
                            word = word.lower()
                            if word not in global_dictionary:
                                global_dictionary[word] = len(global_dictionary)
                    else:
                        line_doc = nlp(line)
                        for token in line_doc:
                            word = token.text.lower()
                            if word not in global_dictionary:
                                global_dictionary[word] = len(global_dictionary)

    return global_dictionary


def get_bow(path, verbose=False, use_spacy=False):
    """Creates Bag of Words representation of txt files in folder."""
    if verbose:
        print('Creating global dictionary')
    global_dict = get_global_dict(path, use_spacy=use_spacy)
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
                            text_vector[global_dict[word]] += 1
                    else:
                        line_doc = nlp(line)
                        for token in line_doc:
                            word = token.text.lower()
                            text_vector[global_dict[word]] += 1
            bow.loc[file] = text_vector
    return bow


def binarize(df, given_threshold=2):
    df = 1 * (df >= given_threshold)
    return df


def threshold_binarization(bow, threshold):
    """Binarizes BoW representation using threshold value. Returns pandas dataframe with binarized values (1 or 0). Non-destructive"""
    bow_copy = bow.copy()
    return binarize(bow_copy, threshold)


def threshold_binarization(bow, threshold: int):
    """Binarizes BoW representation using threshold value. Returns pandas dataframe with binarized values (1 or 0). Non-destructive"""
    binarized_bow = bow.copy()
    binarized_bow = binarized_bow.apply(lambda x: x > threshold).astype('int8')
    binarized_bow = binarized_bow.loc[:, (binarized_bow != 0).any(axis=0)]
    return binarized_bow


def scree_plot(bow, threshold: int):
    """Returns scree plot of binarized BoW"""
    results = dict()
    scree = plt.subplot(1, 1, 1)
    for i in range(threshold+1):
        results[i] = len(threshold_binarization(bow, i).columns)
    x, y = results.keys(), results.values()
    scree.plot(x, y, 'or')
    scree.plot(x, y)
    return scree


def tf_idf(bow, word, text):
    """Returns TF-IDF score of word in BOW"""
    freq = bow[word][text]
    no_of_documents = len(bow.index)
    no_of_documents_with_word = sum(bow[word].apply(lambda x: x > 0))
    tfidfscore = freq*math.log10(no_of_documents/no_of_documents_with_word)
    return tfidfscore


def get_tfidfbow(bow, threshold=0, verbose=False):
    """Transforms BoW to TF-IDF BoW. Returns BoW with TF-IDF scores instead of frequencies."""
    if verbose:
        print('\nCreating TF-IDF Bag of Words out of sparse Bag of Words\n')
    bow_tfidfsc = pandas.DataFrame(columns=bow.columns, index=bow.index)
    texts = bow.index
    for text in texts:
        if verbose:
            print(f'Processing file: {text}')
        for word in bow:
            bow_tfidfsc.loc[text, word] = tf_idf(bow, word, text)
    return bow_tfidfsc.loc[:, (bow_tfidfsc > threshold).any(axis=0)]


def calculate_zscore(bow):
    """Calculates Z-scores of words in BoW. Return pandas dataframe with these values."""
    return (bow - bow.mean())/bow.std()


def pca_reduction(data, information_ratio=0.9):
    """Reduces data using PCA to given informaiton ratio. non-destructive"""
    pca_reduced_data, n = None, 0
    for n in range(1, len(mydata)):
        pca = PCA(n_components=n)
        pca_reduced_data = pca.fit_transform(data)
        results = sum(pca.explained_variance_ratio_)
        if results > information_ratio:
            break
    return pca_reduced_data, n


def pca_reduction(data, information_ratio=0.9):
    """Reduces data using PCA to given informaiton ratio. non-destructive"""
    pca = PCA(information_ratio)
    pca_reduced_data = pca.fit_transform(data)
    return pca_reduced_data


def pca_reductionN(data, n):
    """Reduces data using PCA to given number of components"""
    pca = PCA(n_components=n)
    pca_reduced_data = pca.fit_transform(data)
    return pca_reduced_data


def jaccard(a, b):
    """Calculates Jaccard index"""
    a = set(a)
    b = set(b)
    return len(a.intersection(b))/len(a.union(b))


def manhattan_distance(a, b):
    """Calculates manhatan distance between vectors a, b"""
    return sum(abs(a-b))


def euclidean_distance(a, b):
    """Calculates euclidean distance between vectors a, b"""
    return math.sqrt(sum((a-b)**2))


def cosine_distance(a, b):
    """Calculates cosine dissimilarity between vectors a, b"""
    return 1 - np.dot(a/np.linalg.norm(a), b/np.linalg.norm(b))


def process_data(input_folder_path, binarize, show, n, z_score, use_spacy, verbose):
    results = {'bow': None, 'tfidfbow': None, 'binarized_bow': None, 'bow_z_score': None}
    bow = get_bow(input_folder_path, use_spacy=use_spacy, verbose=verbose)
    tfidfbow = get_tfidfbow(bow, verbose=verbose)
    results['bow'] = bow
    results['tfidfbow'] = tfidfbow
    preresult = list()
    if binarize:
        if verbose:
            print(f'\nBinarization of Bag of Words (threshold = {n})\n')
        binarized_bow = threshold_binarization(bow, n)
        preresult.append(binarized_bow)
        results['binarized_bow'] = binarized_bow
        scree_plot(bow, n)
        if show:
            plt.show()
    if z_score:
        if verbose:
            print('Calculating z_score')
        z_scorebow = calculate_zscore(tfidfbow)
        preresult.append(z_scorebow)
        results['bow_z_score'] = z_scorebow
    #results = [bow, tfidfbow] + preresult if (binarize or z_score) else [bow, tfidfbow]
    return results


def write_data(output_folder_path, data):
    """Writes data to output file in csv format"""
    for result_type, result in data.items():
        if result is not None:
            file_name = result_type + '.txt'
            output_file_path = os.path.join(output_folder_path, file_name)
            result.to_csv(output_file_path)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='BOW program')
    parser.add_argument('input_folder_path')
    parser.add_argument('output_folder_path')
    parser.add_argument('-b', '--binarize', action='store_const', const=True, default=False)
    parser.add_argument('-p', '--plot', action='store_const', const=True, default=False)
    parser.add_argument('-n', '--threshold', const=5, default=5, type=int, nargs='?')
    parser.add_argument('-z', '--z_score', action='store_const', const=True, default=False)
    parser.add_argument('-s', '--use_spacy', action='store_const', const=True, default=False)
    parser.add_argument('-v', '--verbose', action='store_const', const=True, default=False)
    args = parser.parse_args()

    if args.use_spacy:
        nlp = spacy.load('en_core_web_md')

    input_folder_path = args.input_folder_path
    output_folder_path = args.output_folder_path

    results = process_data(input_folder_path=input_folder_path,
                           binarize=args.binarize,
                           show=args.plot,
                           n=args.threshold,
                           z_score=args.z_score,
                           use_spacy=args.use_spacy,
                           verbose=args.verbose)

    write_data(output_folder_path, results)



