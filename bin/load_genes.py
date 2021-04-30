#!/usr/bin/env python3
"""Load gene symbol, ensembl_id into elastic."""

import os
import logging

from elasticsearch import Elasticsearch
from elasticsearch.helpers import parallel_bulk

import click


def read_genes(path, index, skip_first=True):
    """Yield an elastic dictionary {symbol, ensembl_id} for each line in file.

    The _id is set to ensembl_id - except if it's missing! Then we use the symbol.
    See https://elasticsearch-py.readthedocs.io/en/master/helpers.html?highlight=parallel_bulk#bulk-helpers"""

    with open(path, "r") as inputs:
        skip_first = True
        for line in inputs:
            if skip_first:
                skip_first = False
                continue
            (symbol, ensemble_id) = line.rstrip('\n').split('\t')
            yield({
                '_index': index,
                '_id': ensemble_id or symbol,
                '_source': {'symbol': symbol, 'ensemble_id': ensemble_id}
            })

@click.command()
@click.option('--path', default="gene-names.tsv", help='Path to gene names TSV', show_default=True)
@click.option('--index', default="genes", help='Elastic search index name.', show_default=True)
@click.option('--elastic_url', default=lambda: os.environ.get('ELASTICSEARCH_URL', ''), help='elastic hosts. [default env[ELASTICSEARCH_URL]]')
@click.option('--log_level', default="INFO", help='logging level.', show_default=True)
def load_genes(path, index, elastic_url, log_level):
    """Load gene symbol, ensembl_id into elastic."""

    numeric_level = getattr(logging, log_level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError('Invalid log level: %s' % log_level)
    logging.basicConfig(
        format='%(asctime)s %(levelname)s %(name)s %(message)s',
        level=numeric_level
    )
    logging.getLogger('elasticsearch').setLevel(logging.WARN)

    logger = logging.getLogger(__name__)
    logger.info(f"Loading contents of {path} into {index} on {elastic_url}.")

    # progress counters
    count = 0
    total_count = 0
    for success, info in parallel_bulk(Elasticsearch(elastic_url), read_genes(path, index)):
        if not success:
            logger.warn(f'A document failed: {info}')
        count += 1
        total_count += 1
        if count == 1000:
            count = 0
            logger.info(f'Loaded: {total_count}')


if __name__ == '__main__':
    load_genes()
