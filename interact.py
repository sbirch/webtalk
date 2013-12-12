import numpy as np
import web
import policy_gradient
import random
import readline
from data import gen_docs


if False: # train a new vector
	docs = gen_docs.get_all_docs("data/sendacard_corpus.tsv")
	random.shuffle(docs)
	docs = docs[:25]
	theta = policy_gradient.policy_gradient(docs)
else:
	# Daedalus vector
	#theta = [+4.3172, +3.3282, +3.8092, -2.6218, +7.9710, +4.0238, -0.0002, +1.3441, +5.7676, +7.4365]
	
	# Best of eval
	theta = [4.1303645925709178, 2.4226422308579605, 5.3969554359870386, -3.1853219158721493, 6.6798106812814826, 3.1624395829369849, 0.00021545227788204581, 1.1430678550057314, 5.3933282823027868, 7.4415914266213221]


try:
	driver = web.start("http://localhost:8000")

	cmd = ""
	while cmd != "QUIT":
	    cmd = raw_input('> ')
	    state = web.build_state(driver, web.tokenize_command(cmd))

	    actions = state.enumerate_actions()

	    action, best_score, probs = state.get_action_probs(actions, theta)

	    print "Performing... ", action
	    state.phi_dot_theta(action, theta, True)

	    if False:
	    	correct = [a for a in actions if a.type == 'click' and a.element.get_attribute('x-wtid') == 'continue' and a.params is None][0]
	    	print 'Correct action was:', correct
	    	state.phi_dot_theta(correct, theta, True)

	    action.perform(driver, dry=False)
finally:
	driver.quit()

