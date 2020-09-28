from ..db import G
from collections import Counter
import gripql
import json
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def gene_dd_selections(df, val_col, key_col):
    '''Gene dropdown menu options. Input gene symbol or ensembl id'''
    options = dict(zip(df[key_col],df[val_col]))
    return options
    
def drug_dd_selections(selected_gene, key_col, val_col, df):
    '''Get drug selections avail for the user selected gene'''
    df2= df[df['geneID']==selected_gene].reset_index(drop=True)
    options = dict(zip(df2[key_col],df2[val_col]))
    return options
    
def reduce_df(df, col, col_value, col2, col2_value):
    '''Reduce df to include only rows that contain a certain value'''
    reduced = df[df[col]==col_value].reset_index(drop=True)
    return reduced[reduced[col2]==col2_value].reset_index(drop=True)

def counting(vals_list):
    '''Count'''
    lab=[]
    cts=[]
    for k,v in Counter(vals_list).items():
        lab.append(k)
        cts.append(v)
    return lab, cts

def piecharts(df):
    '''Pie charts. Hardcoded col names'''
    fig = make_subplots(rows=1, cols=3, specs=[[{'type':'domain'},{'type':'domain'},{'type':'domain'}]])
    lab,cts=counting(df['response'].dropna())
    fig.add_trace(go.Pie(labels=lab, values=cts,textinfo='label+percent', name="Drug Response",legendgroup='group1',showlegend=True),1, 1)
    lab,cts=counting(df['source'].dropna())
    fig.add_trace(go.Pie(labels=lab, values=cts,textinfo='label+percent', name="Source",legendgroup='group2',showlegend=True),1, 2)
    lab,cts=counting(df['evidence label'].dropna())
    fig.add_trace(go.Pie(labels=lab, values=cts,textinfo='label+percent', name="Source Strength",legendgroup='group1',showlegend=True),1, 3)
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(height=150,showlegend=False,margin={'t':0, 'b':0,'r':0,'l':0})
    return fig
    
def card(k,v,graph_font,h):
    '''Input text to display (k), numeric value (v), and plot height'''
    label = k
    lay = go.Layout(margin={'t':0,'b':0, 'l':0,'r':0},height=h,font=dict(family=graph_font,size=8,color='black'))
    fig = go.Figure(go.Indicator(
        mode = "number",
        value = v,
        number = {'suffix': " {}".format(label)},
            domain = {'x': [0, 1], 'y': [0, 1]}))
    return fig 
        
def get_baseDF():
    '''Get base df of all gene drug combos that user can select from'''
    q=G.query().V().hasLabel('Gene').as_('g').limit(1000).out('g2p_associations').as_('lit').out('compounds').as_('c')
    q=q.render(['$g._gid','$g._data.symbol','$c._gid','$c._data.synonym','$lit._data.evidence_label','$lit._data.response_type', '$lit._data.source', '$lit._data.source_document'])
    a=[]
    b=[]
    c=[]
    d=[]
    e=[]
    f=[]
    g=[]
    h=[]
    for row in q:
        gene_id, gene, drug_id, drug, lit_evid, lit_resp, src, lit_etc= row
        if drug is not None and lit_evid is not None and lit_resp is not None and src is not None:
            a.append(gene_id)
            b.append(gene)
            c.append(drug_id)
            d.append(drug)
            e.append(lit_evid)
            f.append(lit_resp)
            g.append(src)
            h.append(lit_etc)
    return pd.DataFrame(list(zip(a,b,c,d,e,f,g,h)),columns=['geneID','gene','drugID','drug', 'evidence label','response','source','litETC'])

def get_resultsDict(df,colname):
    '''Info stored in source doc property. Hardcoded col name'''
    # TODO update this to handle other keys too (non-clinical)
    res_dict = {}
    for i in range(0, len(df[colname])):
        info = df[colname][i]
        doc_dict = json.loads(info) 
        if 'clinical' in doc_dict:
            data = doc_dict['clinical']
            for k,v in data.items():
                if k not in res_dict:
                    if k =='drugAbstracts':
                        res_dict[k]=[v[0]['link']]
                    else:
                        res_dict[k]=[v]
                else:
                    if k =='drugAbstracts':
                        res_dict[k].append(v[0]['link'])
                    else:
                        res_dict[k].append(v)
    return res_dict
    
def build_publication_table(res_dict):
    '''Build publication table ['Cancer Studied', 'Evidence Level','Evidence Meaning','Study']'''
    if 'cancerType' in res_dict:
        return pd.DataFrame(list(zip(res_dict['cancerType'],res_dict['level'],res_dict['level_label'],res_dict['drugAbstracts'])),columns=['Cancer Studied', 'Evidence Level','Evidence Meaning','Study'])
    else:
        return pd.DataFrame((['-','-','-','-'],['-','-','-','-'],['-','-','-','-'],['-','-','-','-']),columns=['Cancer Studied', 'Evidence Level','Evidence Meaning','Study'])

def pull_data(res_dict,variant_key1,variant_key2, level):
    '''Pull variant information'''
    if 'variant' in res_dict:
        if level == 2:
            return [res_dict['variant'][i][variant_key1][variant_key2] for i in range(0,len(res_dict['variant']))]
        else:
            return [res_dict['variant'][i][variant_key1] for i in range(0,len(res_dict['variant']))]
    else:
        return {}
    
def build_bio_table(res_dict):
    '''Build biological relevance table ['Curated Isoform','Gene Alias','Gene Info','Oncogene','TS Gene','Gene Alteration', 'Alteration Type','Alteration Description']'''
    if 'variant' in res_dict:
        iso=pull_data(res_dict, 'gene','curatedIsoform',2)   
        alia=[str(a).replace("\'",'').strip('[').strip(']')  for a in pull_data(res_dict, 'gene','geneAliases',2) ]
        nm = [a.capitalize() for a in pull_data(res_dict, 'gene','name',2)]  
        og=pull_data(res_dict, 'gene','oncogene',2)
        tsupg=pull_data(res_dict, 'gene','tsg',2)  
        alter=pull_data(res_dict, 'alteration','',1) 
        alter_term=pull_data(res_dict, 'consequence','term',2)
        desp=pull_data(res_dict, 'consequence','description',2)  
        return pd.DataFrame(list(zip(iso,alia,nm,og,tsupg,alter,alter_term,desp)),columns=['Curated Isoform','Gene Alias','Gene Info','Oncogene','TS Gene','Gene Alteration', 'Alteration Type','Alteration Description'])
    else:
        return pd.DataFrame((['-','-','-','-','-','-','-','-'],['-','-','-','-','-','-','-','-'],['-','-','-','-','-','-','-','-']),columns=['Curated Isoform','Gene Alias','Gene Info','Oncogene','Tumor Suppressor Gene','Gene Alteration', 'Alteration Type','Alteration Description'])
