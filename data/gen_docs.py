from collections import defaultdict

# dict from sequence number to a tuple with command and a second tuple with its
# semantic representation
def get_all_docs(cmds_file):
    commands = defaultdict(list)
    for l in open(cmds_file):
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
        if step_num == 5:#len(commands):
            all_docs.append(doc_so_far)

        for command in commands[step_num]:
            new_doc = list(doc_so_far)
            new_doc.append(command)
            rec_gendocs(step_num+1, new_doc)

    rec_gendocs()
    return all_docs









