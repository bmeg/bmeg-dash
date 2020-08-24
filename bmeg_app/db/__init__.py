import gripql

conn = gripql.Connection("https://bmeg.io/api", credential_file = 'bmeg_app/secrets/bmeg_credentials.json') #external
G = conn.graph('rc5') #specific schema version
