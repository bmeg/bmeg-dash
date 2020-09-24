"""To fill out example app, simulate backend by calling ensembl."""

import requests
import logging

SERVER = "https://rest.ensembl.org"
logger = logging.getLogger(__name__)


def fetch_phenotypes(ensemble_id):
    """Retrieve the phenotypes for a gene.
    see https://rest.ensembl.org/documentation/info/phenotype_gene

    snafu!: see https://github.com/Ensembl/ensembl-rest/issues/427 
    if running on ubuntu 20, you will need to modify openssl conf
    to lower ssl level
    https://askubuntu.com/questions/1233186/ubuntu-20-04-how-to-set-lower-ssl-security-level
    see /usr/lib/ssl/openssl.cnf
    `CipherString = DEFAULT:@SECLEVEL=1`
    """

    url = f"{SERVER}/phenotype/gene/homo_sapiens/{ensemble_id}?include_associated=1"
    logger.info(url)
    r = requests.get(url, headers={"Content-Type": "application/json"})

    if not r.ok:
        r.raise_for_status()

    return r.json()
