import unicodedata
from jellyfish import jaro_distance, levenshtein_distance
from perf import tick, tock

dist = levenshtein_distance

MIN_WORD_LEN = 4

# return a list of members of w_list except those of length less than MIN_WORD_LEN
def filter_word_list(w_list):
    new_list = list()
    for w in w_list:
        if len(w) >= MIN_WORD_LEN:
            new_list.append(unicodedata.normalize('NFKD', w).encode('ascii','ignore'))
    return new_list

def getMinDistanceForWord(w, word_list):
    min_dist = float("inf")
    for w2 in word_list:
        d = dist(w,w2)

        if d < min_dist:
            min_dist = d

    return min_dist

def getMinDistanceForWords(w_list1, w_list2):
    min_dist = float("inf")
    for w1 in filter_word_list(w_list1):
        d = getMinDistanceForWord(w1, w_list2)
        if d < min_dist:
            min_dist = d
    return min_dist
