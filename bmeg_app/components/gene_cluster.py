from ..db import G
import pandas as pd
import gripql

def get_df(dropdown_selection,property):
    lookup = {'CCLE': 'Project:CCLE',
     'CTRP': 'Project:CTRP',
     'TCGA-OV': 'Project:TCGA-OV',
     'TCGA-UVM': 'Project:TCGA-UVM',
     'TCGA-LUSC': 'Project:TCGA-LUSC',
     'TCGA-READ': 'Project:TCGA-READ',
     'TCGA-PRAD': 'Project:TCGA-PRAD',
     'TCGA-LGG': 'Project:TCGA-LGG',
     'TCGA-THYM': 'Project:TCGA-THYM',
     'TCGA-BRCA': 'Project:TCGA-BRCA',
     'TCGA-CHOL': 'Project:TCGA-CHOL',
     'TCGA-ESCA': 'Project:TCGA-ESCA',
     'TCGA-KICH': 'Project:TCGA-KICH',
     'TCGA-HNSC': 'Project:TCGA-HNSC',
     'TCGA-UCS': 'Project:TCGA-UCS',
     'TCGA-MESO': 'Project:TCGA-MESO',
     'TCGA-KIRP': 'Project:TCGA-KIRP',
     'TCGA-LUAD': 'Project:TCGA-LUAD',
     'TCGA-THCA': 'Project:TCGA-THCA',
     'TCGA-COAD': 'Project:TCGA-COAD',
     'TCGA-LIHC': 'Project:TCGA-LIHC',
     'TCGA-UCEC': 'Project:TCGA-UCEC',
     'TCGA-SKCM': 'Project:TCGA-SKCM',
     'TCGA-KIRC': 'Project:TCGA-KIRC',
     'TCGA-SARC': 'Project:TCGA-SARC',
     'TCGA-GBM': 'Project:TCGA-GBM',
     'TCGA-PCPG': 'Project:TCGA-PCPG',
     'TCGA-BLCA': 'Project:TCGA-BLCA',
     'TCGA-STAD': 'Project:TCGA-STAD',
     'TCGA-TGCT': 'Project:TCGA-TGCT',
     'TCGA-ACC': 'Project:TCGA-ACC',
     'TCGA-DLBC': 'Project:TCGA-DLBC',
     'TCGA-CESC': 'Project:TCGA-CESC',
     'TCGA-PAAD': 'Project:TCGA-PAAD',
     'TCGA-LAML': 'Project:TCGA-LAML',
     'GDSC': 'Project:GDSC',
     'GTEx_Pituitary': 'Project:GTEx_Pituitary',
     'GTEx_Uterus': 'Project:GTEx_Uterus',
     'GTEx_Testis': 'Project:GTEx_Testis',
     'GTEx_Bone Marrow': 'Project:GTEx_Bone Marrow',
     'GTEx_Vagina': 'Project:GTEx_Vagina',
     'GTEx_Nerve': 'Project:GTEx_Nerve',
     'GTEx_Cervix Uteri': 'Project:GTEx_Cervix Uteri',
     'GTEx_Colon': 'Project:GTEx_Colon',
     'GTEx_Adrenal Gland': 'Project:GTEx_Adrenal Gland',
     'GTEx_Lung': 'Project:GTEx_Lung',
     'GTEx_Ovary': 'Project:GTEx_Ovary',
     'GTEx_Muscle': 'Project:GTEx_Muscle',
     'GTEx_Brain': 'Project:GTEx_Brain',
     'GTEx_Small Intestine': 'Project:GTEx_Small Intestine',
     'GTEx_Liver': 'Project:GTEx_Liver',
     'GTEx_Blood': 'Project:GTEx_Blood',
     'GTEx_Blood Vessel': 'Project:GTEx_Blood Vessel',
     'GTEx_Stomach': 'Project:GTEx_Stomach',
     'GTEx_Prostate': 'Project:GTEx_Prostate',
     'GTEx_Pancreas': 'Project:GTEx_Pancreas',
     'GTEx_Fallopian Tube': 'Project:GTEx_Fallopian Tube',
     'GTEx_Heart': 'Project:GTEx_Heart',
     'GTEx_Bladder': 'Project:GTEx_Bladder',
     'GTEx_Salivary Gland': 'Project:GTEx_Salivary Gland',
     'GTEx_Breast': 'Project:GTEx_Breast',
     'GTEx_Skin': 'Project:GTEx_Skin',
     'GTEx_Kidney': 'Project:GTEx_Kidney',
     'GTEx_Esophagus': 'Project:GTEx_Esophagus',
     'GTEx_Adipose Tissue': 'Project:GTEx_Adipose Tissue',
     'GTEx_Spleen': 'Project:GTEx_Spleen',
     'GTEx_Thyroid': 'Project:GTEx_Thyroid'}
    data = {}
    label = lookup[dropdown_selection]
    q=G.query().V(label).out("cases").as_('c').out("samples").as_('s').out("aliquots").out("gene_expressions").as_('gexp')
    q=q.render([property, '$s._gid', '$gexp._gid','$gexp._data.values'])
    data = {}
    for row in q:
        if row[0] !=[]:
            stage = row[0][0].replace(' ',':').upper() 
            sample = row[1]
            key=stage+"__"+sample
            gid = row[2]
            vals=row[3]
            data[key]= vals
    return pd.DataFrame(data).transpose()


def get_umap(df, input_title):
    import plotly.express as px
    import umap.umap_ as umap
    locs = umap.UMAP().fit_transform(df)
    uDF = pd.concat( [pd.DataFrame(locs, index=df.index), df.index.to_series()], axis=1, ignore_index=True )
    uDF['group']= [a.split('__')[0] for a in uDF.index]
    fig = px.scatter(uDF, x=0, y=1, hover_name=2,color='group')
    fig.update_layout(title=input_title,height=400)
    return fig
    

def dropdown_options():
    '''
    All projects a
    projects can be manually pulled with 
        [row[0] for row in G.query().V().hasLabel('Project').as_('p').render(['$p._data.project_id']) if 'TCGA' in row[0]]
    '''
    options = {}
    for row in G.query().V().hasLabel('Project').as_('p').render(['$p._data.project_id']):
        if 'TCGA' in row[0]:
            options[row[0]]=1
    return options

def mappings(selected_project):
    if 'TCGA' in selected_project:
        return {
        'Tumor Stage':'$c._data.gdc_attributes.diagnoses.tumor_stage',"Tissue/Organ of Origin":'$c._data.gdc_attributes.diagnoses.tissue_or_organ_of_origin',"Prior Malignancy":'$c._data.gdc_attributes.diagnoses.prior_malignancy',"Prior Treatment":'$c._data.gdc_attributes.diagnoses.prior_treatment'
        }
    #elif other project...load project specific properties
