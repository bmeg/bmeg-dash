#!/usr/bin/env bash
# setup elastic index and launch app


curl -s -f $ELASTICSEARCH_URL/genes
if [ $? -eq 0 ]
then
  echo
  echo "/genes index exists"
  echo
  ls -l bmeg_app/secrets/bmeg_credentials.json
  echo
  echo
else
  echo "/genes index does not exist"
  echo "/genes setup"
  ./bin/setup-elastic.sh
  echo "/genes data //TODO - replace with grip query"
  ./bin/fetch-gene-names.sh
  echo "/genes load"
  ./bin/load_genes.py
fi


python -m bmeg_app
