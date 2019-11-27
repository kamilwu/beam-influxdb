import sys
from collections import namedtuple
from datetime import datetime

from influxdb import InfluxDBClient


def init(db_name):
    client = InfluxDBClient(host='localhost', port=8086)

    if db_name not in client.get_list_database():
        client.create_database(db_name)

    client.switch_database(db_name)
    return client


def load(csv_filename, measurement_name):
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
        } for x in data]
    except ValueError as e:
        print('Invalid data: {}'.format(str(e)))
        sys.exit(1)

    ret = client.write_points(points, batch_size=len(points))

    if not ret:
        raise RuntimeError('Operation failed')
    else:
        print('Inserted {} rows.'.format(len(points)))


if __name__ == '__main__':
    if len(sys.argv) > 1:
        client = init('beam_metrics')
        load(sys.argv[1], sys.argv[2])
    else:
        sys.exit(1)
