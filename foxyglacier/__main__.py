__cmddocs = """foxyglacier

Usage:
 foxyglacier --pm-key=<api_key> [(-y|-n)] [--wget] [DIR]
 foxyglacier --rd-key=<api_key> [--wget] [DIR]

Options:
 -y            Automatically respond yes to add
 -n            Automatically respond no to add
 --wget        Print a wget command for all links
 --pm-key=KEY  Premiumize API Key
 --rd-key=KEY  Real-Debrid API Key

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
    if args['--pm-key']:
        ud = debrid.Premiumize(api_key=args['--pm-key'])
    elif args['--rd-key']:
        ud = debrid.RealDebrid(api_key=args['--rd-key'])
    cache = ud.check_availability(magnets)
    uncached = []
    all_links = []
    for (torrent_file, magnet, cache) in zip(torrent_files, magnets, cache):
        print(f'Torrent: {torrent_file.name}')
        if cache:
            print('Cached links:')
            if isinstance(cache, bool):
                links = [content['link'] for content in
                         ud.cached_content(magnet, fn_filter=mime_check)]
            else:
                links = [ud.resolve_url(magnet, cache)]
            all_links.extend(links)
            print(' \n'.join(links))
            continue
        elif args['--pm-key']:
            if not (args['-y'] or args['-n']):
                add = input('Add to Premiumize? [y/N]: ')
                add = add.lower() == 'y'
            else:
                add = args['-y']
            if add:
                ud.add_torrent(str(torrent_file))
                continue
        uncached.append(torrent_file.name)
        print()
    if args['--wget']:
        print('wget', *all_links, '\n')
    print('Failed to get:')
    print('\n'.join(uncached))


if __name__ == '__main__':
    main()
