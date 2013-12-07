import numpy as np
import web
import policy_gradient
import random
from data import gen_docs

docs = gen_docs.get_all_docs("data/sendacard_corpus.tsv")
docs = random.shuffle(docs)
docs = gen_docs.get_all_docs("data/sendacard_corpus.tsv")[:100]
#docs = [[("Hit submit", ("click", "submit", None))]]

theta_of_all_thetas = [5.19141646, 0.94069248, 7.67249229, -1.43515366, \
                       3.75413168, 2.51073774, 0.38076579,  0.63318844,\
                       4.80660684, 3.97727048, -2.29169644,  -3.44135489]
#theta = policy_gradient.policy_gradient(docs)
theta = theta_of_all_thetas

start_url = "http://localhost:8000"



driver = web.start(start_url)

cmd = ""
while cmd != "QUIT":
    cmd = raw_input()
    state = web.build_state(driver, web.tokenize_command(cmd))

    actions = state.enumerate_actions()

    action, best_score, probs = state.get_action_probs(actions, theta)

    state.phi_dot_theta(action, theta, True)

    action.perform(driver)

