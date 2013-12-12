import numpy as np
import web
import policy_gradient
import random
from data import gen_docs

docs = gen_docs.get_all_docs("data/sendacard_corpus.tsv")
random.shuffle(docs)
docs = docs[:25]

#theta = policy_gradient.policy_gradient(docs)

theta = [+4.3172, +3.3282, +3.8092, -2.6218, +7.9710, +4.0238, -0.0002, +1.3441, +5.7676, +7.4365]

#theta = [  1.36530115e+00,   6.02365845e-01 ,  8.20258919e+00,  -1.47179863e+00, 5.63042785e+00,   1.56722528e+00,   3.25862791e-03,   2.65489344e-01, 5.05448778e+00,   6.13476141e+00]

# awesome one from dec 9
#theta = [7.20747115e+00,  1.69038401e+00,  8.53217940e+00,  -1.59279985e+00, \
#         3.18936265e+00,  3.28663595e+00,  6.51425808e-03,   6.79447331e-01, \
#         6.11002876e+00,  -1.91920040e+00,   8.50328926e+00]

start_url = "http://localhost:8000"


try:
	driver = web.start(start_url)

	cmd = ""
	while cmd != "QUIT":
	    cmd = raw_input('>')
	    state = web.build_state(driver, web.tokenize_command(cmd))

	    actions = state.enumerate_actions()

	    action, best_score, probs = state.get_action_probs(actions, theta)

	    print "Performing... ", action
	    state.phi_dot_theta(action, theta, True)

	    #correct = [a for a in actions if a.type == 'click' and a.element.get_attribute('x-wtid') == 'continue' and a.params is None][0]

	    #print 'Correct action was:', correct
	    #state.phi_dot_theta(correct, theta, True)

	    action.perform(driver, dry=False)
finally:
	driver.quit()

