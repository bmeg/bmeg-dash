# Specialized Ensembl ID parsing

Given   
  * "ensemble_id": "ENSG00000121410",
  * "symbol": "A1BG"

`search_as_you_type` will match `A1...` and `121...` (ENSG0* skipped)


## elastic

```

# drop the elastic index
DELETE genes

# setup elastic index.
# define two fields [symbol, ensemble_id] as `search_as_you_type`
# use the `simple_pattern_split` tokenizer to remove "ENSG0*" from the ensemble_id search index
PUT genes
{
  "settings": {
    "analysis": {
      "analyzer": {
        "ensembl_analyzer": {
          "tokenizer": "ensembl_tokenizer"
        }
      },
      "tokenizer": {
        "ensembl_tokenizer": {
          "type": "simple_pattern_split",
          "pattern": "ENSG0*"
        }
      }
    }
  },
  "mappings": {
    "properties": {
      "symbol": {
        "type": "search_as_you_type"
      },
      "ensemble_id": {
        "type": "search_as_you_type",
        "analyzer":"ensembl_analyzer"
      }      
    }
  }
}

# add some test data

PUT genes/_doc/ENSG00000121410?refresh
{
  "ensemble_id": "ENSG00000121410",
  "symbol": "A1BG"
}

PUT genes/_doc/ENSG00000073331?refresh
{
  "ensemble_id": "ENSG00000073331",
  "symbol": "ALPK1"    
}

# example searches

POST genes/_search
{
  "query": {
    "multi_match": {
      "query": "al",
      "type": "bool_prefix",
      "fields": [
        "symbol",
        "symbol._2gram",
        "symbol._3gram",
        "ensemble_id",
        "ensemble_id._2gram",
        "ensemble_id._3gram"        
      ]
    }
  }
}

>>> {
  "took" : 10,
  "timed_out" : false,
  "_shards" : {
    "total" : 1,
    "successful" : 1,
    "skipped" : 0,
    "failed" : 0
  },
  "hits" : {
    "total" : {
      "value" : 1,
      "relation" : "eq"
    },
    "max_score" : 1.0,
    "hits" : [
      {
        "_index" : "genes",
        "_type" : "_doc",
        "_id" : "ENSG00000073331",
        "_score" : 1.0,
        "_source" : {
          "ensemble_id" : "ENSG00000073331",
          "symbol" : "ALPK1"
        }
      }
    ]
  }
}



POST genes/_search
{
  "query": {
    "multi_match": {
      "query": "733",
      "type": "bool_prefix",
      "fields": [
        "symbol",
        "symbol._2gram",
        "symbol._3gram",
        "ensemble_id",
        "ensemble_id._2gram",
        "ensemble_id._3gram"        
      ]
    }
  }
}

>>> {
  "took" : 4,
  "timed_out" : false,
  "_shards" : {
    "total" : 1,
    "successful" : 1,
    "skipped" : 0,
    "failed" : 0
  },
  "hits" : {
    "total" : {
      "value" : 1,
      "relation" : "eq"
    },
    "max_score" : 1.0,
    "hits" : [
      {
        "_index" : "genes",
        "_type" : "_doc",
        "_id" : "ENSG00000073331",
        "_score" : 1.0,
        "_source" : {
          "ensemble_id" : "ENSG00000073331",
          "symbol" : "ALPK1"
        }
      }
    ]
  }
}
```

## python

```
import os
from pprint import pprint 

from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search
from elasticsearch_dsl.query import MultiMatch


# connect to server, setup client
client = Elasticsearch(os.environ['ELASTICSEARCH_URL'])
search = Search(using=client, index='genes')

# type ahead `al`
search.query = MultiMatch(query='al', type="bool_prefix",  fields=["symbol", "symbol._2gram", "symbol._3gram", "ensemble_id", "ensemble_id._2gram", "ensemble_id._3gram" ])
pprint([h for h in search])
# >>> [<Hit(genes/ENSG00000073331): {'ensemble_id': 'ENSG00000073331', 'symbol': 'ALPK1'}>]

# type ahead `733`
search.query = MultiMatch(query='733', type="bool_prefix",  fields=["symbol", "symbol._2gram", "symbol._3gram", "ensemble_id", "ensemble_id._2gram", "ensemble_id._3gram" ])
pprint([h for h in search])
# >>> [<Hit(genes/ENSG00000073331): {'ensemble_id': 'ENSG00000073331', 'symbol': 'ALPK1'}>]

```

## docker compose

```
alias dc=docker-compose

# start all
dc up -d

# status
dc ps

# show logs
dc logs

# show logs for app
dc logs app

# rebuild app
dc stop app ; dc rm -f app  ; dc build app

# load data, etc 
dc exec app bash
>> root@13e50cf7f2c5:/app#

# rebuild elastic index
dc exec app bash
>> root@13e50cf7f2c5:/app# 
cd data
./fetch-gene-names.sh
./setup-elastic.sh
./load_genes.py


```

## services

```
# elastic
curl localhost:9200
{
  "name" : "elastic",
  "cluster_name" : "odfe-cluster",
  "cluster_uuid" : "v54nupTqTH2iezTxZGE6kw",
  "version" : {
    "number" : "7.9.1",
    "build_flavor" : "oss",
    "build_type" : "docker",
    "build_hash" : "083627f112ba94dffc1232e8b42b73492789ef91",
    "build_date" : "2020-09-01T21:22:21.964974Z",
    "build_snapshot" : false,
    "lucene_version" : "8.6.2",
    "minimum_wire_compatibility_version" : "6.8.0",
    "minimum_index_compatibility_version" : "6.0.0-beta1"
  },
  "tagline" : "You Know, for Search"
}

## kibana

> provided as a convenience for exploring data, not required

![image](https://user-images.githubusercontent.com/47808/93501339-2b31fd00-f8ca-11ea-83e0-e035d4887fc9.png)

## dash app

`http://localhost:8050/`


## sample `backend`

* To introduce some realistic lag, we added a simple call to retrieve phenotypes per gene.

![image](https://user-images.githubusercontent.com/47808/93521354-cb951b00-f8e4-11ea-865c-9d26b74b7c54.png)

