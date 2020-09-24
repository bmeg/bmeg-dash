import gripql
import yaml

with open('bmeg_app/config.yaml') as f:
    config = yaml.load(f, Loader=yaml.FullLoader)
conn = gripql.Connection("https://bmeg.io/api", credential_file = config['bmeg']['credentials'])    
G = conn.graph(config['bmeg']['graph'])
