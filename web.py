from selenium import webdriver, selenium
from util.perf import tick, tock
import util.seutil as seutil
import sys
import time
import itertools
import random
import math

GET_FEATURES_JS = "js/get-features.js"
UNDERSCORE_JS = "js/underscore.js"

def tokenize_command(command):
    return command.split(' ')

def untokenize_subcommand(sub):
    return ' '.join(sub)

class Action:
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

    def __repr__(self):
        if self.params == None:
            return '<Action %s on %r>' % (self.type, self.element)
        return '<Action %s on %r, %r>' % (self.type, self.element, self.params)

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
        # TODO:
            # filter out typing on the many elements that don't support it
            # (since that's a very limited set of HTML element types)
        actions = []
        for el in self.features:
            if el['typeable'] == 1:
                for subwords in self._subcommands():
                    actions.append(Action(el['element'], 'type', el, params=subwords))
            else:
                actions.append(Action(el['element'], 'click', el))
        return actions

    def phi_dot_theta(self, action, theta):
        return random.random()

    def choose_action(self, actions, theta):
        '''Chooses the modal action'''
        products = {}

        normalization = 0.0
        for action in actions:
            v = math.exp(self.phi_dot_theta(action, theta))
            products[action] = v
            normalization += v

        max_v, max_action = None, None
        for action in products:
            products[action] /= normalization
            if max_v == None or products[action] > max_v:
                max_v = products[action]
                max_action = action

        return max_action

def start(url):
    driver = seutil.get_driver()
    driver.get(url)
    return driver

def extend_feature(element, feature):
    feature['element'] = element

    #tagname: elem.tagName,
    #text_words: Features.getTextWords(elem),
    #sibling_text_words: Features.getSiblingTextWords(elem),

    #feature['tagname'] = 
    #feature['text_words'] = 
    #feature['sibling_text_words'] = 

    return feature

def extract(driver, command):
    driver.execute_script(open(UNDERSCORE_JS).read())
    features, tree = driver.execute_script(open(GET_FEATURES_JS).read())
    features = [extend_feature(*f, command) for f in features]

    return features, tree

def build_state(driver, command):
    features, tree = extract(driver, command)
    return State(command, features)

    