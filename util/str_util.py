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
    if len(text) == 0:
        return 0.0

    mean_distance = sum([get_min_distance_for_word(w, cmd) for w in text]) / float(len(text))

    norm_f = max([len(word) for word in cmd + text])
    return 1.0 - (mean_distance/norm_f)

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

import re, string, itertools
from collections import defaultdict
def new_dist(needle, haystack):
    #needle = [w.strip(string.punctuation) for w in re.split('\s+',needle)]
    #haystack = [w.strip(string.punctuation) for w in re.split('\s+',haystack)]

    needle = [w.lower() for w in needle]
    haystack = [w.lower() for w in haystack]

    if len(needle) == 0 or len(haystack) == 0:
        return 0

    needles = set(needle)
    needles_appear = defaultdict(list)
    k = 0
    for i,w in enumerate(haystack):
        if w in needles:
            needles_appear[w].append(i)
            k += 1

    #print needle
    #print haystack
    #print needles_appear

    # unigram terms
    score = float(k)

    # pair terms: for each pair of needle words and each pair of their appearances,
    # add the inverse square of their appearance distance
    for n1, n2 in itertools.permutations(needle, 2):
        if n1 == n2:
            continue
        for p1,p2 in itertools.combinations(needles_appear[n1] + needles_appear[n2], 2):
            d = 1.0 / abs(p1-p2)**2
            score += d
            #print n1, n2, d

    return score / len(haystack)

if __name__ == '__main__':
    '''
    q = 'In the Wake of Disaster'

    print 'TIGHT'
    tight = new_dist(q, 'Exxon Valdez: In the Wake of Disaster')
    print 'DISORDER'
    disorder = new_dist(q, 'Exxon Valdez: Wake Disaster')
    print 'CONTEXT'
    context = new_dist(q, 'RETRO REPORT Exxon Valdez: In the Wake of Disaster By HENRY FOUNTAIN In 1989, a tanker ran aground off the coast of Alaska, causing one of the worst oil spills in United States history. Nearly 25 years later, the lessons continue to resonate.')
    print 'OUT'
    out = new_dist(q, 'A final agreement on a policy bill would strengthen protections for victims of sexual assault in the military and keep open the prison at Guantanamo Bay.')

    print tight
    print disorder
    print context
    print out
    '''

    print new_dist('type Boston in the from box'.split(), ['From', 'City', 'or', 'Airport'])
