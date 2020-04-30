import sys
from collections import namedtuple
from datetime import datetime

import influxdb
from influxdb import exceptions


def init(db_name):
    client = influxdb.InfluxDBClient(host='localhost', port=8086)
    client.switch_database(db_name)
    return client


def load(csv_filename, measurement_name):
    client = init('beam_test_metrics')

    with open(csv_filename) as f:
        data = [line.rstrip() for line in f.readlines()[1:]]

    Row = namedtuple('Row', 'test_id time metric value')
    data = [Row(*(x.split(','))) for x in data]

    try:
        points = [{
            'measurement': measurement_name,
            'time': datetime.strptime(x.time, '%Y-%m-%d %H:%M:%S.%f %Z'),
            'fields': {
                'value': float(x.value)
            },
            'tags': {
                'metric': x.metric,
                'test_id': x.test_id
            },
        } for x in data if float(x.value) > 0.0]
    except ValueError as e:
        print('Invalid data: {}'.format(str(e)))
        sys.exit(1)

    try:
        client.write_points(points, batch_size=len(points))
    except exceptions.InfluxDBClientError:
        # Ignore "points beyond retention policy" errors
        pass

    print('Inserted {} rows.'.format(len(points)))


if __name__ == '__main__':
    if len(sys.argv) > 1:
        load(sys.argv[1], sys.argv[2])
    else:
        sys.exit(1)
