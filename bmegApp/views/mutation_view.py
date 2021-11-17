
import i18n
from ..widgets import needleplot

NAME = i18n.t('app.config.tabname_gmut')

def CREATE(index):
    return needleplot.CREATE(index)
