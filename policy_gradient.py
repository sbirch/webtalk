import numpy as np
import web
import random
import time
import util.str_util as str_util
import copy
import sys
from data import gen_docs
from scipy.spatial import distance

# takes in a list of lists of commands which should be executed in order
def policy_gradient(command_documents, start_url = "http://localhost:8000", visualize=False, verbose=False, ITERATIONS=50):
    theta = np.zeros(len(web.Action.FEATURE_NAMES))

    for i in range(len(web.Action.FEATURE_NAMES)):
        theta[i] = (((random.random() * 2) - 1) / 1000)

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
                    cmd, annotation = document[t]

                    state = web.build_state(driver, web.tokenize_command(cmd))

                    actions = state.enumerate_actions()

                    action, best_score, probs = state.get_action_probs(actions, theta)


                    # we got to page where we cant do anything any more so end
                    # the history here
                    if action == None:
                        break

                    # pick an action weighted by how likely it is
                    r = random.random()
                    acc_prob = 0
                    for a in probs:
                        acc_prob += probs[a]
                        if acc_prob > r:
                            action = a
                            break

                    if verbose:
                        state.phi_dot_theta(action, theta, verbose=True)

                    rewarder.update_reward(state, action)

                    if verbose:
                        print "Performing... %r for %r" % (action, cmd)
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
                if verbose:
                    # \x1b[2K\x1b[0G ?
                    print "Reward: %r" % r

                reward_history.append(r)

                theta = np.add(theta, np.multiply(r, gradient))
                theta_history.append(copy.copy(theta))
                if len(theta_history) > 1:
                    avg_dist += distance.euclidean(theta, theta_history[-2]) / len(command_documents)
            if verbose:
                print "Avg_dist:" , avg_dist
            if avg_dist < .1:
                if verbose:
                    print "Theta is not changing much in the latest iteration, breaking"
                break
    finally:
        driver.quit()

    if visualize:
        from matplotlib import pyplot as plt
        plt.plot(reward_history, 'o')
        for i in range(len(web.Action.FEATURE_NAMES)):
            plt.plot([x[i] for x in theta_history])
        plt.legend(['reward'] + web.Action.FEATURE_NAMES)
        plt.show()

    return theta


class Rewarder:
    def __init__(self, correct, perfect=1, ok=0.6, bad=-1):
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
            if gold_text: gold_text = web.tokenize_command(gold_text)

            right_type = a_type == gold_type
            right_element = a_element == gold_wtid

            if right_type and right_element:
                reward += self.ok

                if gold_text and a_text:
                    longer_text = max(len(gold_text), len(a_text))
                    text_rightness = float(len(set(gold_text).intersection(set(a_text)))) / longer_text
                    reward += (self.perfect - self.ok)  * text_rightness
                elif not gold_text and not a_text:
                    reward += self.perfect - self.ok
            else:
                reward += self.bad

        return reward*1.0 / len(self.reward_history)


if __name__ == "__main__":
    docs = gen_docs.get_all_docs("data/sendacard_corpus.tsv")[:25]
    print "Theta:", policy_gradient(docs)
