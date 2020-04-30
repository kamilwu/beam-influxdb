import os
import sys

from load import load


def run(directory):
    for csv_to_measurements_mapping in ['load_test_measurements.txt',
                                        'beam_performance_measurements.txt']:
        with open(csv_to_measurements_mapping) as file:
            for line in file:
                splitted = line.rstrip().split(' ')
                csv_file, measurement = splitted[0], splitted[1]
                load(os.path.join(directory, csv_file), measurement)


if __name__ == '__main__':
    try:
        run(sys.argv[1])
    except IndexError:
        print('Usage: python {} dir'.format(sys.argv[0]))
        sys.exit(1)
