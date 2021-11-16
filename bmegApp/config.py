
import sys
import os
import i18n
import base64
import yaml

BASEDIR = os.path.dirname( os.path.abspath(__file__) )

STAGE = None
CONFIG = None
CONFIG_PATH = None
LOGO_IMAGE = None

def loadConfig():
    global CONFIG
    global STAGE
    global CONFIG_PATH
    global LOGO_IMAGE
    CONFIG_PATH = "./"
    if len(sys.argv) > 1:
        CONFIG_PATH = sys.argv[1]
    with open(os.path.join(CONFIG_PATH, 'config.yaml') ) as f:
        CONFIG = yaml.load(f, Loader=yaml.FullLoader)
    STAGE = os.environ.get("BMEG_STAGE", "DEV")
    print('BMEG stage: ', STAGE)
    path_name = CONFIG['DEV']['basepath']

    i18n.load_path.append(os.path.join(BASEDIR , 'locales/'))


    #######
    # Prep
    #######
    image_filename = os.path.join(BASEDIR, 'images/bmeg_logo.png')
    LOGO_IMAGE = base64.b64encode(open(image_filename, 'rb').read())


if CONFIG is None:
    loadConfig()

print("Config", CONFIG)
