
rule all:
    input: dynamic("data/{project}.locs")

def read_id_file(wildcards):
    print("Reading %s" % (wildcards.project))
    with open("data/%s.id" % (wildcards.project)) as handle:
        s = handle.read()
        return s.rstrip()

rule download:
    input: "data/{project}.id"
    output: "data/{project}.tsv"
    params:
        id=read_id_file
    shell:
        "./bin/download_project_gene_expression.py '{params.id}' data/{wildcards.project}.tsv"

rule umap_calc:
    input: "data/{project}.tsv"
    output: "data/{project}.locs"
    shell:
        "./bin/matrix_umap.py data/{wildcards.project}.tsv data/{wildcards.project}.locs"

rule project_list:
    output: dynamic("data/{project}.id")
    shell: "./bin/project_list.py data"
