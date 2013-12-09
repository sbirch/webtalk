from data import gen_docs
import random
import web
import text_classification

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
               action.element.get_attribute('x-wtid') == wtid and \
               (action.params == None or text_classification.untokenize_subcommand(action.params).lower() == arg.lower()):
                   correct_cmds += 1
            else:
                doc_correct = False

            action.perform(driver)
        if doc_correct:
            correct_docs += 1


    return float(correct_docs) / len(docs), float(correct_cmds) / total_cmds

if __name__ == "__main__":
    # generated this one friday dec 6

    theta = [8.38515110e+00,   9.63934260e-01,  1.05792457e+01,  -4.32258654e+00,
             6.42159957e+00,   2.45657051e+00,  8.16512377e-03,   1.02236192e+00,
             6.45579111e+00,   7.19044059e+00]
    doc_pct, cmd_pct = evaluate("data/sendacard_mturk_corpus.tsv", theta, "http://localhost:8000")

    print "Doc Pct: " , doc_pct , " Cmd Pct: " , cmd_pct


