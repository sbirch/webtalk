from selenium import webdriver, selenium
from util.perf import tick, tock
import util.str_util as str_util
import util.seutil as seutil
import sys
import time
import itertools
import random
import math
import numpy as np

GET_FEATURES_JS = "js/get-features.js"
UNDERSCORE_JS = "js/underscore.js"

def tokenize_command(command):
    command = unicode(command, 'utf-8')
    return command.split(' ')

def untokenize_subcommand(sub):
    return ' '.join(sub)

class Action:
    FEATURE_NAMES = [
        'text_words_edit',
        'n_children',
        'width',
        'height',
        'sibling_text_words_edit',
        'tagname_edit',
        'typeable',
        'clickable',
        'text_size'
    ]

    def __init__(self, element, atype, features, params=None):
        self.element = element
        self.type = atype
        self.params = params
        self.features = features

    def perform(self, driver, dry=False):
        if dry:
            seutil.highlight(driver, self.element, opacity=0.5)
            return

        if self.type == 'click':
            self.element.click()
        elif self.type == 'type':
            self.element.send_keys(untokenize_subcommand(self.params))

    def as_numeric_vector(self):
        return tuple([
            self.features[k] for k in self.FEATURE_NAMES
        ])

    def __repr__(self):
        if self.params == None:
            return '<Action %s on %s#%s>' % (self.type, self.features['tagname'], self.features['id'])
        return '<Action %s on %r, %s#%s>' % (self.type, self.params, self.features['tagname'], self.features['id'])

class State:
    def __init__(self, command, features):
        self.command = command
        self.features = features

    def _subcommands(self):
        if hasattr(self, '_subcommand_cache'):
            return self._subcommand_cache

        subcommands = []
        for window_size in range(1, len(self.command)+1):
            #print 'window', window_size
            for i in range(0, len(self.command)-window_size+1):
                #print 'range', i, i+window_size, self.command[i:i+window_size]
                subcommands.append(self.command[i:i+window_size])

        self._subcommand_cache = subcommands
        return self._subcommand_cache

    def enumerate_actions(self):
        actions = []
        for el in self.features:
            if el['typeable'] == 1:
                for subwords in self._subcommands():
                    actions.append(Action(el['element'], 'type', el, params=subwords))
            else:
                actions.append(Action(el['element'], 'click', el))
        return actions

    def phi_dot_theta(self, action, theta):
        phi = action.as_numeric_vector()
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

def extend_feature(element, feature, command):
    feature['element'] = element

    feature['tagname_edit'] = str_util.get_min_distance_for_words(command, feature['tagname'])
    feature['text_words_edit'] = str_util.get_min_distance_for_words(command, feature['text_words'])
    feature['sibling_text_words_edit'] = str_util.get_min_distance_for_words(command, feature['sibling_text_words'])

    return feature

def extract(driver, command):
    driver.execute_script(open(UNDERSCORE_JS).read())
    features, tree = driver.execute_script(open(GET_FEATURES_JS).read())
    features = [extend_feature(f[0], f[1], command) for f in features]

    return features, tree

def build_state(driver, command):
    features, tree = extract(driver, command)
    return State(command, features)


