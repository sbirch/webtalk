import numpy as np
import argparse
import web
import policy_gradient
import random
import readline
from data import gen_docs
import sys


parser = argparse.ArgumentParser(description="Launch an interactive web talk session attached to Chrome")

parser.add_argument("theta_file", type=file, help="A file containing a theta vector in the text output format of numpy, pass as an argument or pipe in through stdin", default=sys.stdin, nargs='?')

args = parser.parse_args()

theta = np.loadtxt(args.theta_file)

try:
    driver = web.start("http://localhost:8000")

    cmd = ""
    sys.stdin = open('/dev/tty')
    while cmd != "QUIT":
        cmd = raw_input('> ')
        state = web.build_state(driver, web.tokenize_command(cmd))

        actions = state.enumerate_actions()

        action, best_score, probs = state.get_action_probs(actions, theta)

        print "Performing... ", action
        print "With prob: ", probs[action]
        print state.phi_dot_theta_str(action, theta)

        if False:
            correct = [a for a in actions if a.type == 'click' and a.element.get_attribute('x-wtid') == 'continue' and a.params is None][0]
            print 'Correct action was:', correct
            print state.phi_dot_theta_str(correct, theta)

        action.perform(driver, dry=False)
finally:
    driver.quit()

