#!/usr/bin/env python

import os
import sys
import gripql
import pandas as pd
from gripql.graph import Graph
from tqdm import tqdm


G = Graph(url='https://bmeg.io/grip', graph='rc5', credential_file='./bmeg_app/secrets/bmeg_credentials.json')

proj = sys.argv[1]
outfile = sys.argv[2]

q = G.query().V(proj).out("cases").as_('c').out("samples").has(gripql.eq("project_id", proj)).as_('s').out("aliquots").out("gene_expressions").as_('gexp')
q = q.render(['$s._gid', '$gexp.values'])
data = {}
for row in tqdm(q):
    sample = row[0]
    data[sample] = row[1]
df = pd.DataFrame(data).transpose() #sample rows and gene cols
df.to_csv(outfile, sep="\t")
