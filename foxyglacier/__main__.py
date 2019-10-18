__cmddocs = """foxyglacier

Usage:
 foxyglacier --pm-key=<api_key> [(-y|-n)] [--wget] [DIR]

Options:
 -y            Automatically respond yes to add
 -n            Automatically respond no to add
 --wget        Print a wget command for all links
 --pm-key=KEY  API Key

"""
from pathlib import Path

from docopt import docopt

from .foxyglacier import *
from foxydebrid import debrid



def main():
    args = docopt(__cmddocs)
    watchdir = Path(args['DIR'] or '.')
    torrent_files = list(watchdir.glob('*.torrent'))
    if not torrent_files:
        return
    torrents = [decode_torrent(torrent) for torrent in torrent_files]
    magnets = [get_magnet(torrent) for torrent in torrents]
    pm = debrid.Premiumize(api_key=args['--pm-key'])
    cache = pm.check_availability(magnets)
    uncached = []
    all_links = []
    for (torrent_file, magnet, cache) in zip(torrent_files, magnets, cache):
        print(f'Torrent: {torrent_file.name}')
        if cache:
            print('Cached links:')
            links = [content['link'] for content in
                     pm.cached_content(magnet, fn_filter=mime_check)]
            all_links.extend(links)
            print(' \n'.join(links))
        else:
            if not (args['-y'] or args['-n']):
                add = input('Add to Premiumize? [y/N]: ')
                add = add.lower() == 'y'
            else:
                add = args['-y']
            if add:
                pm.add_torrent(str(torrent_file))
            else:
                uncached.append(torrent_file.name)
        print()
    if args['--wget']:
        print('wget', *all_links, '\n')
    print('Failed to get:')
    print('\n'.join(uncached))


if __name__ == '__main__':
    main()
