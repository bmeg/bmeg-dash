#!/usr/bin/env python

import pandas as pd
from gripql.graph import Graph

G = Graph(url='https://bmeg.io/grip', graph='rc5', credential_file='bmeg_app/secrets/bmeg_credentials.json')

label='Project:CCLE'
###############
# Get genotype df 
###############
q=G.query().V(label).out("cases").out("samples").as_('s').out("aliquots").out("gene_expressions").as_('gexp').out("aliquot").out("drug_response").as_("dr").out("compounds").as_('comp')
q = q.render(["$s.sample_id", "$comp._gid", "$dr._data.aac",'$gexp._data.values'])
phenotype={}
genotype={}
for row in q:
    sample, compound, aac, g_matrix = row
    for gene,gene_expr in g_matrix.items():
        if sample not in phenotype:
            phenotype[sample] = {compound:aac}
            genotype[sample]={gene:gene_expr}
        else:
            phenotype[sample][compound] = aac
            genotype[sample][gene]=gene_expr

genotypeDF = pd.DataFrame(genotype).transpose().sort_index().sort_index(axis=1) #sort rows, sort cols
phenotypeDF = pd.DataFrame(phenotype).transpose().sort_index().sort_index(axis=1) #sort rows, sort cols

genotypeDF.to_csv('bmeg_app/source/genotypeDF.tsv',sep='\t',index=True)
phenotypeDF.to_csv('bmeg_app/source/phenotypeDF.tsv',sep='\t',index=True)
