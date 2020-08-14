import dash_core_components as dcc

import dash_core_components as dcc

def codeblock_cohort_genom():
    return dcc.Markdown('''
    ```py
    import matplotlib.pyplot as plt
    import gripql
    conn = gripql.Connection("https://bmeg.io/api", credential_file="bmeg_credentials.json")
    G = conn.graph("rc5")

    q = G.query().V("Project:TCGA-BRCA").out("cases").out("samples")
    q = q.has(gripql.eq("gdc_attributes.sample_type", "Primary Tumor"))
    q = q.out("aliquots").out("somatic_callsets").out("alleles")
    q = q.has(gripql.eq("variant_type", "SNP"))
    q = q.aggregate(gripql.term("chrom", "chromosome"))
    res = q.execute()
    
    name = []
    count = []
    for i in res[0].chrom.buckets:
        name.append(i["key"])
        count.append(i["value"])
    plt.bar(name, count, width=0.35)
    ```
    ''', style={'textAlign': 'left'})


def codeblock_drugresp():
    return dcc.Markdown('''
    ```py
    import pandas as pd
    import gripql
    conn = gripql.Connection("https://bmeg.io/api", credential_file="bmeg_credentials.json")
    G = conn.graph("rc5")
    
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
    ```
    ''', style={'textAlign': 'left'})
