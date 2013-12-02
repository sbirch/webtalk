import numpy as np
import web
import random
import time

ITERATIONS = 20

# takes in a list of lists of commands which should be executed in order
def policy_gradient(command_documents, start_url = "http://www.hipmunk.com"):
    theta = np.array([ -5.0, 0.0, 0.0, 0, 11.0, 0.0, 5.0, 5.0, 1.0, -1.0, -1.0 ])
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
                action.perform(driver, True)
                state_actions.append((state, action))
                action_choices.append(probs)

            gradient = np.zeros(len(web.Action.FEATURE_NAMES))
            for t in range(len(document)):
                phi_t = actions[t].as_numeric_vector()

                # STEP 4
                weighted_actions = np.zeros(len(web.Action.FEATURE_NAMES))
                for action in action_choices[t]:
                    prob_action = action_choices[t][action]
                    weighted_actions = np.add(weighted_actions, \
                              np.multiply(action.as_numeric_vector(), prob_action))

                gradient = np.add(gradient, np.subtract(phi_t, weighted_actions))

            # STEP 5
            r = reward(state_actions)

            theta = np.add(theta, np.multiply(r, gradient))
            print theta
    driver.quit()
    return theta
def reward(history):
    last_state, last_action = history[-1]
    classes = set(last_action.element.get_attribute("class").split())

    search_classes = set(["submit front-box-search-button m-flight m-active"])


    return len(classes.intersection(search_classes))

if __name__ == "__main__":
    docs = [["click search"]]
    for i in range(1):
        print policy_gradient(docs)






