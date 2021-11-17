
import i18n
from ..widgets import pathway

NAME = i18n.t('app.config.tabname_pathway')

def CREATE(path):
    return pathway.CREATE(0)
