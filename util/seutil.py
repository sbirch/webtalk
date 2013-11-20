from selenium import webdriver
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains

def get_driver():
	driver = webdriver.Chrome(executable_path="./chromedriver")
	driver.set_window_size(1400, 900)
	driver.set_window_position(200, 50)

	return driver

def plog(driver, log_type='browser'):
	logs = driver.get_log(log_type)
	for log in logs:
		print log['level'], log['message']

def highlight_element(driver, element):
	try:
		driver.find_element_by_id("selenium-highlight-dhq8gcnaasx0")
	except NoSuchElementException:
		driver.execute_script('''
			var e = document.createElement('div');
			e.id = 'selenium-highlight-dhq8gcnaasx0';
			e.style.position = 'absolute';
			e.style.backgroundColor = 'rgba(255, 0, 0, 0.5)';
			e.style.zIndex = '999999999999999';
			e.style.border = '3px dashed #000';
			e.style.pointerEvents = 'none';
			document.body.appendChild(e);
		''')

	top = element.location['y']
	left = element.location['x']
	width = element.size['width']
	height = element.size['height']

	driver.execute_script('''
			var e = document.getElementById('selenium-highlight-dhq8gcnaasx0');
			e.style.top = '%dpx';
			e.style.left = '%dpx';
			e.style.width = '%dpx';
			e.style.height = '%dpx';
		''' % (top, left, width, height))

	print 'Overlaid %dx%d at (%d,%d)' % (width, height, left, top)


def type_on_element(driver, element, content):
	element.send_keys(content)

def hover_on_element(driver, element):
	ActionChains(driver).move_to_element(element).perform()

def click_on_element(driver, element):
	element.click()

def find_visible_element(driver, selector):
	candidates = driver.find_elements_by_css_selector(selector)
	candidates = [x for x in candidates if x.is_displayed()]

	assert len(candidates) == 1

	return candidates[0]