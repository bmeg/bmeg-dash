from ..db import G
import pandas as pd
import gripql
import json 
import plotly.express as px
import umap.umap_ as umap 

def get_df(selected_project,property):
    '''Create df for selected property'''
    property_name=property.split('.')[-1]

    data = {}
    q=G.query().V(selected_project).out("cases").as_('c').out("samples").as_('s').out("aliquots").out("gene_expressions").as_('gexp')
    q=q.render([property, '$s._gid', '$gexp._gid','$gexp._data.values'])
    data = {}
    for row in q:
        stage = row[0][0].replace(' ',':').upper() 
        sample = row[1]
        key=stage+"__"+sample
        gid = row[2]
        vals=row[3]
        data[key]= vals
    df = pd.DataFrame(data).transpose() #sample rows and gene cols
    locs = umap.UMAP().fit_transform(df)
    uDF = pd.concat( [pd.DataFrame(locs, index=df.index), df.index.to_series()], axis=1, ignore_index=True )
    uDF[property_name]= [a.split('__')[0] for a in uDF.index]
    return uDF

def update_umap(p, cached_df):
    '''
    Input existing df for umap and new attribute to show
    
    + adds new col and returns this df
    '''
    ordered_samp = [a.split('__')[1] for a in cached_df.index]
    new_colname=p.split('.')[-1]
    new_col = []
    q=G.query().V(ordered_samp).as_('s').out("case").as_('c').render([p])
    for a in q:
        new_col.append(a[0][0])
    cached_df[new_colname]= new_col
    return cached_df

def get_umap(uDF, input_title,cached_df_column):
    fig = px.scatter(uDF, x='0', y='1', hover_name='2',color=cached_df_column)
    fig.update_layout(title=input_title,height=400)
    return fig

    
def options_project():
    '''Project dropdown menu options'''
    options = {}
    for row in G.query().V().hasLabel('Project').render(['$._gid','$._data.project_id']):
        if 'TCGA' in row[0]:
            options[row[0]]=row[1]
    return options

def options_property(selected_project):
    '''Property dropdown menu options'''
    exclude=['created_datetime','state','submitter_id','updated_datetime','days_to_recurrence',\
            'treatments','age_at_diagnosis','classification_of_tumor','days_to_recurrence','diagnosis_id']
    q=G.query().V(selected_project).out("cases").as_('c').out("samples").as_('s').out("aliquots").out("gene_expressions").as_('gexp')
    q=q.render(['$c._data.gdc_attributes.diagnoses']).limit(1)

    options={}
    for row in q:
        prop_list = list(row[0][0].keys()) 
        for a in prop_list:
            if a not in exclude:
                q= '$c._data.gdc_attributes.diagnoses.'+a
                string = a.replace('_',' ').upper()
                options[string]=q
    return options
