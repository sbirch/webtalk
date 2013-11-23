from selenium import webdriver, selenium
from util.perf import tick, tock
import util.seutil as seutil
import sys
import time
import scipy.stats
from numpy import array
from util import str_util

get_features_js = "js/get-features.js"
underscore_js = "js/underscore.js"

driver = seutil.get_driver()
#driver = webdriver.phantomjs.webdriver.WebDriver()
#driver = webdriver.Firefox()

tick('Loading page')
driver.get("http://www.hipmunk.com/flights-search")
tock()

# convert an object from the javascript to an Array of numerical features
def web_obj_to_vector(obj):
    return array([obj["width"],
                obj["height"],
                obj["clickable"],
                obj["typeable"],
                obj["tagname_edit"],
                str_util.getMinDistanceForWords(f["text_words"], words),
                str_util.getMinDistanceForWords(f["sibling_text_words"], words),
                obj["text_size"],
                obj["n_children"],
                obj["tab_index"],
                str_util.getMinDistanceForWord(f["id"], words)])
                #str_util.getMinDistanceForWords(f["class_list"], words)])
def extend_feature(element, feature):
    feature['element'] = element

    w, h = feature['width'], feature['height']
    #feature['button_probability'] = scipy.stats()

    return feature

try:
    #tick('* selector')
    #elements = driver.find_elements_by_css_selector('*')
    #tock()

    #print 'Got %d elements' % len(elements)

    tick('Loading underscore')
    driver.execute_script(open(underscore_js).read())
    tock()

    tick('JS enumeration')
    features = driver.execute_script(open(get_features_js).read())
    tock()

    features = [extend_feature(*f) for f in features]
    words = ["click", "the", "search", "button"]

    tick('feature vectors')
    for f in features:
        print f["text"]
        print web_obj_to_vector(f)
    tock()




    print 'Got %d feature vectors' % len(features)
    #time.sleep(100)
finally:
    #time.sleep(15)
    driver.quit()
