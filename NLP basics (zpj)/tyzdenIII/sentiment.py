import spacy
from spacytextblob.spacytextblob import SpacyTextBlob
import matplotlib.pyplot as plt
import time
import argparse


def timeit(fn):
    def timeit_wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        result = fn(*args, **kwargs)
        end_time = time.perf_counter()
        print(f'\nFunction {fn.__name__}\nProvided args and kwargs:\t{args} {kwargs}:\n\t\tTime elapsed: {end_time-start_time}')
        return result
    return timeit_wrapper


def extract_polarity_from_sents(sents, polarity_data, cumulative_polarity):
    for sent in sents:
        polarity_data[sent] = sent._.blob.polarity
        cumulative_polarity.append(sum(polarity_data.values()) / len(polarity_data))


@timeit
def get_polarity_in_file(file_path, read_by_lines=True, speed_up_pipeline=True):
    if speed_up_pipeline:
        nlp = spacy.load('en_core_web_md', disable=['parser', 'ner'])
        nlp.add_pipe('sentencizer')
    else:
        nlp = spacy.load('en_core_web_md')
    nlp.add_pipe('spacytextblob')
    with open(file_path, 'r', encoding='utf-8') as input_file:
        polarity_data = dict()
        cumulative_polarity = list()
        if read_by_lines:
            for line in input_file:
                doc = nlp(line)
                extract_polarity_from_sents(doc.sents, polarity_data, cumulative_polarity)
        else:
            doc = nlp(input_file.read())
            extract_polarity_from_sents(doc.sents, polarity_data, cumulative_polarity)
    return polarity_data, cumulative_polarity


def write_sentiment_data(polarity_data, cumulative_polarity=list(), output_file_path='output_sentiment_data.txt', sents=False):
    with open(output_file_path, 'w', encoding='utf-8') as output_file:
        header = 'sent\tsentiment_value' if not cumulative_polarity else 'sent\tsentiment_value\tcumulative_polarity'
        output_file.write(header)
        counter = 0
        for sent, value in polarity_data.items():
            if sents:
                string = f'\n{sent}\t{value}'
            else:
                string = f'\n{counter}\t{value}'
            if cumulative_polarity:
                string += f'\t{cumulative_polarity[counter]}'
            output_file.write(string)
            counter += 1
    return


def find_extreme(extreme_fn, data, all_extremes=True):
    if type(data) == dict:
        extreme_key = extreme_fn(data, key=data.get)
        if all_extremes:
            return [k for k,v in data.items() if v == data[extreme_key]]
        return extreme_key
    extreme = extreme_fn(data)
    if all_extremes:
        return [i for i, j in enumerate(data) if j == extreme]
    return data.index(extreme)


def plot_results(*results, show_max=True, show_min=True, all_extremes=True):
    for result in results:
        scatter = plt.subplot(1, 1, 1)
        plottable_result = result.values() if type(result) == dict else result
        scatter.plot(plottable_result)
        if show_max:
            maxs = find_extreme(max, result, all_extremes)
            for mx in maxs:
                max_index = list(result.keys()).index(mx) if type(result) == dict else mx
                scatter.plot(max_index, result[mx], 'or')
        if show_min:
            mins = find_extreme(min, result, all_extremes)
            for mn in mins:
                min_index = list(result.keys()).index(mn) if type(result) == dict else mn
                scatter.plot(min_index, result[mn], 'or')
        plt.show()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="maps sentiment in txt file")
    parser.add_argument("input_file", help="input txt file")
    parser.add_argument("output_file", help="output txt file")
    parser.add_argument("--ex", dest="ex", action="store_const", const=True, default=False, help="plot all extremes")
    parser.add_argument("--sn", dest="sn", action="store_const", const=True, default=False, help="write sentences")
    parser.add_argument("--sp", dest="sp", action="store_const", const=True, default=False, help="speed up process (might affect results)")
    args = parser.parse_args()

    polarity_data, cumulative_polarity = get_polarity_in_file(args.input_file, read_by_lines=args.sp, speed_up_pipeline=args.sp)
    write_sentiment_data(polarity_data, cumulative_polarity, output_file_path=args.output_file, sents=args.sn)
    plot_results(polarity_data, cumulative_polarity, all_extremes=args.ex)
