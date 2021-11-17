import os
import yaml
import gripql
from .. import config
from ..app import app
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search
from elasticsearch_dsl.query import MultiMatch
from flask_caching import Cache

if 'credentials' in config.CONFIG['bmeg']:
    credFile = os.path.join( config.CONFIG_PATH, config.CONFIG['bmeg']['credentials'] )
    conn = gripql.Connection(
        config.CONFIG['bmeg']['url'],
        credential_file=credFile
    )
else:
    conn = gripql.Connection(
        config.CONFIG['bmeg']['url']
    )

G = conn.graph(config.CONFIG['bmeg']['graph'])

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

GENE_MAP = None

def gene_search(query):
    """Query gene index, map to {label, value}.

    Connects to elastic search via env var ELASTICSEARCH_URL"""

    if 'ELASTICSEARCH_URL' in os.environ:
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

    global GENE_MAP
    if GENE_MAP is None:
        GENE_MAP = sorted(G.query().V().hasLabel("Gene").render(["$.symbol", "$._gid"]).execute(), key=lambda x:x[0])

    query = query.upper()
    t = query.split("/") #check if in the GENE/ENSEMBL format
    if len(t) > 1 and t[1].startswith("ENSG"):
        query = t[1]

    out = []
    if query.startswith("ENSG"):
        for symbol, ensemble_id in GENE_MAP:
            if ensemble_id.startswith(query):
                out.append({
                    'label' : "%s/%s" % (symbol, ensemble_id),
                    'value' : "%s/%s" % (symbol, ensemble_id)
                })
    else:
        for symbol, ensemble_id in GENE_MAP:
            if symbol.startswith(query):
                out.append({
                    'label' : "%s/%s" % (symbol, ensemble_id),
                    'value' : "%s/%s" % (symbol, ensemble_id)
                })
    return out


@cache.memoize(timeout=TIMEOUT)
def get_vertex_label_count(label):
    return G.query().V().hasLabel(label).count().execute()[0]['count']
