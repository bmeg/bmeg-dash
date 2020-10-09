#!/usr/bin/env python

import os
import sys
import gripql
from gripql.graph import Graph

G = Graph(url='https://bmeg.io/grip', graph='rc5', credential_file='./bmeg_app/secrets/bmeg_credentials.json')

name_base = sys.argv[1]
for p in G.query().V().hasLabel("Project").render("$._gid"):
    name = p.split(":")[1].replace(" ", "_")
    with open(os.path.join(name_base, name) + ".id", "w") as handle:
        handle.write("%s\n" % (p))
