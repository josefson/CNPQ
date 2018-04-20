"""This module is just a collection of examples of how to use the pages module
so one can have some idea of what to do and how to do."""
#!/usr/bin/env python
# -*- coding: utf-8 -*-
from multiprocessing import Process, current_process
from lattes.pages import CurriculumPage, CurriculumXml
from lattes.search import SearchSession
from lattes.config import BaseLogger
import logging


logger = BaseLogger()
zip_path = '/Users/josefson/Workspace/Python/CNPQ2/xmls'


def worker(short_ids):
    """Run through a list of short_ids downloading it's respective xmls."""
    for short_id in short_ids:
        curriculum = CurriculumPage(short_id)
        xml_page = CurriculumXml(curriculum.long_id, zip_path)
        xml_page.get_xml()


def multi_cored_example(short_ids):
    """Simple enough multicore example."""
    chunk = 1
    short_ids = [short_ids[x:x+chunk] for x in range(0, len(short_ids), chunk)]
    for split_list in short_ids:
        p = Process(target=worker, args=(split_list,))
        p.start()


def single_cored_example(short_ids):
    worker(short_ids)


def better_logic_example(short_ids):
    ids_not_found = []  # Save unsuccessfull for later

    # Process all ids
    for short_id in short_ids:
        curriculum = CurriculumPage(short_id)
        # Test if long_id is not None or False, ergo is real
        # One could also test if curriculum update date is newer than some other date in order to download
        if curriculum.long_id:
            xml_page = CurriculumXml(curriculum.long_id, zip_path)
            xml_page.get_xml()
        elif not curriculum.long_id:
            ids_not_found.append(short_id)

    # Save not found ids for new try
    with open('ids_not_found.txt', 'w') as out_file:
        for short_id in ids_not_found:
            out_file.write(short_id)


if __name__ == "__main__":
    # short_ids = ['K8185478E7', 'K4246690H2', 'K4138636E6'] single_cored_example(short_ids)
    # # multi_cored_example(short_ids)
    s = SearchSession()
