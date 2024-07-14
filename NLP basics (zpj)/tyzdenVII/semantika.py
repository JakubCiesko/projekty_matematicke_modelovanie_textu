import scipy.spatial.distance
import numpy as np
import gensim
import math
from matplotlib import pyplot as plt
from sklearn.manifold import MDS
from scipy.spatial.kdtree import KDTree
import argparse

#empty_embedding = np.arrray([None] * len(model['dog'])) (nahradit )
def get_word_embedding(word: str, model):
    result = model[word] if word in model else np.arrray([None] * len(model['dog']))
    return result


def create_PDM(positions):
    distances = scipy.spatial.distance.pdist(positions)
    return scipy.spatial.distance.squareform(distances)


def MDS_reduction(data, n_components=2):
    embedding = MDS(n_components=n_components)
    mds_reduced_data = embedding.fit_transform(data)
    return mds_reduced_data


def plot_data(data, labels, query_word=None):
    x = [d[0] for d in data]
    y = [d[1] for d in data]
    plt.scatter(x, y)
    #colors = ['red' if query_word == word else 'black' for word in labels]
    #plt.annotate(labels, (x, y), colors)        #annotate alebo text
    for i, txt in enumerate(labels):
        color = 'black'
        if query_word and txt == query_word:
            color = 'red'
        plt.annotate(txt, (x[i], y[i]), color=color)
    plt.show()

#returny a if-else
def get_words_embeddings(words, model, np_array=False, remove_none=False):
    if np_array:
        words_embeddings = np.array([get_word_embedding(word, model) for word in words])
    else:
        words_embeddings = {word: get_word_embedding(word, model) for word in words}
    if remove_none:
        if not np_array:
            return {k: v for k, v in words_embeddings.items() if v[0] is not None}
        rows = np.where(words_embeddings[:, 0] is not None)
        return words_embeddings[rows]
    return words_embeddings


def get_average_embedding(embeddings, axis=0):
    embeddings = np.array(embeddings)
    rows = np.where(embeddings[:, 0] is not None)
    return np.mean(embeddings[rows], axis=axis)


#kdstrom vstupuje sem
def find_closest_word(query_word, text, model, k=10, remove_none=False):
    words = text.split()
    query_word_embedding = get_word_embedding(query_word, model)
    words_embeddings = get_words_embeddings(words, model, remove_none=remove_none)
    tree = KDTree(list(words_embeddings.values()))
    d, i = tree.query(query_word_embedding, k=min(len(words_embeddings), k))
    return [words[index] for index in i]


def euclidean_distance(a, b):
    return math.sqrt(sum((a-b)**2))


#robi aj KDstrom (ale pre kosinus treba zmenit embeddingy vydelenim L2normou)
def find_n_closest(query_word_embedding, embeddings, n=3, distance_method=euclidean_distance):
    dst = [distance_method(query_word_embedding, emb) for emb in embeddings.values()]
    dists = sorted(dst)
    inds = [dst.index(d) for d in dists[:n]]
    wrds = list()
    for ind in inds:
        wrds.append(list(embeddings.keys())[ind])
    return wrds


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='BOW program')
    parser.add_argument('binary_gensim_model_path')
    parser.add_argument('words_string')
    parser.add_argument('query_word')
    args = parser.parse_args()
    """path = "D:\\kody\\python\\upol\\du\\zjp\\bow_tfidf\\GoogleNews-vectors-negative300.bin"
    model = gensim.models.keyedvectors.load_word2vec_format(path, binary=True)
    words = ["dog", "cat", "bird", "wall", "brick", "house", "hawk", "tiger"]
    query_word = 'eagle'"""
    model = gensim.models.keyedvectors.load_word2vec_format(args.binary_gensim_model_path, binary=True)
    words = args.words_string.split()
    query_word = args.query_word
    query_word_embedding = get_word_embedding(query_word, model)
    words_embeddings = get_words_embeddings(words, model)
    print(find_n_closest(query_word_embedding, words_embeddings))
    words_embeddings[query_word] = query_word_embedding
    reduced_embeddings = MDS_reduction(list(words_embeddings.values()))
    print(find_closest_word(query_word, ' '.join(words), model))
    plot_data(reduced_embeddings, list(words_embeddings.keys()), query_word=query_word)
