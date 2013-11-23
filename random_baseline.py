import web
import random
import time
import numpy as np

def policy(state, theta):
	'''Returns an action (element, action info.)'''

	actions = state.enumerate_actions()
	print '%d actions' % len(actions)

	action, score = state.choose_action(actions, theta)
	print 'Chose', action, 'with score', score

	return action

try:
	driver = web.start("http://www.hipmunk.com/flights-search")

	theta = np.zeros(len(web.Action.FEATURE_NAMES))

	command = web.tokenize_command('click on the search button')
	state = web.build_state(driver, command)

	action = policy(state, theta)
	action.perform(driver, dry=True)

	time.sleep(15)
finally:
	driver.quit()