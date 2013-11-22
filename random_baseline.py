import web
import random
import time

def policy(state, theta):
	'''Returns an action (element, action info.)'''

	print state

	return web.Action(random.choice(state)['element'], 'click')

try:
	driver = web.start("http://www.hipmunk.com/flights-search")

	command = 'click on search'
	action = policy(web.build_state(command, driver), None)
	action.perform(driver, dry=True)

	time.sleep(15)
finally:
	driver.quit()