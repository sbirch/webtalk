import numpy as np
import web
import random
import time

ITERATIONS = 2

# takes in a list of lists of commands which should be executed in order
def policy_gradient(command_documents, start_url = "http://www.hipmunk.com"):
    theta = np.zeros(len(web.Action.FEATURE_NAMES))
    driver = web.start("http://www.hipmunk.com/flights-search")

    for i in range(ITERATIONS):
        for document in command_documents:
            state_actions = []
            action_choices = []

            # STEP 3
            print document
            for t in range(len(document)):
                state = web.build_state(driver, web.tokenize_command(document[t]))

                actions = state.enumerate_actions()
                action, score, probs = state.get_action_probs(actions, theta)

                print "Performing... %" , action
                action.perform(driver)
                state_actions.append((state, action))
                action_choices.append(probs)

                # TODO: properly wait for load using selenium.WebDriverWait
                time.sleep(15)

            gradient = np.zeros(len(web.Action.FEATURE_NAMES))
            for t in range(len(document)):
                phi_t = actions[t].as_numeric_vector()

                # STEP 4
                weighted_actions = np.zeros(len(web.Action.FEATURE_NAMES))
                print action_choices[t]
                for action in action_choices[t]:
                    prob_action = action_choices[t][action]
                    weighted_actions = np.add(weighted_actions, \
                              np.multiply(action.as_numeric_vector(), prob_action))

                print action.as_numeric_vector
                print prob_action
                print weighted_actions
                print
                gradient = np.add(gradient, np.subtract(phi_t, weighted_actions))

            # STEP 5
            r = reward(state_actions)
            print r
            print gradient
            print theta
            print

            theta = np.add(theta, np.multiply(r, gradient))
    return theta
def reward(history):
    return random.randrange(100)

if __name__ == "__main__":
    docs = [["click search"]]
    print policy_gradient(docs)




