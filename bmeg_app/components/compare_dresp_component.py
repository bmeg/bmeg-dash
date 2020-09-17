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
        
def get_table(df,disease):
    '''Melt df'''
    df['Cell Line']=df.index
    df= df.melt(id_vars=['Cell Line'])
    df.columns=['Cell Line', 'Drug', 'Drug Response']
    return df
        
def violins(compound,df,y_axis_label):
    '''Violin plots'''
    compound = G.query().V(compound).render(['$._data.synonym']).execute()[0][0]
    fig = go.Figure()
    drugs = list(set(df['Drug']))
    assert compound in drugs
    drugs.remove(compound)
    drugs.insert(0,compound)
    for d in drugs:
        fig.add_trace(go.Violin(x=df['Drug'][df['Drug'] == d],y=df['Drug Response'][df['Drug'] == d],name=d,box_visible=True,meanline_visible=True))
    fig.update_layout(margin={'t':10, 'b':10},height=400,yaxis=dict(title=y_axis_label))
    fig.update_xaxes(tickangle=45)
    fig.update_layout(showlegend=False)
    return fig

def options_project():
    '''Project dropdown menu options'''
    project_label=['CCLE'] # TODO incorp CTRP and GDSC and check all downstream queries
    options ={}
    for row in G.query().V().hasLabel('Project').render(['$._gid']):
        if project_label[0] in row[0]:
            options[row[0]]=project_label[0]
    return options

def options_disease(selected_project):
    '''Disease dropdown menu options'''
    options={}
    for row in G.query().V(selected_project).out("cases").render(['$._data.cellline_attributes.Primary Disease']):
        if row[0] is not None and row[0]!='Unknown':
            options[row[0]]=''
    return options

def options_drug(selected_project):
    '''Drug dropdown menu options. If no synonym then use GID'''
    options={}
    if selected_project=='Project:CCLE':
        for row in G.query().V('Project:CCLE').out("cases").as_("p").out("samples").out("aliquots").out("drug_response").as_("dr").out("compounds").as_("c").render(['$._gid','$._data.synonym']):
            if row[1] is None:
                options[row[0]]=row[0]
            else:
                options[row[0]]=row[1].capitalize()
    # TODO add elif other project...load project specific properties
    return options

def options_dresp(selected_project):
    '''Drug response dropdown menu options'''
    if 'Project:CCLE' == selected_project:
        options = {
            'AAC':'$dr._data.aac',
            'IC50':'$dr._data.ic50',
            'EC50': '$dr._data.ec50'
             }
        return options
    #elif other project...load project specific properties

def drugDetails(drugs_list):
    '''Drug property table'''
    q=G.query().V(drugs_list).render(['$._data.synonym','$._data.pubchem_id','$._data.taxonomy.direct-parent','$._data.taxonomy.kingdom','$._data.taxonomy.superclass','$._data.taxonomy.class','$._data.taxonomy.subclass','$._data.taxonomy.description','$._gid'])
    a=[]
    b=[]
    c=[]
    d=[]
    e=[]
    f=[]
    g=[]
    for row in q:
        if row[0] is None: # Drug has no common name
            a.append(row[7])
            b.append(row[1])
            c.append(row[2])
            d.append(row[3])
            e.append(row[4])
            f.append(row[5])
            g.append(row[6])
        else:            
            a.append(row[0])
            b.append(row[1])
            c.append(row[2])
            d.append(row[3])
            e.append(row[4])
            f.append(row[5])
            g.append(row[6])
    df = pd.DataFrame(list(zip(a,b,c,d,e,f,g)),columns=['Drug','PubChem ID','Direct Parent','Kingdom','Superclass','Class','Subclass'])
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
