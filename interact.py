import numpy as np
import web

start_url = "http://localhost:8000"
theta = np.zeros(len(web.Action.FEATURE_NAMES))
for i in range(len(web.Action.FEATURE_NAMES)):
    theta[i] = 1



driver = web.start(start_url)

cmd = ""
while cmd != "QUIT":
    cmd = raw_input()
    state = web.build_state(driver, web.tokenize_command(cmd))

    actions = state.enumerate_actions()

    action, best_score, probs = state.get_action_probs(actions, theta)

    action.perform(driver)

