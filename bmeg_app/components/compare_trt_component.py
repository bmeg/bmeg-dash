from ..db import G
import gripql 
import pandas as pd 
from collections import Counter
import plotly.graph_objects as go
from plotly.subplots import make_subplots
    
def line2disease(CELLLINES):
    '''Dictionary mapping cell line GID to reported primary disease'''
    # some vals are None
    disease_dict = {}
    q=G.query().V(CELLLINES).render(["$._gid",'$._data.cellline_attributes.Primary Disease'])
    for row in q:
        disease_dict[row[0]]=row[1]
    return disease_dict


def get_base_matrix(PROJECT, DRUGRESPONSE,est,selected_disease):
    '''Get row col matrix of cell line vs drug for a specific project'''   
    # Query results
    q1 = G.query().V(PROJECT).out("cases").as_("ca").out("samples").out("aliquots").out("drug_response").as_("dr").out("compounds").as_("c")
    q1 = q1.render(["$ca._gid", "$c._gid", DRUGRESPONSE])
    data = {}
    for row in q1:
        if row[0] not in data: 
            data[row[0]] = { row[1] :  row[2] } 
        else: 
            data[row[0]][row[1]] = row[2]  
    drugDF = pd.DataFrame(data).transpose()
    drugDF = drugDF.sort_index().sort_index(axis=1) #sort by rows, cols
    # create disease mapping dict
    disease =line2disease(list(drugDF.index))
    # exclude non disease related derived cell lines
    new_col=[]
    for a in list(drugDF.index):
        new_col.append(disease.get(a))
    drugDF['disease']=new_col
    subsetDF=drugDF[drugDF['disease']==selected_disease]
    # set established drug to first col and rm disease col
    new_col=subsetDF.pop(est)
    subsetDF.insert(0, est, new_col)
    subsetDF.pop('disease')
    return subsetDF
    
    
def get_table(df,disease,fig_yaxisLabel):
    '''Return melted df'''
    df['Cell Line']=df.index
    df= df.melt(id_vars=['Cell Line'])
    df.columns=['Cell Line', 'Drug', 'Drug Response']
    return df
    
    
def violins(compound,df,fig_yaxisLabel):
    '''    '''
    import plotly.graph_objects as go
    import pandas as pd
    compound = G.query().V(compound).render(['$._data.synonym']).execute()[0][0]

    # Generate violin plots
    fig = go.Figure()
    drugs = list(set(df['Drug']))
    assert compound in drugs
    drugs.remove(compound)
    drugs.insert(0,compound) # place established drug at index0

    for d in drugs:
        fig.add_trace(go.Violin(x=df['Drug'][df['Drug'] == d],
                                y=df['Drug Response'][df['Drug'] == d],
                                name=d,box_visible=True,meanline_visible=True))
    fig.update_layout(margin={'t':10, 'b':10},height=400,yaxis=dict(title=fig_yaxisLabel))
    fig.update_xaxes(tickangle=45)
    fig.update_layout(showlegend=False)
    return fig


def options_project():
    '''project dropdown menu options '''
    project_label=['CCLE'] # TODO incorp CTRP and GDSC and check all downstream queries
    options ={}
    for row in G.query().V().hasLabel('Project').render(['$._gid']):
        if project_label[0] in row[0]:
            options[row[0]]=project_label[0]
    return options

def options_disease(selected_project):
    '''disease dropdown menu options'''
    options={}
    for row in G.query().V(selected_project).out("cases").render(['$._data.cellline_attributes.Primary Disease']):
        if row[0] is not None and row[0]!='Unknown':
            options[row[0]]=''
    return options

def options_drug(selected_project):
    '''drug dropdown menu options. if no synonym then use GID'''
    options={}
    if selected_project=='Project:CCLE':
        for row in G.query().V('Project:CCLE').out("cases").as_("p").out("samples").out("aliquots").out("drug_response").as_("dr").out("compounds").as_("c").render(['$._gid','$._data.synonym']):
            if row[1] is None:
                options[row[0]]=row[0]
            else:
                options[row[0]]=row[1].capitalize()
    # TODO add elif other project...load project specific properties
    return options

    
def mappings_drugResp(selected_project):
    if 'Project:CCLE' == selected_project:
        options = {
            'AAC':'$dr._data.aac',
            'IC50':'$dr._data.ic50',
            'EC50': '$dr._data.ec50'
             }
        return options
    #elif other project...load project specific properties

def drugDetails(drugs_list):
    '''
    create table of drugs and their taxon.
    '''
    a=[]
    b=[]
    c=[]
    d=[]
    e=[]
    f=[]
    g=[]
    for DRUG in drugs_list:
        q=G.query().V().hasLabel('Compound').has(gripql.eq('_data.synonym', DRUG))
        q=q.render(['_data.synonym','_data.pubchem_id','_data.taxonomy.direct-parent','_data.taxonomy.kingdom','_data.taxonomy.superclass','_data.taxonomy.class','_data.taxonomy.subclass','_data.taxonomy.description'])
        for row in q:
            a.append(row[0])
            b.append(row[1])
            c.append(row[2])
            d.append(row[3])
            e.append(row[4])
            f.append(row[5])
            g.append(row[6])
    df = pd.DataFrame(list(zip(a,b,c,d,e,f,g)),columns=['Drug','PubChem ID','Direct Parent','Kingdom','Superclass','Class','Subclass'])
    df.to_csv('CHECKING_ORIGINAL.tsv',sep='\t')
    return df

def counting(vals_list):
    '''
    ex. counting(res['Gender'])
    '''
    lab=[]
    cts=[]
    for k,v in Counter(vals_list).items():
        lab.append(k)
        cts.append(v)
    return lab, cts

def get_histogram_normal(data):
    '''
    input values to plot. can be pandas df['col']
    yticks == how far apart ticks
     returns go figure
    '''
    import pandas as pd
    import plotly.graph_objects as go
    fig = go.Figure(data=[go.Histogram(
        x=data,
        #marker=dict(color=box_color)
        )]).update_xaxes(categoryorder="total descending")
    fig.update_layout(margin={'t':0, 'b':0},
        height=200,
        yaxis=dict(tickmode='linear'),
        #plot_bgcolor='white'
    )
    fig.update_xaxes(showticklabels=False)
    fig.update_yaxes(showticklabels=False)
    return fig
    
def sample_table(df):
    '''table of pie chart details. cols [Cell Line,Drug,Drug Response,Gender,Subtype,Disease Subtype]'''
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
    fig = make_subplots(rows=1, cols=2, specs=[[{'type':'domain'}, {'type':'domain'}]])
    lab,cts=counting(df['Gender'])
    fig.add_trace(go.Pie(labels=lab, values=cts,textinfo='label+percent', name="Gender",legendgroup='group1',showlegend=True),1, 1)
    lab,cts=counting(df['Disease Subtype'])
    fig.add_trace(go.Pie(labels=lab, values=cts,textinfo='label+percent', name="Gender",legendgroup='group2',showlegend=True),1, 2)
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(showlegend=False,margin={'t':0, 'b':0,'r':0,'l':0})
    return fig    
