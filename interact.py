import numpy as np
import web
import policy_gradient
import random
from data import gen_docs

docs = gen_docs.get_all_docs("data/sendacard_corpus.tsv")
random.shuffle(docs)
docs = docs[:25]

#docs = gen_docs.get_all_docs("data/sendacard_corpus.tsv")[:25]
#docs = [[("Hit submit", ("click", "submit", None))]]

#theta_of_all_thetas = [5.19141646, 0.94069248, 7.67249229, -1.43515366, \
#                       3.75413168, 2.51073774, 0.38076579,  0.63318844,\
#                       4.80660684, 3.97727048, -2.29169644,  -3.44135489]

#theta = policy_gradient.policy_gradient(docs)
#theta = theta_of_all_thetas

theta = [  1.36530115e+00,   6.02365845e-01 ,  8.20258919e+00,  -1.47179863e+00, 5.63042785e+00,   1.56722528e+00,   3.25862791e-03,   2.65489344e-01, 5.05448778e+00,   6.13476141e+00]
start_url = "http://localhost:8000"



driver = web.start(start_url)

cmd = ""
while cmd != "QUIT":
    cmd = raw_input('>')
    state = web.build_state(driver, web.tokenize_command(cmd))

    actions = state.enumerate_actions()

    action, best_score, probs = state.get_action_probs(actions, theta)

    print "Performing... ", action
    state.phi_dot_theta(action, theta, True)

    correct = [a for a in actions if a.type == 'click' and a.element.get_attribute('x-wtid') == 'continue' and a.params is None][0]

    print 'Correct action was:', correct
    state.phi_dot_theta(correct, theta, True)

    action.perform(driver)

