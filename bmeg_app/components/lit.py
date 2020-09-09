from ..db import G
import pandas as pd
import gripql

def gene_dd_selections(df, colKEY, colVALUE):
    '''
    Input gene options
    '''
    dict1 = dict(zip(df[colKEY],df[colVALUE]))
    return dict1
    
    
def drug_dd_selections(selected_gene, colKEY, colVALUE, baseDF):
    '''
    Get drug selections avail for the user selected gene
    '''
    filtered1= baseDF[baseDF['geneID']==selected_gene].reset_index(drop=True)
    dict1 = dict(zip(filtered1[colKEY],filtered1[colVALUE]))
    return dict1
    
    
def reduce_df(df, col, col_value, col2, col2_value):
    '''reduce df to include only rows that contain a certain value'''
    reduced = df[df[col]==col_value].reset_index(drop=True)
    return reduced[reduced[col2]==col2_value].reset_index(drop=True)

def counting(vals_list):
    '''
    ex. counting(res['Gender'])
    '''
    from collections import Counter
    lab=[]
    cts=[]
    for k,v in Counter(vals_list).items():
        lab.append(k)
        cts.append(v)
    return lab, cts

def piecharts(df):
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    # Pie charts
    fig = make_subplots(rows=3, cols=1, specs=[[{'type':'domain'}], [{'type':'domain'}],[{'type':'domain'}]])
    lab,cts=counting(df['response'].dropna())
    fig.add_trace(go.Pie(labels=lab, values=cts,textinfo='label+percent', name="Drug Response",legendgroup='group1',showlegend=True),1, 1)
    lab,cts=counting(df['source'].dropna())
    fig.add_trace(go.Pie(labels=lab, values=cts,textinfo='label+percent', name="Source",legendgroup='group2',showlegend=True),2, 1)
    lab,cts=counting(df['evidence label'].dropna())
    fig.add_trace(go.Pie(labels=lab, values=cts,textinfo='label+percent', name="Source Strength",legendgroup='group1',showlegend=True),3, 1)
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(showlegend=False,margin={'t':0, 'b':0,'r':0,'l':0})
    return fig
    
def card(k,v,graph_font,h):
    '''
    input text to display (k), numeric value (v), and plot height
    '''
    import plotly.graph_objects as go
    label = k
    lay = go.Layout(margin={'t':0,'b':0, 'l':0,'r':0},height=h,font=dict(family=graph_font,size=8,color='black'))
    gofig = go.Figure(go.Indicator(
        mode = "number",
        value = v,
        number = {'suffix': " {}".format(label)},
            domain = {'x': [0, 1], 'y': [0, 1]}))
    return gofig 
    
    
def source_document_info(DF, colname):
    '''
    '''
    import json
    new_entry =[]
    body_string = []

    for i in range(0, len(DF['litETC'])):
        info = DF[colname][i]
        textDict = json.loads(info) 

        # TODO change this for alltypes
        if 'clinical' in textDict:
            data = textDict['clinical']
            for k,v in data.items():
                if k != 'drugAbstracts':
                    new_entry.append(str(k)+':'+str(v))
                    #print(k,':', v)

            assert 'drugAbstracts' in data, 'no link provided'
            urlLink = data['drugAbstracts'][0]['link']
            new_entry.append(urlLink)
            #print(urlLink)
            #print()
            body_string.append('\n'.join(new_entry) )
        else:
            pass
    return body_string
    
    
    
# def gene_dd_selections():
#     '''
#     Get dictionary of gene dropdown selections 
#     '''
#     # # TODO cache selections so can remove limit in query
#     # q= G.query().V().hasLabel('Gene').limit(150).as_('gene').out('g2p_associations').as_('lit').out('compounds').as_('comp').out('drug_responses')
#     # q= q.render(['$gene._gid','$lit._data.response_type'])
#     # gene_options={}
#     # for a,b in q:
#     #     gene_options[a]=1
# 
#     # temp for testing 
#     gene_options={'ENSG00000132781':1, 'ENSG00000163531':1}
#     return gene_options

# def drug_dd_selections(gene):
#     '''
#     Get dictionary of drug dropdown selections
#     '''
#     # TODO change to query instead of hardcoded drug options 
#     if gene == 'ENSG00000132781':
#         drug_options={'OLAPARIB':'OLAPARIB', 'Epirubicin':'Epirubicin'} #todo replace with gid as key
#     elif gene == 'ENSG00000163531':
#         drug_options={'SIROLIMUS': 'SIROLIMUS',
#             'TESTOSTERONE': 'TESTOSTERONE',
#             'OBINUTUZUMAB': 'OBINUTUZUMAB',
#             'EVEROLIMUS': 'EVEROLIMUS',
#             'Cyclophosphamide': 'Cyclophosphamide',
#             'ARGININE HYDROCHLORIDE': 'ARGININE HYDROCHLORIDE',
#             'BEVACIZUMAB': 'BEVACIZUMAB',
#             'Imatinib': 'Imatinib',
#             'CARBOPLATIN': 'CARBOPLATIN',
#             'SUNITINIB': 'SUNITINIB',
#             'ETOPOSIDE': 'ETOPOSIDE',
#             'CHEMBL2108950': 'CHEMBL2108950',
#             'PIOGLITAZONE': 'PIOGLITAZONE',
#             'LOVASTATIN': 'LOVASTATIN',
#             '445419': '445419',
#             'TESTOSTERONE PROPIONATE': 'TESTOSTERONE PROPIONATE',
#             'BLOOD CELLS, RED': 'BLOOD CELLS, RED',
#             'Fludarabine': 'Fludarabine',
#             'RITUXIMAB': 'RITUXIMAB',
#             'NAFOMINE MALATE': 'NAFOMINE MALATE',
#             'VALPROIC ACID': 'VALPROIC ACID',
#             'CETUXIMAB': 'CETUXIMAB',
#             'TEMSIROLIMUS': 'TEMSIROLIMUS',
#             'CAMAZEPAM': 'CAMAZEPAM',
#             'MESNA': 'MESNA',
#             'PEMBROLIZUMAB': 'PEMBROLIZUMAB',
#             'VISMODEGIB': 'VISMODEGIB',
#             'CHEMBL3544967': 'CHEMBL3544967',
#             'FENTANYL': 'FENTANYL',
#             'Vincristine': 'Vincristine',
#             'ALDESLEUKIN': 'ALDESLEUKIN',
#             'SELUMETINIB': 'SELUMETINIB',
#             'VEDOTIN': 'VEDOTIN',
#             '15983966': '15983966',
#             '101743': '101743'}
#     return drug_options


