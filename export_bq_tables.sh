#!/usr/bin/env bash
set -euo pipefail

if [[ -z "${GCS_BUCKET}" ]]; then
  echo "GCS_BUCKET is required."
  exit 1
fi

load_test=$(cat load_test.txt)
beam_performance=$(cat beam_performance.txt)

for table in ${load_test}
do
  bq extract --destination_format=CSV "load_test.${table}" "${GCS_BUCKET}/bq_tables/${table}.csv"
done

for table in ${beam_performance}
do
  bq extract --destination_format=CSV "beam_performance.${table}" "${GCS_BUCKET}/bq_tables/${table}.csv"
done

mkdir -p bq_data
gsutil -m cp "${GCS_BUCKET}/bq_tables/*" bq_data
gsutil -m rm -rf "${GCS_BUCKET}/bq_tables"

python cleanup_data.py bq_data
python inject.py bq_data_clean
