
import os
import yaml

import gripql
import dash
import pandas as pd

from ..app import app
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search, Index
from elasticsearch_dsl.query import MultiMatch

from flask_caching import Cache


with open('bmeg_app/config.yaml') as f:
    config = yaml.load(f, Loader=yaml.FullLoader)
conn = gripql.Connection("https://bmeg.io/api", credential_file = config['bmeg']['credentials'])
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
    return([{'label': f'{h.symbol}/{h.ensemble_id}', 'value': f'{h.symbol}/{h.ensemble_id}'} for h in search])

@cache.memoize(timeout=TIMEOUT)
def get_vertex_label_count(label):
    return G.query().V().hasLabel(label).count().execute()[0]['count']

def line2disease(lines_list):
    '''Dictionary mapping cell line GIDs to reported primary disease'''
    disease_dict = {}
    q=G.query().V(lines_list).render(["$._gid",'$._data.cellline_attributes.Primary Disease'])
    for row in q:
        disease_dict[row[0]]=row[1] # some vals are None
    return disease_dict
        
@cache.memoize(timeout=TIMEOUT)
def get_base_matrix(project, drug_resp,selected_drug,selected_disease):
    '''Get row col matrix of cell line vs drug for a specific project'''   
    q = G.query().V(project).out("cases").as_("ca").out("samples").out("aliquots").out("drug_response").as_("dr").out("compounds").as_("c")
    q = q.render(["$ca._gid", "$c._gid", drug_resp])
    data = {}
    for row in q:
        if row[0] not in data: 
            data[row[0]] = { row[1] :  row[2] } 
        else: 
            data[row[0]][row[1]] = row[2]  
    df = pd.DataFrame(data).transpose()
    df = df.sort_index().sort_index(axis=1) #sort by rows, cols
    # create disease mapping dict
    disease =line2disease(list(df.index))
    # exclude non disease related derived cell lines
    new_col=[]
    for a in list(df.index):
        new_col.append(disease.get(a))
    df['disease']=new_col
    subset_df=df[df['disease']==selected_disease]
    # set established drug to first col and rm disease col
    new_col=subset_df.pop(selected_drug)
    subset_df.insert(0, selected_drug, new_col)
    subset_df.pop('disease')
    return subset_df
