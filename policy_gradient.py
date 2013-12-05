import numpy as np
import web
import random
import time
import util.str_util as str_util
import copy
#from matplotlib import pyplot as plt
from data import gen_docs

ITERATIONS = 5

# takes in a list of lists of commands which should be executed in order
def policy_gradient(command_documents, start_url = "http://localhost:8000", visualize=False):
    theta = np.zeros(len(web.Action.FEATURE_NAMES))
    for i in range(len(web.Action.FEATURE_NAMES)):
        theta[i] = random.random()

    theta_history = [copy.copy(theta)]

    driver = web.start(start_url)
    try:
        for i in range(ITERATIONS):
            for doc_num, document in enumerate(command_documents):
                driver.get(start_url)
                state_actions = []
                action_choices = []

                # STEP 3
                for t in range(len(document)):
                    annotated_cmd = document[t]
                    state = web.build_state(driver, web.tokenize_command(annotated_cmd[0]))

                    actions = state.enumerate_actions()

                    action, best_score, probs = state.get_action_probs(actions, theta)

                    r = random.random()
                    acc_prob = 0
                    for a in probs:
                        acc_prob += probs[a]
                        if acc_prob > r:
                            action = a
                            break

                    state.phi_dot_theta(action, theta, verbose=True)

                    print "Performing... %r for %r" % (action, annotated_cmd[0])
                    action.perform(driver, dry=True)

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
                r = reward_gold_standard(state_actions, document)
                print "Reward: %", r

                theta = np.add(theta, np.multiply(r, gradient))
                theta_history.append(copy.copy(theta))
    finally:
        driver.quit()

    if visualize:
        plt.legend(web.Action.FEATURE_NAMES)
        for i in range(len(web.Action.FEATURE_NAMES)):
            plt.plot([x[i] for x in theta_history])
        plt.show()

    return theta

def reward_gold_standard(history, document, perfect=1, ok=0.5, bad=-1):
    correct = [command[1] for command in document]

    reward = 0

    for i, (state, action, best_score) in enumerate(history):
        gold_type, gold_wtid, gold_text = correct[i]

        right_type = action.type == gold_type
        right_element = action.element.get_attribute('x-wtid') == gold_wtid
        right_text = gold_text != None and action.params == gold_text

        if right_type and right_element and right_text:
            reward += perfect
        elif right_type and right_element and not right_text:
            reward += ok
        else:
            reward += bad


    return reward / len(history)


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
    docs = gen_docs.get_all_docs()
    for i in range(1):
        res = policy_gradient(docs)
        print "Result theta:", res
        print






