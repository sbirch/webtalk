import argparse
from data import gen_docs
from policy_gradient import policy_gradient
import numpy as np
import sys

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train webtalk to generate a parameter vector")

    parser.add_argument("corpus_file", type=file, help="A corpus file to train off of", default=sys.stdin, nargs='?')
    parser.add_argument("--url", type=str, help="An initial URL on which to start each training document", default="http://localhost:8000")
    parser.add_argument("--iters", type=int, help="Number of iterations to train on all the docs", default=50)

    args = parser.parse_args()

    docs = gen_docs.parse_docs_file(args.corpus_file)
    theta = policy_gradient(docs, args.url, ITERATIONS=args.iters)

    np.savetxt(sys.stdout, theta)
