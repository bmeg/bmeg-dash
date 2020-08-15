from ..db import G
import pandas as pd
import gripql

# Drug response 2a.
def evidenceTable(select_genes):
    '''
    input list of genes that want to look for g2p response 
    output pandas df
    '''
    if len(select_genes)>=1:
        for i in range(0, len(select_genes)):
            if i == 0:
                gene=select_genes[i]
                q= G.query().V().hasLabel('Gene').has(gripql.eq('$._gid', gene)).as_('gene').limit(1000).out('g2p_associations').as_('lit').out('compounds').as_('comp')
                q= q.render(['$gene._gid','$gene._data.symbol','$comp._data.synonym', '$lit._data.response_type',  '$lit._data.source','$lit._data.evidence_label', '$lit._data.description'])
                col_a=[]
                col_b=[]
                col_c=[]
                col_d=[]
                col_e=[]
                col_f=[]
                col_g=[]
                for a,b,c,d,e,f,g in q:
                    if d is not None:
                        col_a.append(a)
                        col_b.append(b)
                        col_c.append(c)
                        col_d.append(d.upper())
                        col_e.append(e)
                        col_f.append(f)
                        col_g.append(g)
                df=pd.DataFrame(list(zip(col_a,col_b, col_c, col_d,col_e, col_f,col_g)),columns=['EnsemblID','Gene Symbol','Drug Compound','Response Type','Source','Source Evidence Level','Description'])
            else:
                gene=select_genes[i]
                q= G.query().V().hasLabel('Gene').has(gripql.eq('$._gid', gene)).as_('gene').out('g2p_associations').as_('lit').out('compounds').as_('comp')
                q= q.render(['$gene._gid','$gene._data.symbol','$comp._data.synonym', '$lit._data.response_type',  '$lit._data.source','$lit._data.evidence_label', '$lit._data.description'])
                col_a=[]
                col_b=[]
                col_c=[]
                col_d=[]
                col_e=[]
                col_f=[]
                col_g=[]
                for a,b,c,d,e,f,g in q:
                    if d is not None:
                        col_a.append(a)
                        col_b.append(b)
                        col_c.append(c)
                        col_d.append(d.upper())
                        col_e.append(e)
                        col_f.append(f)
                        col_g.append(g)
                # Store as Pandas DataFrame
                df2=pd.DataFrame(list(zip(col_a,col_b, col_c, col_d,col_e, col_f,col_g)),columns=['EnsemblID','Gene Symbol','Drug Compound','Response Type','Source','Source Evidence Level','Description'])
                df=pd.concat([df,df2],ignore_index=True)        
        df= df.sort_values(by=['EnsemblID', 'Source Evidence Level', 'Response Type'], ascending = (True, True, False)).reset_index(drop=True)
        return df
    else:
        return pd.DataFrame((),columns=['EnsemblID','Gene Symbol','Drug Compound','Response Type','Source','Source Evidence Level','Description'])

# drug response 2b
def response_table(selection, metric_selection):
    '''
    Input drug synonym and metric
    return dictionary of all drug response values as v and k as indexing number
    '''
    res={}
    index =0
    conversion={'AAC':'$dr._data.aac'}
    if selection != None:
        q = G.query().V().hasLabel('Compound').has(gripql.eq('$._data.synonym', selection)).as_('comp').out('drug_responses').as_('dr')
        q= q.render(['$dr._data.ec50'])
        for a in q:
            if a != [None]:
                res[index]=a[0] #list of one
            index+=1
    return res
