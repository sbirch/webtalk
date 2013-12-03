import unicodedata
#from jellyfish import jaro_distance, levenshtein_distance
from perf import tick, tock
import Levenshtein

dist = Levenshtein.distance

MIN_WORD_LEN = 4

# return a list of members of w_list except those of length less than MIN_WORD_LEN
def filter_word_list(w_list):
    new_list = list()
    for w in w_list:
        if len(w) >= MIN_WORD_LEN:
            new_list.append(w)
    return new_list

def get_normed_dist_for_word(w, word_list):
    norm_f = max(len(w),max([len(word) for word in word_list]))
    return 1 - float(get_min_distance_for_word(w, word_list)) / norm_f

def get_normed_dist_for_words(w_list1, w_list2):
    norm_f = max([len(word) for word in w_list1 + w_list2])
    return  1 - float(get_min_distance_for_words(w_list1, w_list2)) / norm_f

def get_mean_distance_of_words(cmd, text):
    return sum([get_min_distance_for_word(w, cmd) for w in text]) / float(len(text))

def get_min_distance_for_word(w, word_list):
    min_dist = len(w)
    for w2 in word_list:
        d = dist(w.lower(),w2.lower())

        if d < min_dist:
            min_dist = d

    return min_dist

def get_min_distance_for_words(w_list1, w_list2):
    min_dist = float("inf")
    for w1 in filter_word_list(w_list1):
        d = get_min_distance_for_word(w1, w_list2)
        if d < min_dist:
            min_dist = d
    return min_dist
