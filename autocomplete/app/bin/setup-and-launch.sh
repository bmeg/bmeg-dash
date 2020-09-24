#!/usr/bin/env bash
# setup elastic index and launch app


curl -s -f $ELASTICSEARCH_URL/genes
if [ $? -eq 0 ]
then
  echo "/genes index exists"
else
  echo "/genes index does not exist"
  echo "/genes setup"
  ./data/setup-elastic.sh
  echo "/genes data //TODO - replace with grip query"
  ./data/fetch-gene-names.sh
  echo "/genes load"
  ./data/load_genes.py  
fi


python -m app_autocomplete