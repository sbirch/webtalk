import numpy as np
import web
import policy_gradient
from data import gen_docs

docs = gen_docs.get_all_docs()[:10]

theta_of_all_thetas = [0.17334518, 0.90195079, 0.42518274, 0.72998457,\
        0.56155784, 0.2100886, 0.73153149, 0.20276437, 0.0031535, 0.21628661]
theta = policy_gradient.policy_gradient(docs)

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

