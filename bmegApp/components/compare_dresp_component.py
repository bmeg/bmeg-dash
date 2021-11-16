from ..db import G
import gripql


def find_index(list_dictionary):
    '''Input list of dictionaries (keys='label','value')
    and return index of first occurance that label is not numeric'''
    for i in range(0, len(list_dictionary)):
        label = list_dictionary[i]['label']
        if label.isnumeric() is False:
            return i


def get_project_drugs(selected_project):
    '''Drug dropdown menu options. If no synonym then use GID'''
    options = {}
    q = G.query().V(selected_project).out("compounds") \
        .render(['$._gid', '$._data.synonym'])
    for row in q:
        if 'Compound:NO_ONTOLOGY' not in row[0]:
            if row[1] is None:
                options[row[0]] = row[0]
            else:
                options[row[0]] = row[1].capitalize()
    return options


def get_project_aliquot_disease(project):
    q = G.query().V(project).out("cases").as_("case") \
        .out("samples").out("aliquots").as_("al") \
        .render(["$al._gid", "$case.cellline_attributes.Primary Disease"])
    return dict(list(q))


def get_project_compound_dr(project, compound, dr):
    q = G.query().V(compound).out("drug_responses")
    q = q.has(gripql.eq("project_id", project)).as_("dr")
    q = q.out("aliquot").as_("a").render(["$a._gid", "$dr." + dr])
    return dict(q)
