# Specialized Ensembl ID parsing

Given   
  * "ensemble_id": "ENSG00000121410",
  * "symbol": "A1BG"

`search_as_you_type` will match `A1...` and `121...` (ENSG0* skipped)


## elastic

```

DELETE genes

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