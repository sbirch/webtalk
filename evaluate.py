from data import gen_docs
import random
import web

# return a tuple with the percentage of correct commands
# and the percentage of correct documents for the given
# evaluation corpus file and theta vector
def evaluate(eval_corpus_file, theta, start_url):
    docs = gen_docs.get_all_docs(eval_corpus_file)
    random.shuffle(docs)
    docs = docs[:200]
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
               action.element.get_attribute('x-wtid') == wtid:
               #action.params == arg:
                   correct_cmds += 1
            else:
                doc_correct = False

            action.perform(driver)
        if doc_correct:
            correct_docs += 1


    return float(correct_docs) / len(docs), float(correct_cmds) / total_cmds

if __name__ == "__main__":
    # generated this one friday dec 6
    theta_of_all_thetas = [5.19141646, 0.94069248, 7.67249229, -1.43515366, \
                           3.75413168, 2.51073774, 0.38076579,  0.63318844,\
                           4.80660684, 3.97727048, -2.29169644,  -3.44135489]
    doc_pct, cmd_pct = evaluate("data/sendacard_mturk_corpus.tsv", theta_of_all_thetas, "http://localhost:8000")

    print "Doc Pct: " , doc_pct , " Cmd Pct: " , cmd_pct


