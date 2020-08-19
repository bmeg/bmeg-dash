from ..db import G
import pandas as pd
import gripql


        
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
