from ..db import G
from collections import Counter
import gripql
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def line2disease(lines_list):
    '''Dictionary mapping cell line GIDs to reported primary disease'''
    disease_dict = {}
    q=G.query().V(lines_list).render(["$._gid",'$._data.cellline_attributes.Primary Disease'])
    for row in q:
        disease_dict[row[0]]=row[1] # some vals are None
    return disease_dict

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

def get_table(df):
    '''Melt df'''
    df['Cell Line']=df.index
    df= df.melt(id_vars=['Cell Line'])
    df.columns=['Cell Line', 'Drug', 'Drug Response']
    return df

def dresp_pairs(df,drug1,drug2,dresp):
    '''Pairwise drug response plots'''
    dresp=dresp.split('.')[2].upper()
    drug1_resp = df[df['Drug']==drug1]['Drug Response']
    drug2_resp = df[df['Drug']==drug2]['Drug Response']
    fig = go.Figure(data=go.Scatter(x=drug1_resp,y=drug2_resp,mode='markers'))
    fig.update_layout(margin={'t':15, 'b':15,'r':15,'l':15},xaxis_title=drug1+' '+dresp,yaxis_title=drug2+' '+dresp)
    return fig

def options_disease(selected_project):
    '''Get all diseases for a project'''
    options=[]
    for row in G.query().V(selected_project).out("cases").render(['$._data.cellline_attributes.Primary Disease']):
        if row[0] is not None and row[0].lower()!='unknown' and row[0] not in options:
            # options[row[0]]=''
            options.append(row[0])
    options.sort()
    return options

def get_project_drugs(selected_project):
    '''Drug dropdown menu options. If no synonym then use GID'''
    options={}
    for row in G.query().V(selected_project).out("compounds").render(['$._gid','$._data.synonym']):
        if 'Compound:NO_ONTOLOGY' not in row[0]:
            if row[1] is None:
                options[row[0]]=row[0]
            else:
                options[row[0]]=row[1].capitalize()
    return options

def get_project_aliquot_disease(project):
    q = G.query().V("Project:CCLE").out("cases").as_("case").out("samples").out("aliquots").as_("al").render(["$al._gid", "$case.cellline_attributes.Primary Disease"])
    return dict(list(q))

def options_drug2(drug_list):
    '''Dictionary mapping cell line GIDs to reported primary disease'''
    disease_dict = {}
    for row in G.query().V(drug_list).render(["$._gid",'$._data.synonym']):
        if 'Compound:NO_ONTOLOGY' not in row[0]:
            if row[1] is None:
                disease_dict[row[0]]=row[0]
            else:
                disease_dict[row[0]]=row[1].capitalize()
    return disease_dict

def get_project_compound_dr(project, compound, dr):
    q = G.query().V(compound).out("drug_responses")
    q = q.has(gripql.eq("project_id", "Project:CCLE")).as_("dr")
    q = q.out("aliquot").as_("a").render(["$a._gid", "$dr." + dr])
    return dict(q)

def drugDetails(drugs_list):
    '''Drug property table'''
    mapping = {
        "Drug" : '$.synonym',
        "PubChem ID" : '$.pubchem_id',
        'Direct Parent' : '$.taxonomy.direct-parent',
        'Kingdom' : '$.taxonomy.kingdom',
        'Superclass' : '$.taxonomy.superclass',
        'Class' : '$.taxonomy.class',
        'Subclass' : '$.taxonomy.subclass',
        "Description" : '$.taxonomy.description',
        "gid" : '$._gid'
    }
    q=G.query().V(drugs_list).render(mapping)
    data = []
    for row in q:
        data.append(row)
    df = pd.DataFrame(data)
    return df

def counting(vals_list):
    '''Count'''
    lab=[]
    cts=[]
    for k,v in Counter(vals_list).items():
        lab.append(k)
        cts.append(v)
    return lab, cts

def sample_table(df):
    '''Table of pie chart details. cols [Cell Line,Drug,Drug Response,Gender,Subtype,Disease Subtype]'''
    lookup={}
    for row in G.query().V(list(df['Cell Line'])).render(['$._gid','$._data.cellline_attributes.Gender','$._data.cellline_attributes.Subtype Disease']):
        lookup[row[0]]=[row[1],row[2]]
    new_col1=[]
    new_col2=[]
    for c in df['Cell Line']:
        new_col1.append(lookup.get(c)[0])
        new_col2.append(lookup.get(c)[1])
    df['Gender']=new_col1
    df['Disease Subtype']=new_col2
    df['Drug'] = df['Drug'].str.capitalize()
    df= df.sort_values(by='Drug Response', ascending=True).reset_index(drop=True)
    return df

def piecharts_celllines(df):
    '''Pie chart'''
    fig = make_subplots(rows=1, cols=2, specs=[[{'type':'domain'}, {'type':'domain'}]])
    lab,cts=counting(df['Gender'])
    fig.add_trace(go.Pie(labels=lab, values=cts,textinfo='label+percent', name="Gender",legendgroup='group1',showlegend=True),1, 1)
    lab,cts=counting(df['Disease Subtype'])
    fig.add_trace(go.Pie(labels=lab, values=cts,textinfo='label+percent', name="Gender",legendgroup='group2',showlegend=True),1, 2)
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(showlegend=False,margin={'t':0, 'b':0,'r':0,'l':0})
    return fig
