from ..db import G
import pandas as pd
import gripql

# Drug response 2a.
def tab2_drug(select_genes):
    '''
    input list of genes that want to look for g2p response 
    output pandas df
    '''
    if len(select_genes)>=1:
        for i in range(0, len(select_genes)):
            if i == 0:
                gene=select_genes[i]
                q= G.query().V().hasLabel('Gene').as_('gene').out('g2p_associations').as_('lit').out('compounds').as_('comp').has(gripql.eq('$._gid', gene))
                q= q.render(['$comp._gid','$comp._data.synonym','$comp._data.pubchem_id','$comp._data.chembl_id','$comp._data.drugbank_id','$comp._data.chebi_id','$comp._data.inchi','$comp._data.inchi_key'])
                col_a=[]
                col_b=[]
                col_c=[]
                col_d=[]
                col_e=[]
                col_f=[]
                col_g=[]
                col_h=[]
                for a,b,c,d,e,f,g,h in q:
                    if a is not None:
                        col_a.append(a)
                        col_b.append(b)
                        col_c.append(c)
                        col_d.append(d)
                        col_e.append(e)
                        col_f.append(f)
                        col_g.append(g)
                        col_h.append(h)
                df=pd.DataFrame(list(zip(col_a,col_b, col_c, col_d,col_e, col_f,col_g,col_h)),columns=['Compound ID','Common Name','PubChem ID','Chembl ID', 'Drugbank ID','Chebi ID','IUPAC','IUPAC Key'])
            else:
                gene=select_genes[i]
                q= G.query().V().hasLabel('Gene').as_('gene').out('g2p_associations').as_('lit').out('compounds').as_('comp').has(gripql.eq('$._gid', gene))
                q= q.render(['$comp._gid','$comp._data.synonym','$comp._data.pubchem_id','$comp._data.chembl_id','$comp._data.drugbank_id','$comp._data.chebi_id','$comp._data.inchi','$comp._data.inchi_key'])
                col_a=[]
                col_b=[]
                col_c=[]
                col_d=[]
                col_e=[]
                col_f=[]
                col_g=[]
                col_h=[]
                for a,b,c,d,e,f,g,h in q:
                    if a is not None:
                        col_a.append(a)
                        col_b.append(b)
                        col_c.append(c)
                        col_d.append(d)
                        col_e.append(e)
                        col_f.append(f)
                        col_g.append(g)
                        col_h.append(h)
                df2=pd.DataFrame(list(zip(col_a,col_b, col_c, col_d,col_e, col_f,col_g,col_h)),columns=['Compound ID','Common Name','PubChem ID','Chembl ID', 'Drugbank ID','Chebi ID','IUPAC','IUPAC Key'])
                df=pd.concat([df,df2],ignore_index=True)        
        df= df.sort_values(by=['Compound ID'], ascending = True).reset_index(drop=True)
        return df
    else:
        return pd.DataFrame((),columns=['Compound ID','Common Name','PubChem ID','Chembl ID', 'Drugbank ID','Chebi ID','IUPAC','IUPAC Key'])


def tab1_gene(select_genes):
    '''
    input list of genes that want to look for g2p response 
    output pandas df
    '''
    description={}
    if len(select_genes)>=1:
        for i in range(0, len(select_genes)):
            if i == 0:
                gene=select_genes[i]
                q= G.query().V().hasLabel('Gene').has(gripql.eq('$._gid', gene)).as_('gene')
                q= q.render(['$gene._data.symbol','$gene._gid','$gene._data.chromosome','$gene._data.strand','$gene._data.start', '$gene._data.end','$gene._data.genome', '$gene._data.project_id','$gene._data.description'])
                col_a=[]
                col_b=[]
                col_c=[]
                col_d=[]
                col_e=[]
                col_f=[]
                col_g=[]
                
                
                for a,gid,c,d,e,f,g,prj,des in q:
                    col_a.append(a)
                    col_b.append(gid)
                    col_c.append(c)
                    col_d.append(d)
                    col_e.append(e)
                    col_f.append(f)
                    col_g.append(g)
                    if des+gid not in description:
                        description[des+gid]={gid:des}
                df=pd.DataFrame(list(zip(col_a,col_b, col_c, col_d,col_e, col_f,col_g)),columns=['Gene Symbol','Ensembl ID','Chromsome','Strand','Start Position','Stop Position','Genome'])
            else:
                gene=select_genes[i]
                q= G.query().V().hasLabel('Gene').has(gripql.eq('$._gid', gene)).as_('gene')
                q= q.render(['$gene._data.symbol','$gene._gid','$gene._data.chromosome','$gene._data.strand','$gene._data.start', '$gene._data.end','$gene._data.genome', '$gene._data.project_id','$gene._data.description'])
                col_a=[]
                col_b=[]
                col_c=[]
                col_d=[]
                col_e=[]
                col_f=[]
                col_g=[]
                
                
                for a,gid,c,d,e,f,g,prj,des in q:
                    col_a.append(a)
                    col_b.append(gid)
                    col_c.append(c)
                    col_d.append(d)
                    col_e.append(e)
                    col_f.append(f)
                    col_g.append(g)
                    if des+gid not in description:
                        description[des+gid]={gid:des}
                df2=pd.DataFrame(list(zip(col_a,col_b, col_c, col_d,col_e, col_f,col_g)),columns=['Gene Symbol','Ensembl ID','Chromsome','Strand','Start Position','Stop Position','Genome'])
                df=pd.concat([df,df2],ignore_index=True)        
        df= df.sort_values(by=['Ensembl ID'], ascending = True).reset_index(drop=True)
        return df
    else: #no selection
        return pd.DataFrame((),columns=['Ensembl ID', 'Source Evidence Level', 'Response Type'])


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
