from selenium import webdriver, selenium
from util.perf import tick, tock
import util.str_util as str_util
import util.seutil as seutil
import sys
import time
import itertools
import random
import math
import scipy.stats as stats
import numpy as np
import json
import copy

GET_FEATURES_JS = "js/get-features.js"
UNDERSCORE_JS = "js/underscore.js"

def tokenize_command(command):
    command = unicode(command, 'utf-8')
    return command.split(' ')

def untokenize_subcommand(sub):
    return ' '.join(sub)

class Action:
    # These are the features used in the numeric representation of the feature
    # vector corresponding to this Action. There are some features from get-features.js
    # and/or extend_and_norm_feature which are dropped from this representation.
    FEATURE_NAMES = [
        'text_words_edit',
        'n_children',
        #'width',
        #'height',
        'sibling_text_words_edit',
        'tagname_edit',
        'typeable',
        #'clickable',
        #'text_size',
        'has_id',
        'has_class',
        'button_model',
        #'relative_x',
        #'relative_y',
        'alreadyInteracted',
        'single_subword',
        'double_subword',
        'big_subword',
        'contains_action_word'
    ]

    def __init__(self, element, atype, features, params=None):
        self.element = element
        self.type = atype
        self.params = params
        self.features = features

    def perform(self, driver, dry=False):

        driver.execute_script('''
            var elem = arguments[0]
            elem.setAttribute("x-WebtalkInteracted", "1")
            ''', self.element)

        if dry:
            seutil.highlight(driver, self.element, opacity=0.5)
            return

        if self.type == 'click':
            self.element.click()
        elif self.type == 'type':
            self.element.clear()
            self.element.send_keys(untokenize_subcommand(self.params))

    def as_numeric_vector(self):
        return tuple([
            self.features[k] for k in self.FEATURE_NAMES
        ])

    def __repr__(self):
        classes = self.element.get_attribute("class")
        if self.params == None:
            return '<Action %s on %s#%s.%s>' % (self.type, self.features['tagname'], self.features['id'], classes)
        return '<Action %s on %r, %s#%s.%s>' % (self.type, self.params, self.features['tagname'], self.features['id'], classes)


class State:
    def __init__(self, command, features):
        self.command = command
        self.features = features

    def _subcommands(self):
        if hasattr(self, '_subcommand_cache'):
            return self._subcommand_cache

        subcommands = []
        for window_size in range(1, len(self.command)+1):
            for i in range(0, len(self.command)-window_size+1):
                subcommands.append(self.command[i:i+window_size])

        self._subcommand_cache = subcommands
        return self._subcommand_cache

    def enumerate_actions(self):
        actions = []
        for el in self.features:
            if el['typeable'] == 1:
                for subwords in self._subcommands():
                    _el = copy.copy(el)
                    _el = extend_subword_features(_el, subwords, self.command)
                    actions.append(Action(_el['element'], 'type', _el, params=subwords))
            else:
                _el = copy.copy(el)
                _el = extend_subword_features(_el, None, self.command)
                actions.append(Action(_el['element'], 'click', _el))
        return actions

    def phi_dot_theta(self, action, theta, verbose=False):
        phi = action.as_numeric_vector()


        if verbose:
            print 'Product:'
            print np.dot(phi, theta)
            print action.features['sibling_text_words']
            for i,f in enumerate(Action.FEATURE_NAMES):
                print '\t%+.4f\t%s\t%.4f * %.4f' % (phi[i]*theta[i], f, phi[i], theta[i])


        return np.dot(phi, theta)

    def get_action_probs(self, actions, theta):
        '''Chooses the modal action'''
        products = {}

        normalization = 0.0
        for action in actions:
            v = math.exp(self.phi_dot_theta(action, theta))
            products[action] = v
            normalization += v

        max_v, max_action = None, []
        for action in products:
            products[action] /= normalization
            if max_v == None or products[action] >= max_v:
                if max_v == products[action]:
                    max_action.append(action)
                else:
                    max_action = [action]

                max_v = products[action]

        return random.choice(max_action), max_v, products

def start(url):
    driver = seutil.get_driver()
    driver.get(url)
    return driver


ELEMENT_DATA = json.load(open('element_sizes.json', 'rb'))

BUTTON_SIZE_KDE = stats.gaussian_kde(np.transpose(np.array(
    [x[1:] for x in ELEMENT_DATA if x[0]]
)))

ELEMENT_SIZE_KDE = stats.gaussian_kde(np.transpose(np.array(
    [x[1:] for x in ELEMENT_DATA]
)))

_LandH_cache = {}
def likelihood_and_marginal(w, h):
    if (w,h) in _LandH_cache:
        return _LandH_cache[(w,h)]
    #likelihood_button = (stats.norm.cdf(h+1, loc=my, scale=sy) - stats.norm.cdf(h, loc=my, scale=sy)) * (stats.norm.cdf(w+1, loc=mx, scale=sx) - stats.norm.cdf(w, loc=mx, scale=sx))
    _LandH_cache[(w,h)] = (
        BUTTON_SIZE_KDE.integrate_box([w,h], [w+1,h+1]),
        ELEMENT_SIZE_KDE.integrate_box([w,h], [w+1,h+1])
    )
    return _LandH_cache[(w,h)]

def extend_subword_features(feature, subwords, command):
    if subwords is None:
        subwords = []
    feature['single_subword'] = 1 if len(subwords) == 1 else 0
    feature['double_subword'] = 1 if len(subwords) == 2 else 0
    feature['big_subword'] = 1 if len(subwords) > 2 else 0

    action_words = 'press hit click type enter put'.split(' ')
    feature['contains_action_word'] = 1 if any([w.lower() in action_words for w in subwords]) else 0

    return feature

def extend_and_norm_feature(element, feature, command, num_elems):
    feature['element'] = element
    
    #feature['tagname_edit'] = str_util.get_normed_dist_for_words(command, [feature['tagname']])
    #feature['text_words_edit'] = str_util.get_normed_dist_for_words(command, feature['text_words'])
    #feature['sibling_text_words_edit'] = str_util.get_normed_dist_for_words(command, feature['sibling_text_words'])
    
    feature['tagname_edit'] = str_util.get_mean_distance_of_words(command, [feature['tagname']])
    feature['text_words_edit'] = str_util.get_mean_distance_of_words(command, feature['text_words'])
    feature['sibling_text_words_edit'] = str_util.get_mean_distance_of_words(command, feature['sibling_text_words'])


    feature['n_children'] = 1 - float(feature['n_children']) / num_elems

    w,h = feature['width'], feature['height']
    mx, my, sx, sy = 54.611, 25.206, 43.973, 6.467

    prior = 0.02
    likelihood_button, marginal = likelihood_and_marginal(w, h)

    feature['button_model'] = ((likelihood_button * prior) / marginal) - .147

    # relative x and y can  be more than 1 because things can be beyond the edge of the window
    # so nudge things to be between -1 and 1
    feature['relative_x'] = np.arctan(1 * (feature['relative_x'] + 0.5)) / (np.pi / 2)
    feature['relative_y'] = np.arctan(1 * feature['relative_y']) / (np.pi / 2)

    # new on page?
    # position (relative to last action?)
    # color
    # relative tab index
    # text specificity
    return feature

def extract(driver, command):
    driver.execute_script(open(UNDERSCORE_JS).read())
    features, tree = driver.execute_script(open(GET_FEATURES_JS).read())
    features = [extend_and_norm_feature(f[0], f[1], command, len(features)) for f in features]

    return features, tree

def build_state(driver, command):
    features, tree = extract(driver, command)
    return State(command, features)


