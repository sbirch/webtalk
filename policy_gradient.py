import numpy as np
import web
import random
import time
import util.str_util as str_util

ITERATIONS = 5

# takes in a list of lists of commands which should be executed in order
def policy_gradient(command_documents, start_url = "http://www.hipmunk.com"):
    theta = np.zeros(len(web.Action.FEATURE_NAMES))
    #for i in range(len(web.Action.FEATURE_NAMES)):
    #    theta[i] = random.random()

    driver = web.start("http://www.hipmunk.com/flights-search")

    for i in range(ITERATIONS):
        for doc_num, document in enumerate(command_documents):
            state_actions = []
            action_choices = []

            # STEP 3
            print document
            for t in range(len(document)):
                state = web.build_state(driver, web.tokenize_command(document[t]))

                action, best_score, probs = state.get_actions_and_probs(theta)

                print "Performing... %" , action
                action.perform(driver, True)

                state_actions.append((
                    state,
                    action,
                    best_score
                ))
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
    driver.quit()
    return theta

def reward_branavan(history):
    
    sentence_rewards = []

    for state, action, best_score in history:
        # did the action make sense for state?
        # we assess by seeing if any word in the command appeared in the element we chose.
        chosen_element_words = action.features['text_words']
        if str_util.get_min_distance_for_words(state.command, chosen_element_words) == 0:
            sentence_rewards.append(best_score)
        else:
            return -1

    return sum(sentence_rewards)*1.0 / len(sentence_rewards)

def reward(history):
    #last_state, last_action, last_best_score = history[-1]
    #classes = set(last_action.element.get_attribute("class").split())

    #search_classes = set(["submit front-box-search-button m-flight m-active"])


    #return len(classes.intersection(search_classes))
    return random.randint(0,10)

if __name__ == "__main__":
    docs = [["click search"]]
    for i in range(10):
        res = policy_gradient(docs)
        print "Result theta: "
        print res
        print






