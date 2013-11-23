from selenium import webdriver, selenium
from util.perf import tick, tock
import util.seutil as seutil
import sys
import time
import scipy.stats

get_features_js = "js/get-features.js"
underscore_js = "js/underscore.js"

driver = seutil.get_driver()
#driver = webdriver.phantomjs.webdriver.WebDriver()
#driver = webdriver.Firefox()

tick('Loading page')
driver.get("http://www.hipmunk.com/flights-search")
tock()


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

    print 'click!!'
    time.sleep(15)

    tick('Loading underscore')
    driver.execute_script(open(underscore_js).read())
    tock()

    tick('JS enumeration')
    extract = driver.execute_script(open(get_features_js).read())
    tock()

    features = extract['features']

    print extract['tree']

    features = [extend_feature(*f) for f in features]
    
    print 'Got %d feature vectors' % len(features)
    #time.sleep(100)
finally:
    #time.sleep(15)
    driver.quit()