def get_baseDF():
    '''
    TODO: cache df istead of query on the fly 
    
    Get base df of all gene drug combos that user can select from 
    '''
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
        geneID, gene, drugID, drug, lit_evid, lit_resp, src, lit_etc= row
        if drug is not None and lit_evid is not None and lit_resp is not None and src is not None:
            a.append(geneID)
            b.append(gene)
            c.append(drugID)
            d.append(drug)
            e.append(lit_evid)
            f.append(lit_resp)
            g.append(src)
            h.append(lit_etc)
    return pd.DataFrame(list(zip(a,b,c,d,e,f,g,h)),columns=['geneID','gene','drugID','drug', 'evidence label','response','source','litETC'])




    
        
def fullDF(response_metric,select_genes):
    '''
    input list of genes that want to look for g2p response 
    output pandas df, eg ENSG00000050628
    '''
    conversion = {'EC50':'$dr._data.ec50', 'AAC':'$dr._data.aac'}

    if len(select_genes)>=1:
        for i in range(0, len(select_genes)):
            if i == 0:
                gene=select_genes[i]
                q= G.query().V().hasLabel('Gene').has(gripql.eq('$._gid', gene)).limit(150).as_('gene').out('g2p_associations').as_('lit').out('compounds').as_('comp').out('drug_responses').as_('dr')
                q = q.render(['$gene._gid','$gene._data.symbol', '$lit._data.source', '$lit._data.description','$dr._data.source_cell_name','$comp._data.synonym',conversion[response_metric],'$dr._data.project_id','$lit._data.response_type'])
                gene_gid=[]
                gene_sym=[]
                lit_src=[]
                lit_des=[]
                dr_cellline=[]
                comp_syn=[]
                dr_metric=[]
                dr_projid=[]
                lit_resptype=[]                
                for i in q:
                    gene_gid.append(i[0])
                    gene_sym.append(i[1])
                    lit_src.append(i[2])
                    lit_des.append(i[3])
                    dr_cellline.append(i[4])
                    comp_syn.append(i[5])
                    dr_metric.append(i[6])
                    dr_projid.append(i[7])
                    lit_resptype.append(i[8])
                df=pd.DataFrame(list(zip(gene_gid,gene_sym,lit_src,lit_des,dr_cellline,comp_syn,dr_metric,dr_projid,lit_resptype)),columns=['Ensembl ID','Gene Symbol','Source','Description','Cell Line','Drug Compound','dr_metric','Dataset','Response Type'])
            else:
                gene=select_genes[i]
                q= G.query().V().hasLabel('Gene').has(gripql.eq('$._gid', gene)).limit(150).as_('gene').out('g2p_associations').as_('lit').out('compounds').as_('comp').out('drug_responses').as_('dr')
                q = q.render(['$gene._gid','$gene._data.symbol', '$lit._data.source', '$lit._data.description','$dr._data.source_cell_name','$comp._data.synonym',conversion[response_metric],'$dr._data.project_id','$lit._data.response_type'])
                gene_gid=[]
                gene_sym=[]
                lit_src=[]
                lit_des=[]
                dr_cellline=[]
                comp_syn=[]
                dr_metric=[]
                dr_projid=[]
                lit_resptype=[]                
                for i in q:
                    gene_gid.append(i[0])
                    gene_sym.append(i[1])
                    lit_src.append(i[2])
                    lit_des.append(i[3])
                    dr_cellline.append(i[4])
                    comp_syn.append(i[5])
                    dr_metric.append(i[6])
                    dr_projid.append(i[7])
                    lit_resptype.append(i[8])
                df2=pd.DataFrame(list(zip(gene_gid,gene_sym,lit_src,lit_des,dr_cellline,comp_syn,dr_metric,dr_projid,lit_resptype)),columns=['Ensembl ID','Gene Symbol','Source','Description','Cell Line','Drug Compound','dr_metric','Dataset','Response Type'])
                df=pd.concat([df,df2],ignore_index=True).reset_index(drop=True)  
        df.insert(loc=0, column='i', value=list(range(0,df.shape[0])))
    elif len(select_genes)==0:    
        df=pd.DataFrame((),columns=['i','Ensembl ID','Gene Symbol','Source','Description','Cell Line','Drug Compound','dr_metric','Dataset','Response Type'])
    return df
