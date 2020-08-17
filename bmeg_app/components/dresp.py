from ..db import G
import pandas as pd
import gripql

def evidenceTable(select_genes):
    '''
    input list of genes that want to look for g2p response 
    output pandas df, eg ENSG00000050628
    '''
    if len(select_genes)>=1:
        for i in range(0, len(select_genes)):
            if i == 0:
                gene=select_genes[i]
                q= G.query().V().hasLabel('Gene').has(gripql.eq('$._gid', gene)).as_('gene').limit(4000).out('g2p_associations').as_('lit').out('compounds').as_('comp')
                q= q.render(['$gene._gid','$gene._data.symbol','$comp._data.synonym', '$lit._data.response_type', '$lit._data.source', '$lit._data.description'])
                col_a=[]
                col_b=[]
                col_c=[]
                col_d=[]
                col_e=[]
                col_f=[]
                for a,b,c,d,e,f in q:
                    if d is not None and d != '':
                        col_a.append(a)
                        col_b.append(b)
                        col_c.append(c)
                        col_d.append(d.upper())
                        col_e.append(e)
                        col_f.append(f)
                df=pd.DataFrame(list(zip(col_a,col_b, col_c, col_d,col_e, col_f)),columns=['EnsemblID','Gene Symbol','Drug Compound','Response Type','Source','Description'])
            else:
                gene=select_genes[i]
                q= G.query().V().hasLabel('Gene').has(gripql.eq('$._gid', gene)).as_('gene').out('g2p_associations').as_('lit').out('compounds').as_('comp')
                q= q.render(['$gene._gid','$gene._data.symbol','$comp._data.synonym', '$lit._data.response_type',  '$lit._data.source', '$lit._data.description'])
                col_a=[]
                col_b=[]
                col_c=[]
                col_d=[]
                col_e=[]
                col_f=[]
                for a,b,c,d,e,f in q:
                    if d is not None and d != '':
                        col_a.append(a)
                        col_b.append(b)
                        col_c.append(c)
                        col_d.append(d.upper())
                        col_e.append(e)
                        col_f.append(f)
                # Store as Pandas DataFrame
                df2=pd.DataFrame(list(zip(col_a,col_b, col_c, col_d,col_e, col_f)),columns=['EnsemblID','Gene Symbol','Drug Compound','Response Type','Source','Description'])
                df=pd.concat([df,df2],ignore_index=True)        
        df= df.sort_values(by=['Drug Compound'], ascending = True).reset_index(drop=True)
        return df
    else:
        return pd.DataFrame((),columns=['EnsemblID','Gene Symbol','Drug Compound','Response Type','Source','Description'])

def drug_response(gene_list, response_metric):
    '''
    input gene and response metric (AAC, EC50)
    '''
    conversion = {'EC50':'$dr._data.ec50', 'AAC':'$dr._data.aac'}
    if len(gene_list)==0:
        return pd.DataFrame((),columns=['Drug Compound','Cell Line', response_metric, 'Dataset'])
    else:
        for i in range(0,len(gene_list)):
            if i==0:
                gene = gene_list[i]
                q= G.query().V().hasLabel('Gene').has(gripql.eq('$._gid', gene)).as_('gene').out('g2p_associations').as_('lit').out('compounds').as_('comp').out('drug_responses').as_('dr')
                q = q.render(['$comp._data.synonym', '$dr._data.source_cell_name',conversion[response_metric],'$dr._data.project_id'])
                # q = q.render(['$comp._data.submitter_id', '$dr._data',conversion[response_metric],'$dr._data.project_id'])
                a=[]
                b=[]
                c=[]
                d=[]
                for i in q:
                    # drug response metric is measured (ex. ec50)
                    if i[2] is not None:
                        a.append(i[0])
                        b.append(i[1])
                        c.append(i[2])
                        d.append(i[3])
                df=pd.DataFrame(list(zip(a,b,c,d)),columns=['Drug Compound','Cell Line', response_metric, 'Dataset'])
            else:
                gene = gene_list[i]
                q= G.query().V().hasLabel('Gene').has(gripql.eq('$._gid', gene)).as_('gene').out('g2p_associations').as_('lit').out('compounds').as_('comp').out('drug_responses').as_('dr')
                q = q.render(['$comp._data.synonym', '$dr._data.source_cell_name',conversion[response_metric],'$dr._data.project_id'])
                # q = q.render(['$comp._data.submitter_id', '$dr._data',conversion[response_metric],'$dr._data.project_id'])
                a=[]
                b=[]
                c=[]
                d=[]
                for i in q:
                    # drug response metric is measured (ex. ec50)
                    if i[2] is not None:
                        a.append(i[0])
                        b.append(i[1])
                        c.append(i[2])
                        d.append(i[3])
                df2=pd.DataFrame(list(zip(a,b,c,d)),columns=['Drug Compound','Cell Line', response_metric, 'Dataset']) 
                df=pd.concat([df,df2],ignore_index=True)        
        df= df.sort_values(by=['Drug Compound'], ascending =True).reset_index(drop=True)
        return df
    
# drug response 2b
def response_table(selection, metric_selection):
    '''
    Input drug synonym and metric
    return dictionary of all drug response values as v and k as indexing number
    '''
    res={}
    index =0
    conversion={'AAC':'$dr._data.aac', 'EC50':'$dr._data.ec50'}
    if selection != None:
        q = G.query().V().hasLabel('Compound').has(gripql.eq('$._data.synonym', selection)).as_('comp').out('drug_responses').as_('dr')
        q= q.render([conversion[metric_selection]])
        for a in q:
            if a != [None]:
                res[index]=a[0] #list of one
            index+=1
    return res
