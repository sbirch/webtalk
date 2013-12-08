import web, pprint, csv, string, random, sys
from collections import Counter
from sklearn import svm
from nltk.tokenize import word_tokenize

#from nltk.tag import pos_tag  
#import stanford_parser_pipe
#print stanford_parser_pipe.parse('Type John in the First Name field')
#sys.exit(0)

def feats(subwords, command, start, end):
    single_subword = 1 if len(subwords) == 1 else 0
    double_subword = 1 if len(subwords) == 2 else 0
    big_subword = 1 if len(subwords) > 2 else 0

    action_words = 'press hit click type enter put'.split(' ')
    contains_action_word = 1 if any([w.lower() in action_words for w in subwords]) else -1

    stop_words = 'the in as for to'.split(' ')
    contains_stop_word = 1 if any([w.lower() in stop_words for w in subwords]) else -1

    # Note that this is not the phrase likelihood, but the average term likelihood
    word_entropy = sum([web.UNIGRAM_MODEL(w) for w in subwords]) / len(subwords)

    tf_idf = sum([web.IDF_MODEL(w) for w in subwords]) / len(subwords)

    
    #tags = [(word, tag) for word, tag in pos_tag(command)][start:end]
    #taglist = [tag for word, tag in tags]

    #has_nn = 'NN' in taglist or 'NNP' in taglist
    #has_dt = 'DT' in taglist
    #has_in = 'IN' in taglist

    return [
        single_subword, double_subword, big_subword,
        contains_action_word ,contains_stop_word,
        word_entropy, tf_idf,
        #has_nn, has_dt, has_in
    ]

def subcommands(command):
    command = word_tokenize(command)
    subcommands = []
    for window_size in range(1, len(command)+1):
        for i in range(0, len(command)-window_size+1):
            subcommands.append((
                command[i:i+window_size],
                i, i+window_size
            ))
    return subcommands

def read_data(path):
    data = list(csv.reader(open(path, 'rb'), delimiter='\t'))
    return [(sentence.strip(), text.strip()) for seq,sentence,action,element,text in data if action == 'type']

def build_model(train):
    feature_vectors = []
    labels = []

    for sentence, correct in train:
        for subwords, start, end in subcommands(sentence):
            f = feats(subwords, sentence, start, end)

            label = -1
            if ' '.join([w.strip(string.punctuation) for w in subwords]).lower() == correct.lower():
                label = 1

            feature_vectors.append(f)
            labels.append(label)

    clf = svm.LinearSVC()
    clf.fit(feature_vectors, labels)

    return clf

def build_default_model():
    model = build_model(read_data('data/sendacard_corpus.tsv'))

    def evalmodel(subwords):
        v = model.decision_function(feats(subwords, None, None, None))[0]
        return 1 + v

    return evalmodel

if __name__ == '__main__':
    #clf = build_model(train)

    model = build_default_model()

    total_correct = 0

    test = read_data('data/sendacard_mturk_corpus.tsv')

    for sentence, correct in test:
        print sentence, '=>', correct

        best = Counter()
        for subwords, start, end in subcommands(sentence):
            #f = feats(subwords, sentence, start, end)
            #prediction, decision_f = clf.predict(f)[0], clf.decision_function(f)[0]
            best[tuple(subwords)] += model(subwords)

        best_cmd, best_score = best.most_common(1)[0]
        if ' '.join([w.strip(string.punctuation) for w in best_cmd]).lower() == correct.lower():
            total_correct += 1
        else:
            print '\tIncorrect:', best_cmd

        for cmd, score in best.most_common(3):
            print '\t', ' '.join(cmd), score

    print 'Accuracy:', (total_correct*1.0) / len(test)
