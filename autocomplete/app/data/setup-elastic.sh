# delete and re-create index
echo '>dropping index'
curl -s -X DELETE $ELASTICSEARCH_URL/genes

echo
echo '>configuring index'
curl -s -X PUT $ELASTICSEARCH_URL/genes -H "Content-Type: application/json" -d'
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
        "type": "search_as_you_type"
      }      
    }
  }
}'
echo
echo '>Ready'