import web
import random
import time
import numpy as np

def policy(state, theta):
	'''Returns an action (element, action info.)'''

	actions = state.enumerate_actions()
	print '%d actions' % len(actions)

	right_button = [a for a in actions if a.type == 'click' and 'frontbox-search-button' in a.features['class_list']]
	right_button = right_button[0]

	action, score, probs = state.get_action_probs(actions, theta)
	print 'Chose', action, 'with score', score

	print action.features
	print state.phi_dot_theta(action, theta, verbose=True), probs[action]

	print right_button.features
	print state.phi_dot_theta(right_button, theta, verbose=True), probs[right_button]

	return action

try:
	driver = web.start("http://www.hipmunk.com/flights-search")

	'''[
        'text_words_edit',
        'n_children',
        'width',
        'height',
        'sibling_text_words_edit',
        'tagname_edit',
        'typeable',
        'clickable',
        'text_size',
        'has_id',
        'has_class',
        'button_model',
        'relative_x',
        'relative_y'
    ]'''
	#theta = np.zeros(len(web.Action.FEATURE_NAMES))

	theta = [
		-10.0,
		0.0,
		0.0,
		0.0,
		0.0,
		-1.0,
		15.0,
		15.0,
		0.0,
		5.0,
		5.0,
		1.0,
		-1.0,
		-1.0
	]

	command = web.tokenize_command('click on the search button')
	state = web.build_state(driver, command)

	action = policy(state, theta)
	action.perform(driver, dry=True)

	time.sleep(15)
finally:
	driver.quit()
