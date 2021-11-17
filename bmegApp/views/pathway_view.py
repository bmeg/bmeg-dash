
import i18n
from ..widgets import pathway

NAME = i18n.t('app.config.tabname_pathway')

def CREATE(index):
    return pathway.CREATE(index)
