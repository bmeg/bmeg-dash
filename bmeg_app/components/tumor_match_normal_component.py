from ..db import G
import pandas as pd
import umap.umap_ as umap


def get_df(selected_project, property):
    '''Create df for selected property'''
    property_name = property.split('.')[-1]
    data = {}
    q = G.query().V(selected_project).out("cases").as_('c') \
        .out("samples").as_('s') \
        .out("aliquots") \
        .out("gene_expressions").as_('gexp')
    q = q.render([property, '$s._gid', '$gexp._data.values'])
    data = {}
    for row in q:
        stage = row[0][0].replace(' ', ':').upper()
        sample = row[1]
        key = stage + "__" + sample
        vals = row[2]
        data[key] = vals
    df = pd.DataFrame(data).transpose()
    locs = umap.UMAP().fit_transform(df)
    df2 = pd.concat(
        [
            pd.DataFrame(locs, index=df.index),
            df.index.to_series()
        ],
        axis=1,
        ignore_index=True
    )
    df2[property_name] = [a.split('__')[0] for a in df2.index]
    return df2


def options_project():
    '''Project dropdown menu options'''
    options = {}
    q = G.query().V().hasLabel('Project') \
        .render(['$._gid', '$._data.project_id'])
    for row in q:
        if 'TCGA' in row[0]:
            options[row[0]] = row[1]
    return options


def options_property(selected_project):
    '''Property dropdown menu options'''
    exclude = [
        'CCLE_Name',
        'COSMIC_ID',
        'DepMap_ID',
        'created_datetime',
        'state',
        'submitter_id',
        'updated_datetime',
        'days_to_recurrence',
        'treatments',
        'age_at_diagnosis',
        'classification_of_tumor',
        'days_to_recurrence',
        'diagnosis_id',
    ]

    # If TCGA data...
    if "TCGA" in selected_project:
        print('selected ', selected_project)
        q = G.query().V(selected_project).out("cases").as_('c') \
            .out("samples").as_('s') \
            .out("aliquots") \
            .out("gene_expressions").as_('gexp')
        q = q.render(['$c._data.gdc_attributes.diagnoses']).limit(1)
        options = {}
        for row in q:
            prop_list = list(row[0][0].keys())
            for a in prop_list:
                if a not in exclude:
                    q = '$c._data.gdc_attributes.diagnoses.' + a
                    string = a.replace('_', ' ').upper()
                    options[string] = q
        return options
    if 'GTEx' in selected_project:
        print('selected ', selected_project)
        q = G.query().V(selected_project).out("cases").as_('c') \
            .out("samples").as_('s') \
            .out("aliquots") \
            .out("gene_expressions").as_('gexp')
        q = q.render(['$c._data.gtex_attributes']).limit(1)
        options = {}
        for row in q:
            prop_list = list(row[0].keys())
            for a in prop_list:
                if a not in exclude:
                    q = '$c._data.gtex_attributes.' + a
                    string = a.replace('_', ' ').upper()
                    options[string] = q
        return options
    else:
        print('selected ', selected_project)
        q = G.query().V(selected_project).out("cases").as_('c') \
            .out("samples").as_('s') \
            .out("aliquots") \
            .out("gene_expressions").as_('gexp')
        q = q.render(['$c._data.cellline_attributes']).limit(1)
        options = {}
        for row in q:
            prop_list = list(row[0].keys())
            for a in prop_list:
                if a not in exclude:
                    q = '$c._data.cellline_attributes.' + a
                    string = a.replace('_', ' ').upper()
                    options[string] = q
        return options
