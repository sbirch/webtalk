from selenium import webdriver, selenium
from util.perf import tick, tock
import util.seutil as seutil
import sys
import time
import scipy.stats

GET_FEATURES_JS = "js/get-features.js"
UNDERSCORE_JS = "js/underscore.js"

class Action:
    def __init__(self, element, _type, params=None):
        self.element = element
        self.type = _type
        self.params = params
    def perform(self, driver, dry=False):
        if self.type == 'click':
            if dry:
                seutil.highlight(driver, self.element, opacity=0.5)
            else:
                self.element.click()

def extend_feature(element, feature):
    feature['element'] = element
    return feature

def start(url):
    driver = seutil.get_driver()
    driver.get(url)
    return driver

def get_features(driver):
    driver.execute_script(open(UNDERSCORE_JS).read())
    features = driver.execute_script(open(GET_FEATURES_JS).read())
    return [extend_feature(*f) for f in features]

def build_state(driver, command):
    return (command, get_features(driver))