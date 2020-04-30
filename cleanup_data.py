import heapq
import os
import datetime
import shutil
import sys
from collections import namedtuple
from datetime import datetime

Row = namedtuple('Row', 'test_id timestamp metric value')
GARBAGE = {'_MAX', '_MIN', '_MEAN', '_COUNT'}


def create_output_dir(dir_name):
    try:
        os.mkdir(dir_name)
    except FileExistsError:
        print('%s already exists, deleting...' % dir_name)
        shutil.rmtree(dir_name)
        os.mkdir(dir_name)


def ensure_timestamp_has_miliseconds_part(timestamp):
    fmt = '%Y-%m-%d %H:%M:%S.%f UTC'
    fmt_without_millis = '%Y-%m-%d %H:%M:%S UTC'
    try:
        dt = datetime.strptime(timestamp, fmt)
    except ValueError:
        dt = datetime.strptime(timestamp, fmt_without_millis)
    return dt.strftime(fmt)


def cleanups_rows(lines):
    for line in lines:
        row = Row(*line.rstrip().split(','))

        value = float(row.value)
        if value < 0.0 or value > 1500000000 or \
                any(x in row.metric for x in GARBAGE):
            continue

        timestamp = ensure_timestamp_has_miliseconds_part(
            row.timestamp)
        yield Row(row.test_id, timestamp, row.metric, row.value)


def cleanup(input_dir, csv_filename, output_dir):
    in_csv_path = os.path.join(input_dir, csv_filename)
    out_csv_path = os.path.join(output_dir, csv_filename)
    print('Processing {}...'.format(csv_filename))

    with open(in_csv_path) as f_in:
        lines = f_in.readlines()[1:]
        rows = list(cleanups_rows(lines))

        if rows and csv_filename.startswith('python'):
            latest_row = heapq.nlargest(1, rows, key=lambda r: r.timestamp)[0]
            rows = [Row(r.test_id, r.timestamp, latest_row.metric, r.value) for
                    r in rows]

        if rows and csv_filename.startswith('java'):
            if 'spark' in csv_filename.lower():
                metric_prefix = 'sparkstructuredstreaming_'
            elif 'dataflow' in csv_filename.lower():
                metric_prefix = 'dataflow_'
            else:
                raise ValueError('excepted either "dataflow" or "spark" in a '
                                 'filename')

            rows = [Row(r.test_id, r.timestamp, r.metric, r.value)
                    if 'dataflow' in r.metric or 'spark' in r.metric else
                    Row(r.test_id, r.timestamp, metric_prefix + r.metric,
                        r.value) for r in rows]

        with open(out_csv_path, 'w') as f_out:
            for row in rows:
                f_out.write(','.join(row) + '\n')


def run(input_directory):
    output_dir = input_directory + '_clean'
    create_output_dir(output_dir)

    for file in os.listdir(input_directory):
        cleanup(input_directory, file, output_dir)


if __name__ == '__main__':
    try:
        run(sys.argv[1])
    except IndexError:
        print('Usage: python {} input_dir'.format(sys.argv[0]))
        sys.exit(1)
