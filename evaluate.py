from data import gen_docs
import random
import web
import text_classification
import policy_gradient

# return a tuple with the percentage of correct commands
# and the percentage of correct documents for the given
# evaluation corpus file and theta vector
def evaluate(eval_corpus_file, theta, start_url):
    docs = gen_docs.get_all_docs(eval_corpus_file)
    random.shuffle(docs)
    docs = docs[:100]
    driver = web.start(start_url)

    correct_docs = 0

    correct_cmds = 0
    total_cmds = 0
    for doc in docs:
        driver.get(start_url)
        doc_correct = True

        for cmd in doc:
            total_cmds += 1
            text_cmd, (cmd_type, wtid, arg) = cmd

            # do it
            state = web.build_state(driver, web.tokenize_command(text_cmd))
            actions = state.enumerate_actions()
            action, best_score, probs = state.get_action_probs(actions, theta)


            if action and \
               action.type == cmd_type and \
               action.element.get_attribute('x-wtid') == wtid and \
               (action.params == None or text_classification.untokenize_subcommand(action.params).lower() == arg.lower()):
                   correct_cmds += 1
            else:
                print "Failed: ", action, " for ", text_cmd
                doc_correct = False

            if action:
                action.perform(driver)
        if doc_correct:
            correct_docs += 1


    return float(correct_docs) / len(docs), float(correct_cmds) / total_cmds

if __name__ == "__main__":
    # generated this one friday dec 6

    # Doc Pct:  0.37  Cmd Pct:  0.89
    #theta = [7.4246, 1.6352, 7.2982, -2.9867, 5.4484, 2.0682, -0.0010, 0.8105, 5.0358, 6.9543]
    theta = policy_gradient.policy_gradient([[]], ITERATIONS=0)

    doc_pct, cmd_pct = evaluate("data/sendacard_mturk_corpus.tsv", theta, "http://localhost:8000")

    print "Doc Pct: " , doc_pct , " Cmd Pct: " , cmd_pct


