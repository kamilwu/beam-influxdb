This is an example usage of InfluxDB and Kapacitor to store and detect anomalies in IO
performance tests and Load tests in Beam.

## What does the repository contain
- Configuration files for InfluxDB and Kapacitor. This config is mostly default.
- Python script that loads data from CSV files to InfluxDB.
- docker-compose file
- Definition of an example Kapacitor alert
- one CSV file with the results of BigQueryIO write performance test

## How to run

- Set up containers. You will need `docker` and `docker-compose` installed on your machine.
```bash
docker-compose up
```

- Run `load.py` to populate InfluxDb with data. We are going to use historical results of
 BigQueryIO write performance test between 2019-07-12 and 2019-11-27.    
```bash
pip install -r requirements.txt
python load.py data/python_bq_write python_bq_write
```

- Run grafana to see the results. See https://grafana.com/docs/guides/getting_started/#logging-in-for-the-first-time
to learn how to log in for the first time. After logging in, choose `Beam tests` dashboard.

- Kapacitor can save recordings of data and replay them against a specified task (alert). This is
 especially useful when debugging alerts. We can use this feature to check whether we are able to
 detect a regression in a specified chunk of data.

```bash
docker exec -it kapacitor bash
# The following command saves recording and returns its ID. We will need this ID later.
kapacitor record query -query 'select * from "beam_metrics"."autogen"."python_bq_write"' -type stream
kapacitor replay -recording=$RECORDING_ID -task=alert
```

The alert logs a message to `/tmp/alerts.log` when regression is detected. See the content of
 this file by typing:
```bash
cat /tmp/alerts.log
```  
