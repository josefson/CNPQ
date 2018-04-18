#!/usr/bin/env python
# -*- coding: utf-8 -*-
from pages import CurriculumPage, CurriculumXml
from multiprocessing import Process, current_process


zip_path = '/Users/josefson/Workspace/Python/CNPQ2/xmls'


def worker(short_ids):
    """Run through a list of short_ids downloading it's respective xmls."""
    for short_id in short_ids:
        curriculum = CurriculumPage(short_id)
        xml_page = CurriculumXml(curriculum.long_id, zip_path)
        xml_page.get_xml()


def main():
    chunk = 1
    short_ids = ['K8185478E7', 'K4246690H2', 'K4138636E6']
    short_ids = [short_ids[x:x+chunk] for x in range(0, len(short_ids), chunk)]
    for split_list in short_ids:
        p = Process(target=worker, args=(split_list,))
        p.start()


if __name__ == "__main__":
    main()
