from selenium import webdriver, selenium
import sys

import time

from util.perf import tick, tock

get_features_js = "js/get-features.js"
underscore_js = "js/underscore-min.js"

driver = webdriver.phantomjs.webdriver.WebDriver() #seutil.get_driver()
#driver = webdriver.Firefox()

driver.get("http://www.hipmunk.com/flights-search")

try:
    #tick('* selector')
    #elements = driver.find_elements_by_css_selector('*')
    #tock()

    #print 'Got %d elements' % len(elements)

    tick('JS enumeration')
    driver.execute_script(open(underscore_js).read())
    features = driver.execute_script(open(get_features_js).read())
    tock()

    print features
    print 'Got %d feature vectors' % len(features)

finally:
    time.sleep(15)
    driver.quit()
