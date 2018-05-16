#!/usr/bin/env python
# -*- coding: utf-8 -*-
from multiprocessing import Process
from lattes.pages import Curriculum, Xml
from lattes.config import BaseLogger


logger = BaseLogger.from_file('simple_client', file_name='simple_client.log')
ZIP_PATH = '/Users/josefson/Workspace/Python/cnpq/xmls'


def single_cored_example(short_ids):
    worker(short_ids)


def multi_cored_example(short_ids):
    """Simple enough multicore example."""
    chunk = 1
    short_ids = [short_ids[x:x+chunk] for x in range(0, len(short_ids), chunk)]
    logger.info('Spawning processes')
    for split_list in short_ids:
        p = Process(target=worker, args=(split_list,))
        p.start()


def worker(short_ids):
    """Run through a list of short_ids downloading it's respective xmls."""
    for short_id in short_ids:
        logger.info('Getting curriculum for {}'.format(short_id))
        curriculum = Curriculum(short_id)
        Xml(curriculum.long_id, ZIP_PATH)
        logger.info('Curriculum for {} has been downloaded'.format(short_id))


if __name__ == "__main__":
    short_ids = ['K8185478E7', 'K4246690H2', 'K4138636E6']
    long_ids = ['6380212729787758', '7639569152487589', '1024601314143406']
    logger.info('Starting single_core...')
    single_cored_example(short_ids)
    logger.info('Starting multi_core...')
    multi_cored_example(short_ids)
