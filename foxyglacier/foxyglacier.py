import hashlib
import mimetypes
from pathlib import PurePath

import bencode3


def mime_check(path, types=('video',)):
    """Returns True if file extension in path matches types.

    types -- Iterable of media types to return True for.
    """
    _type, _ = mimetypes.guess_type(str(path))
    _type, _ = _type.split('/')
    return _type in types


def decode_torrent(path):
    """Returns bdecode-ed dict for torrent file at path."""
    with open(path, 'rb') as tfile:
        data = tfile.read()
    return bencode3.bdecode(data)


def get_magnet(torrent):
    """Returns magnet link for torrent.

    torrent -- Either a path to a .torrent or result of decode_torrent().
    """
    try:
        info = torrent['info']
    except TypeError:
        info = decode_torrent(torrent)['info']
    btih = hashlib.sha1(bencode3.bencode(info)).hexdigest()
    return f'magnet:?xt=urn:btih:{btih}'


def get_files(torrent):
    """Returns a list of PurePath objects of file in torrent."""
    try:
        try:
            info = torrent['info']
            files = info['files']
        except TypeError:
            info = decode_torrent(torrent)['info']
            files = info['files']
    except KeyError:
        files = [PurePath(info['name'])]
    else:
        files = [PurePath(*_file['path']) for _file in files]
    finally:
        return files
