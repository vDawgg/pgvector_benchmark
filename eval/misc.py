import os

import pandas as pd

def get_all_exceptions():
    current_dir = os.path.dirname(__file__)
    benchmark_dir = os.path.join(current_dir, '..', 'benchmark')
    logs_dir = os.path.join(benchmark_dir, 'results', 'logs')

    errors = []
    for f in os.listdir(logs_dir):
        log = pd.read_pickle(os.path.join(logs_dir, f))
        errors.extend(log['error_string'])

    errors = [e.__str__() for e in errors]
    for e in set(errors):
        print(e)


if __name__ == '__main__':
    get_all_exceptions()
