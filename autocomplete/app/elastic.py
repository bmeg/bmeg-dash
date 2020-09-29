"""Query ES."""

import os
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search, Index
from elasticsearch_dsl.query import MultiMatch


def gene_search(query):
    """Query gene index, map to {label, value}.

    Connects to elastic search via env var ELASTICSEARCH_URL"""

    client = Elasticsearch(os.environ['ELASTICSEARCH_URL'])
    search = Search(using=client, index='genes')
    search.query = MultiMatch(query=query, type='bool_prefix', fields=[
        'symbol',
        'symbol._2gram',
        'symbol._3gram',
        'ensemble_id',
        'ensemble_id._2gram',
        'ensemble_id._3gram',
        ])

    # map
    # [<Hit(genes/ENSG00000073331): {'ensemble_id': 'ENSG00000073331', 'symbol': 'ALPK1'}>]
    # to
    #  {"label": "New York City", "value": "NYC"},

    return([{'label': f'{h.symbol}/{h.ensemble_id}', 'value': f'{h.symbol}/{h.ensemble_id}'} for h in search])


def gene_index_creation_date():
    """Fetch creation_date of gene index."""

    client = Elasticsearch(os.environ['ELASTICSEARCH_URL'])
    index = Index('genes', using=client).get()
    return index['genes']['settings']['index']['creation_date']
