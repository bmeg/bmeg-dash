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
    q=G.query().V().hasLabel('G2PAssociation').as_('lit') \
        .out('compounds').as_('c') \
        .select('lit').out('genes').as_('g') \
        .select('lit').out('publications').as_('publ')
    q=q.render([
        '$g._gid','$g._data.symbol',
        '$c._gid','$c._data.synonym',
        '$lit._data.evidence_label','$lit._data.response_type', '$lit._data.source',
        '$publ._data.author','$publ._data.date','$publ._data.url'
    ])
    a=[]
    b=[]
    c=[]
    d=[]
    e=[]
    f=[]
    g=[]
    h=[]
    i=[]
    j=[]
    for row in q:
        gene_id, gene, drug_id, drug, lit_evid, lit_resp, src, author, date, url= row
        if lit_resp is not None and url is not None and drug is not None and lit_evid is not None and src is not None:
            a.append(gene_id)
            b.append(gene)
            c.append(drug_id)
            d.append(drug)
            e.append(lit_evid)
            f.append(lit_resp)
            g.append(src)
            h.append(author)
            i.append(date)
            j.append(url)
    return pd.DataFrame(list(zip(a,b,c,d,e,f,g,h,i,j)),columns=['geneID','gene','drugID','drug', 'evidence label','response','source','author','date','url'])

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

def occurances_table(input_df, colname, out_cols):
    '''base df and colname that want to count, list of output cols'''
    from collections import Counter
    col1=[]
    col2=[]
    for k,v in Counter(input_df[colname]).items():
        col1.append(k)
        col2.append(v)
    df = pd.DataFrame(list(zip(col1,col2)),columns=out_cols)
    return df

def count_taxonomy(df):
    '''Create conversion of compoundID to taxonomy and count'''
    from collections import Counter
    comp2sclass={}
    for gid,tax in G.query().V(list(df['drugID'])).render(['$._gid','$._data.taxonomy.superclass']):
        if tax is None:
            tax='None Listed'
        comp2sclass[gid]=tax
    tax_list=[]
    for c in df['drugID']:
        tax_list.append(comp2sclass.get(c))
    return Counter(tax_list)

def pie_from_dict(dictionary,legend):
    '''Dictionary k,v are label and total counts. Legend True or False to show'''
    import plotly.graph_objects as go
    l=[]
    ct=[]
    for k,v in dictionary.items():
        l.append(k)
        ct.append(v)
    fig_data=go.Pie(labels=l, values=ct,textinfo='label+percent',legendgroup='group1',showlegend=legend)
    fig_layout=go.Layout(margin={'t':0, 'b':0,'r':0,'l':0})
    fig = go.Figure(data=fig_data,layout=fig_layout)
    return fig

def get_histogram_side(data,box_color):
    '''
    input values to plot. can be pandas df['col']
     returns go figure
    '''
    import pandas as pd
    import plotly.graph_objects as go
    fig = go.Figure(data=[go.Histogram(y=data,marker=dict(color=box_color))]).update_yaxes(categoryorder="total ascending")
    fig.update_layout(margin={'t':0, 'b':0},
        yaxis=dict(tickmode='linear'),
        plot_bgcolor='white',
        paper_bgcolor='white')
    fig.update_xaxes(showline=True,linewidth=1,ticks='outside',linecolor='black')
    fig.update_yaxes(showline=True,linewidth=1,ticks='outside',linecolor='black')
    return fig
