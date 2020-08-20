from ..db import G

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

def compare_drugs(est,drugDF,disease,fig_yaxisLabel):
    '''
    ex. compare_drugs('PACLITAXEL',drugDF,disease)
    '''
    import plotly.graph_objects as go
    import pandas as pd
    # exclude non-breast cancer derived cell lines
    new_col=[]
    for ind in drugDF.index:
        new_col.append(disease[ind])
    drugDF['disease']=new_col
    drugDF=drugDF[drugDF['disease']=='Breast Cancer']
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
    return melt_drugDF, fig


def mappings(selected_project):
    if 'CCLE' == selected_project:
        return {
        'Paclitaxel':'PACLITAXEL',
        'Nilotinib':'NILOTINIB'
         }
    #elif other project...load project specific properties
def mappings_drugResp(selected_project):
    if 'CCLE' == selected_project:
        return {
        'AAC':'$dr._data.aac',
        'IC50':'$dr._data.ic50',
        'EC50': '$dr._data.ec50'
         }
    #elif other project...load project specific properties
