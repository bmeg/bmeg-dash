#!/usr/bin/env python

import sys
import pandas as pd
import umap

def umap_tsv(path):
    df = pd.read_csv(path, sep="\t", index_col=0)
    if df.shape[0] == 0 or df.shape[1] == 0:
        return pd.DataFrame()
    locs = umap.UMAP().fit_transform(df)
    return pd.DataFrame(locs, index=df.index)

inPath = sys.argv[1]
outPath = sys.argv[2]

locFrame = umap_tsv(inPath)
locFrame.to_csv(outPath, sep="\t")
