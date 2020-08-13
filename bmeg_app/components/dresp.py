def evidenceTable(select_genes):
    '''
    input list of genes that want to look for g2p response 
    output pandas df
    '''
    from ..db import G
    import gripql
    import pandas as pd
    if select_genes == []:
        return pd.DataFrame()
    else:
        for i in range(0, len(select_genes)):
            if i == 0:
                gene=select_genes[i]
                q= G.query().V().hasLabel('Gene').has(gripql.eq('$._gid', gene)).as_('gene').out('g2p_associations').as_('lit').out('compounds').as_('comp')
        #         q= G.query().V().hasLabel('G2PAssociation').as_('lit').out('genes').has(gripql.eq('$._gid', gene)).as_('gene')
                q= q.render(['$gene._gid','$comp._gid', '$lit._data.response_type',  '$lit._data.source','$lit._data.evidence_label', '$lit._data.description'])
                col_a=[]
                col_b=[]
                col_c=[]
                col_d=[]
                col_e=[]
                col_f=[]
                for a,b,c,d,e,f in q:
                    if c is not None:
                        col_a.append(a)
                        col_b.append(b)
                        col_c.append(c.upper())
                        col_d.append(d)
                        col_e.append(e)
                        col_f.append(f)
                df=pd.DataFrame(list(zip(col_a,col_b, col_c, col_d,col_e, col_f)),columns=['EnsemblID','Drug Compound','Response Type','Source','Source Evidence Level','Description'])
            else:
                gene=select_genes[i]
                q= G.query().V().hasLabel('Gene').has(gripql.eq('$._gid', gene)).as_('gene').out('g2p_associations').as_('lit').out('compounds').as_('comp')
        #         q= G.query().V().hasLabel('G2PAssociation').as_('lit').out('genes').has(gripql.eq('$._gid', gene)).as_('gene')
                q= q.render(['$gene._gid','$comp._gid', '$lit._data.response_type',  '$lit._data.source','$lit._data.evidence_label', '$lit._data.description'])
                col_a=[]
                col_b=[]
                col_c=[]
                col_d=[]
                col_e=[]
                col_f=[]
                for a,b,c,d,e,f in q:
                    if c is not None:
                        col_a.append(a)
                        col_b.append(b)
                        col_c.append(c.upper())
                        col_d.append(d)
                        col_e.append(e)
                        col_f.append(f)
                # Store as Pandas DataFrame
                df2=pd.DataFrame(list(zip(col_a,col_b, col_c, col_d,col_e, col_f)),columns=['EnsemblID','Drug Compound','Response Type','Source','Source Evidence Level','Description'])
                df=pd.concat([df,df2],ignore_index=True)        
        df= df.sort_values(by=['EnsemblID', 'Source Evidence Level', 'Response Type'], ascending = (True, True, False)).reset_index(drop=True)
        return df
