import numpy as np
import web
import random
import time
import util.str_util as str_util
import copy
#from matplotlib import pyplot as plt
from data import gen_docs
from scipy.spatial import distance

ITERATIONS = 5

# takes in a list of lists of commands which should be executed in order
def policy_gradient(command_documents, start_url = "http://localhost:8000", visualize=False):
    theta = np.zeros(len(web.Action.FEATURE_NAMES))
    for i in range(len(web.Action.FEATURE_NAMES)):
        theta[i] = random.random()

    theta_history = [copy.copy(theta)]
    reward_history = []

    driver = web.start(start_url)
    try:
        for i in range(ITERATIONS):
            avg_dist = 0
            for doc_num, document in enumerate(command_documents):
                driver.get(start_url)
                state_actions = []
                action_choices = []

                rewarder = Rewarder([command[1] for command in document])

                # STEP 3
                for t in range(len(document)):
                    annotated_cmd = document[t]
                    state = web.build_state(driver, web.tokenize_command(annotated_cmd[0]))

                    actions = state.enumerate_actions()

                    action, best_score, probs = state.get_action_probs(actions, theta)

                    # we got to page where we cant do anything any more so end
                    # the history here
                    if action == None:
                        break

                    r = random.random()
                    acc_prob = 0
                    for a in probs:
                        acc_prob += probs[a]
                        if acc_prob > r:
                            action = a
                            break

                    rewarder.update_reward(state, action)

                    #state.phi_dot_theta(action, theta, verbose=True)
                    #print "Performing... %r for %r" % (action, annotated_cmd[0])
                    action.perform(driver, dry=False)

                    state_actions.append((
                        state,
                        action,
                        best_score
                    ))
                    action_choices.append(probs)

                gradient = np.zeros(len(web.Action.FEATURE_NAMES))
                for t in range(len(state_actions)):
                    phi_t = state_actions[t][1].as_numeric_vector()

                    # STEP 4
                    weighted_actions = np.zeros(len(web.Action.FEATURE_NAMES))
                    for action in action_choices[t]:
                        prob_action = action_choices[t][action]
                        weighted_actions = np.add(weighted_actions, \
                                  np.multiply(action.as_numeric_vector(), prob_action))

                    gradient = np.add(gradient, np.subtract(phi_t, weighted_actions))

                # STEP 5
                r = rewarder.get_reward() #reward_gold_standard(state_actions, document)
                print "Reward:", r

                reward_history.append(r)

                theta = np.add(theta, np.multiply(r, gradient))
                theta_history.append(copy.copy(theta))
                print theta
                if len(theta_history) > 1:
                    avg_dist += distance.euclidean(theta, theta_history[-2]) / len(command_documents)
            print "Avg_dist:" , avg_dist
            if avg_dist < .1:
                print "Theta is not changing much in the latest iteration, breaking"
                break
    finally:
        driver.quit()

    if visualize:
        plt.plot(reward_history, 'o')
        for i in range(len(web.Action.FEATURE_NAMES)):
            plt.plot([x[i] for x in theta_history])
        plt.legend(['reward'] + web.Action.FEATURE_NAMES)
        plt.show()

    return theta


class Rewarder:
    def __init__(self, correct, perfect=1, ok=0.5, bad=-1):
        self.reward_history = []
        self.correct = correct
        self.perfect = perfect
        self.ok = ok
        self.bad = bad
    def update_reward(self, state, action):
        self.reward_history.append((
            action.type,
            action.element.get_attribute('x-wtid'),
            action.params
        ))
    def get_reward(self):
        reward = 0

        for i, (a_type, a_element, a_text) in enumerate(self.reward_history):
            gold_type, gold_wtid, gold_text = self.correct[i]

            right_type = a_type == gold_type
            right_element = a_element == gold_wtid
            right_text = gold_text == None or a_text == gold_text

            if right_type and right_element and right_text:
                reward += self.perfect
            elif right_type and right_element and not right_text:
                reward += self.ok
            else:
                reward += self.bad

        return reward*1.0 / len(self.reward_history)


def reward_gold_standard(history, document, perfect=1, ok=0.5, bad=-1):
    correct = [command[1] for command in document]

    reward = 0

    for i, (state, action, best_score) in enumerate(history):
        gold_type, gold_wtid, gold_text = correct[i]

        right_type = action.type == gold_type
        right_element = action.element.get_attribute('x-wtid') == gold_wtid
        right_text = gold_text == None or action.params == gold_text

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






