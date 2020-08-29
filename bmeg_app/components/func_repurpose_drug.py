from ..db import G
import gripql 
import pandas as pd 
from collections import Counter
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def get_matrix(PROJECT, DRUGRESPONSE):
    '''
    Get row col matrix of cell line vs drug for a specific project. And return dictionary of cellline_caseid:disease state
    ex. get_matrix('CCLE','$dr._data.aac')
    
    disease state
    {'ACH-000956': 'Prostate Cancer',
     'ACH-002219': 'Colon/Colorectal Cancer',...}
    '''
    import gripql
    import pandas as pd 
    p1 = []
    for row in G.query().V().hasLabel("Project"): #start query at vertex and look for labels starting with Project
        if row.data.project_id.startswith(PROJECT):
            p1.append(row.gid)
            
    #Drug Matrix == Project > **Case** > Sample > Aliquot > **DrugResponse** > **Compound**
    q1 = G.query().V(p1).out("cases").as_("p").out("samples").out("aliquots").out("drug_response").as_("dr").out("compounds").as_("c")
    q1 = q1.render(["$p._data.case_id", "$c._gid", DRUGRESPONSE,"$p._data.cellline_attributes.Primary Disease"])
    data = {}
    disease = {}
    for row in q1:
        disease[row[0]]=row[3]
        if row[0] not in data: 
            data[row[0]] = { row[1] :  row[2] } 
        else: 
            data[row[0]][row[1]] = row[2]  
    drugDF = pd.DataFrame(data).transpose()
    drugDF = drugDF.sort_index().sort_index(axis=1) #sort rows by cell line name, sort cols by drug name
    return drugDF, disease

def compare_drugs(est,drugDF,disease,fig_yaxisLabel, selected_disease):
    '''
    ex. compare_drugs('PACLITAXEL',drugDF,disease,'Breast Cancer')
    '''
    import plotly.graph_objects as go
    import pandas as pd
    # exclude non-breast cancer derived cell lines
    new_col=[]
    for ind in drugDF.index:
        new_col.append(disease[ind])
    drugDF['disease']=new_col
    drugDF=drugDF[drugDF['disease']==selected_disease]
    # set established drug to first col
    new_col=drugDF.pop(est)
    drugDF.insert(0, est, new_col)
    drugDF.pop('disease')
    # Melt df (cols: cellline, drug, value)
    melt_drugDF= drugDF
    melt_drugDF['Cell Line']=melt_drugDF.index
    melt_drugDF= melt_drugDF.melt(id_vars=['Cell Line'])
    melt_drugDF.columns=['Cell Line', 'Drug', 'Drug Response']
    # Generate violin plots
    fig = go.Figure()
    drugs = list(set(melt_drugDF['Drug']))
    assert est in drugs
    drugs.remove(est)
    drugs.insert(0,est) # place established drug at index0

    for d in drugs:
        fig.add_trace(go.Violin(x=melt_drugDF['Drug'][melt_drugDF['Drug'] == d],
                                y=melt_drugDF['Drug Response'][melt_drugDF['Drug'] == d],
                                name=d,box_visible=True,meanline_visible=True))
    fig.update_layout(margin={'t':10, 'b':10},height=400,yaxis=dict(title=fig_yaxisLabel))
    fig.update_xaxes(tickangle=45)
    fig.update_layout(showlegend=False)
    return melt_drugDF, fig


def mappings(selected_project):
    if 'CCLE' == selected_project:
        q = G.query().V('Project:CCLE').out("cases").as_("p").out("samples").out("aliquots").out("drug_response").as_("dr").out("compounds").as_("c")
        drugRes = q.aggregate(gripql.term("drugs", '_data.synonym')).execute()
        drug_opts = [a['key'].upper() for a in drugRes[0]['drugs']['buckets']]
        drug_opts = {}
        for a in drugRes[0]['drugs']['buckets']:
            drug_opts[a['key'].upper()]= a['key']
        return drug_opts
    #elif other project...load project specific properties
def mappings_drugResp(selected_project):
    if 'CCLE' == selected_project:
        return {
        'AAC':'$dr._data.aac',
        'IC50':'$dr._data.ic50',
        'EC50': '$dr._data.ec50'
         }
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
    
def piecharts_celllines(drug1,df, proj):
    # Grab all cell lines for that selected drug and look up metadata
    # samples = df[df['Drug']==drug1]['Cell Line'].dropna()
    samples = df[df['Drug']==drug1].dropna(subset=['Drug Response'])['Cell Line']
    sample=[]
    a=[]
    b=[]
    c=[]
    for s in samples:
        q=G.query().V().hasLabel('Case').has(gripql.eq('$._data.case_id', s)).has(gripql.eq('$._data.project_id', proj)).as_('c')
        q=q.render(['$c._data.cellline_attributes.Gender','$c._data.cellline_attributes.Subtype Disease'])
        for gender, subtype in q:
            sample.append(s)
            a.append(gender)
            b.append(subtype)
    resDF=pd.DataFrame(list(zip(sample,a,b)),columns=['Cell Line (Sample)','Gender','Subtype'])
    # Pie charts
    fig = make_subplots(rows=1, cols=2, specs=[[{'type':'domain'}, {'type':'domain'}]])
    lab,cts=counting(resDF['Gender'])
    fig.add_trace(go.Pie(labels=lab, values=cts,textinfo='label+percent', name="Gender",legendgroup='group1',showlegend=True),1, 1)
    lab,cts=counting(resDF['Subtype'])
    fig.add_trace(go.Pie(labels=lab, values=cts,textinfo='label+percent', name="Gender",legendgroup='group2',showlegend=True),1, 2)
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(showlegend=False,margin={'t':0, 'b':0,'r':0,'l':0})
    return fig, resDF
