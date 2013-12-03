import numpy as np
import web
import random
import time
import util.str_util as str_util

ITERATIONS = 100

# takes in a list of lists of commands which should be executed in order
def policy_gradient(command_documents, start_url = "http://www.hipmunk.com"):
    theta = np.zeros(len(web.Action.FEATURE_NAMES))
    #for i in range(len(web.Action.FEATURE_NAMES)):
    #    theta[i] = random.randint(0,10)


    driver = web.start("http://www.hipmunk.com/flights-search")
    for i in range(ITERATIONS):
        for doc_num, document in enumerate(command_documents):
            state_actions = []
            action_choices = []

            # STEP 3
            print document
            for t in range(len(document)):
                state = web.build_state(driver, web.tokenize_command(document[t]))

                actions = state.enumerate_actions()
                assert len(actions) > 0 # If the actions list is empty there will be errors later on. (Perhaps the page failed to load?)
                action, best_score, probs = state.get_action_probs(actions, theta)

                state.phi_dot_theta(action, theta, verbose=True)

                print "Performing... %r for %r" % (action, document[t])
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
            r = reward_gold_standard(state_actions)
            print "Reward: %", r

            theta = np.add(theta, np.multiply(r, gradient))
    driver.quit()
    return theta

def reward_gold_standard(history):
    correct = [
        ('type', 'firstname', 'Andrew'),
        ('type', 'lastname', 'Kovacs'),
        ('type', 'mailbox', '1337'),
        ('click', 'continue', None)
    ]

    reward = 0

    for i, (state, action, best_score) in enumerate(history):
        gold_type, gold_wtid, gold_text = correct[i]

        right_type = action.type == gold_type
        right_element = action.element.get_attribute('x-wtid') == gold_wtid
        right_text = gold_text != None and action.params == gold_text

        score = sum([1 for b in [right_type, right_element, right_text] if b])

        reward += score/3.0


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
    #docs = [["type providence into from box", "type new york into to box", "click search"]]
    docs = [["click search"]]
    for i in range(1):
        res = policy_gradient(docs)
        print "Result theta: "
        print res
        print






