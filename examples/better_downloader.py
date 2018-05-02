#!/usr/bin/env python
# -*- coding: utf-8 -*-
from lattes.pages import Curriculum, Xml, Preview
from lattes.config import BaseLogger

logger = BaseLogger.from_file('better_cli', 'better_cli.log')
ZIP_PATH = '/Users/josefson/Workspace/Python/cnpq/xmls'


def setup():
    """This function is just an example of how you could relate the data you
    already have together (short_id, long_id, update_date).
    The real benefit is in the main() funciton. Read its doc."""

    # Ids we already have from previous scraping
    short_ids = ['K8185478E7', 'K4246690H2', 'K4138636E6']
    long_ids = ['6380212729787758', '7639569152487589', '1024601314143406']
    updated_on = ['01/01/1995', None, '24/11/2009']

    # Recently scraped short_ids
    scraped_short_ids = ['K8185478E7', 'K4246690H2', 'K4138636E6',
                         'K4138281J4', 'K4130978D4', 'K4133929U0']

    class MyData:
        """Simple DataClass just to group the data i already have together."""
        def __init__(self, short_id, long_id=None, date=None):
            self.short_id = short_id
            self.long_id = long_id
            self.date = date

    # Dictionary/hashtable for instances of MyData where short_id is the key
    data_i_already_have = {}
    # for every short_id,long_id and date i have create a MyData instance
    for short_id, long_id, date in zip(short_ids, long_ids, updated_on):
        data = MyData(short_id, long_id, date)
        # Place that instance in the dictionary with short_id as the key
        data_i_already_have[short_id] = data

    """Now we can access through keys:
    data_i_already_have['K8185478E7'].short_id would give us 'K8185478E7'
    data_i_already_have['K8185478E7'].long_id would give us '6380212729787758'
    data_i_already_have['K8185478E7'].long_id would give us '01/01/1995'
    """
    return data_i_already_have, scraped_short_ids


def main(previous_data, new_data):
    """The real benefit of something like this is only investing time on what
    mattes. Since one could have previous data and most curriculums are not
    updated frequently. We can reduce the time spent for one curriculum in 1/3
    if we already have it's long_id and it has been updated since.

    We can also completly skip completly those we already have and haven't
    been updated since, with the cost of a single request, or roughly less than
    1/6 of the time to get a curriculum from scratch.

    This function shows how to use the lattes API in order to add a better
    logic to the scraping.
    """

    ids_not_found = []  # Failback list for not found long_ids
    # for every short_id scraped in new_data:
    for short_id in new_data:
        logger.info('-----------------------------------------')
        logger.info('Is {} in previous data?'.format(short_id))
        if short_id in data_i_already_have.keys():
            logger.info('Yes it is! Has it been updated?')
            previous = data_i_already_have[short_id]
            current_date = Preview.date(short_id)
            if previous.date != current_date:
                logger.info('{} has been updated, starting download...'.
                            format(short_id))
                x = Xml(previous.long_id, ZIP_PATH)
                if not x:
                    logger.info('No. Failed to download {}'.format(short_id))
                    logger.info('Saving {} for later.'.format(short_id))
                    ids_not_found.append(short_id)
                else:
                    logger.info('Done: {}'.format(x.file_name))
            else:
                logger.info('No, already up to date. No need to download.')
        else:
            logger.info('No, loading CV page in order to get long_id...')
            logger.info('Getting curriculum page for {}...'.format(short_id))
            logger.info('Was it successful?')
            curriculum = Curriculum(short_id)
            if curriculum.is_loaded:
                logger.info('Yes it was, now downloading xml...')
                x = Xml(curriculum.long_id, ZIP_PATH)
                if not x:
                    logger.info('No. Failed to download {}'.format(short_id))
                    logger.info('Saving {} for later.'.format(short_id))
                    ids_not_found.append(short_id)
                else:
                    logger.info('Done: {}'.format(x.file_name))
            else:
                logger.info('No. Failed to download {}'.format(short_id))
                logger.info('Saving {} for later.'.format(short_id))
                ids_not_found.append(short_id)

    ids_not_found.append('K4420603Z1')  # Not found id example
    # Write file with not found ids for new try later on
    with open('ids_not_found.txt', 'w') as try_again_file:
        for short_id in ids_not_found:
            try_again_file.write(short_id + '\n')


if __name__ == "__main__":
    data_i_already_have, recently_scraped_short_ids = setup()
    main(data_i_already_have, recently_scraped_short_ids)
