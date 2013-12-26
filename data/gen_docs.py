from collections import defaultdict
import sys
import argparse

# dict from sequence number to a tuple with command and a second tuple with its
# semantic representation
def get_all_docs(cmds_file):
    commands = defaultdict(list)
    for l in cmds_file:
        split_line = l.split("\t")

        n = int(split_line[0])
        str_cmd = split_line[1]

        cmd_type = split_line[2]
        wtid = split_line[3]
        args = split_line[4].strip()

        if args == "None":
            args = None

        semantic_cmd = (cmd_type, wtid, args)

        commands[n].append((str_cmd, semantic_cmd))

    all_docs = []


    def rec_gendocs(step_num = 1, doc_so_far = []):
        if step_num == len(commands):
            all_docs.append(doc_so_far)

        for command in commands[step_num]:
            new_doc = list(doc_so_far)
            new_doc.append(command)
            rec_gendocs(step_num+1, new_doc)

    rec_gendocs()
    return all_docs

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train webtalk to generate a parameter vector")

    parser.add_argument("corpus_file", type=file, help="A tsv of plain commands with order annotations")
    parser.add_argument("num_docs", type=int, help="A number documents to randomly generate off of the corpus file")

    args = parser.parse_args()

    for doc in get_all_docs(args.corpus_file)[:args.num_docs]:
        for command in doc:
            txt_cmd, (cmd_type, target, arg) = command
            print str(txt_cmd) + "\t" + str(cmd_type) + "\t" + str(target) + "\t" + str(arg)
        print









