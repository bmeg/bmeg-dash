import os
import yaml
import gripql
from ..app import app
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search
from elasticsearch_dsl.query import MultiMatch
from flask_caching import Cache

with open('bmeg_app/config.yaml') as f:
    config = yaml.load(f, Loader=yaml.FullLoader)

if 'credentials' in config['bmeg']:
    conn = gripql.Connection(
        config['bmeg']['url'],
        credential_file=config['bmeg']['credentials']
    )
else:
    conn = gripql.Connection(
        config['bmeg']['url']
    )

G = conn.graph(config['bmeg']['graph'])

# configure dash app
# Setup cache, just use local file system for now.
cache = Cache(app.server, config={
    'CACHE_TYPE': 'filesystem',
    'CACHE_DIR': '/tmp/'
})
# check last load of elastic every hour
CHECK_ELASTIC_LOAD_TIMEOUT = 60*60
# otherwise, infinite - use creation_date to invalidate cache
TIMEOUT = 0


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
    out = (
        [
            {
                'label': f'{h.symbol}/{h.ensemble_id}',
                'value': f'{h.symbol}/{h.ensemble_id}'
            }
            for h in search
        ]
    )
    return out


@cache.memoize(timeout=TIMEOUT)
def get_vertex_label_count(label):
    return G.query().V().hasLabel(label).count().execute()[0]['count']
