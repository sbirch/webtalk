from selenium import webdriver, selenium
import sys

print sys.path
import time

from util.perf import tick, tock

get_features_js = "js/get-features.js"

driver = webdriver.Firefox() #seutil.get_driver()

driver.get("http://www.hipmunk.com/flights-search")

try:

	#tick('* selector')
	#elements = driver.find_elements_by_css_selector('*')
	#tock()

    #print 'Got %d elements' % len(elements)

	tick('JS enumeration')
	features = driver.execute_script(open(get_features_js).read())
	tock()

	print 'Got %d feature vectors' % len(features)

finally:
	time.sleep(15)
	driver.quit()
