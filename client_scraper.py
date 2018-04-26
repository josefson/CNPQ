from lattes.search import Search, Scraper
search = Search()
total = search.total
print('Total of registers: {}'.fomat(total))
# From experience: chunk_size should not be > 10k: ConnectionClosed
chunk_size = 1000
short_ids = []  # result list with scraped ids.
for register in range(0, total, chunk_size):
    print('Scraping from {} to {}'.format(register, register+chunk_size))
    ids = Scraper.from_registers(search, register, chunk_size)
    print('got {} valid ids'.format(len(ids)))
    short_ids.extend(ids)
print('Total ids scraped: {}'.format(len(short_ids)))
