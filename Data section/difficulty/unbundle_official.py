"""Unpack a download bundle made in the browser into difficulty/src/official/ (8 Nov 2026, Claude).

Why a bundle: UCI, LibSVM and other official sites are reachable only from the browser on Toon's machine (not from the
cloud workspace or the local shell). The browser fetched each file from the official URL and saved all of them as one
file: the line "SMOTE25BUNDLE", one JSON line {tag, fetched, files:[{name, url, size}]}, then the raw bytes of each file
in that order. This script splits it, checks every size, unzips .zip archives, and appends one row per file to
difficulty/official_manifest.csv (tag, name, url, fetched, bytes, sha256) so that each file can be fetched again.

Usage (from Data section/difficulty):  python3 unbundle_official.py <bundle file> [<bundle file> ...]
Output: src/official/<tag>/<name> (+ unzipped content in src/official/<tag>/<name>.d/), official_manifest.csv
"""
import csv, hashlib, io, json, os, sys, zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'src', 'official')
MAN = os.path.join(HERE, 'official_manifest.csv')

def unbundle(path):
    raw = open(path, 'rb').read()
    assert raw.startswith(b'SMOTE25BUNDLE\n'), f'STOP: {path} is not a bundle'
    p = raw.index(b'\n', 14)
    meta = json.loads(raw[14:p].decode('utf-8')); pos = p + 1
    rows = []
    for f in meta['files']:
        b = raw[pos:pos + f['size']]; pos += f['size']
        assert len(b) == f['size'], f'STOP: truncated bundle at {f["name"]}'
        safe = f['name'].replace('/', '__')
        d = os.path.join(OUT, meta['tag']); os.makedirs(d, exist_ok=True)
        fp = os.path.join(d, safe); open(fp, 'wb').write(b)
        if safe.endswith('.zip'):
            with zipfile.ZipFile(io.BytesIO(b)) as z:
                for m in z.namelist():                      # nested zips (UCI sometimes zips a zip) are opened once more
                    if m.endswith('/') or '..' in m or m.startswith('/'): continue
                    tgt = os.path.join(fp + '.d', m)
                    try:                                    # some archives hold a file and a folder of the same name
                        os.makedirs(os.path.dirname(tgt), exist_ok=True)
                        data = z.read(m)
                        if os.path.isdir(tgt): continue
                        open(tgt, 'wb').write(data)
                    except (FileExistsError, NotADirectoryError, IsADirectoryError):
                        print('  skipped archive member (name clash):', m); continue
                    if m.endswith('.zip'):
                        with zipfile.ZipFile(io.BytesIO(data)) as z2:
                            for m2 in z2.namelist():
                                if m2.endswith('/') or '..' in m2 or m2.startswith('/'): continue
                                t2 = os.path.join(tgt + '.d', m2); os.makedirs(os.path.dirname(t2), exist_ok=True)
                                open(t2, 'wb').write(z2.read(m2))
        rows.append(dict(tag=meta['tag'], name=f['name'], url=f['url'], fetched=meta['fetched'], bytes=len(b),
                         sha256=hashlib.sha256(b).hexdigest()))
    assert pos == len(raw), 'STOP: trailing bytes in bundle'
    old = list(csv.DictReader(open(MAN, encoding='utf-8'))) if os.path.exists(MAN) else []
    keep = [r for r in old if (r['tag'], r['name']) not in {(x['tag'], x['name']) for x in rows}]
    with open(MAN, 'w', newline='', encoding='utf-8') as fh:
        w = csv.DictWriter(fh, fieldnames=['tag', 'name', 'url', 'fetched', 'bytes', 'sha256'], lineterminator='\n')
        w.writeheader(); w.writerows(sorted(keep + rows, key=lambda r: (r['tag'], r['name'])))
    print(meta['tag'], len(rows), 'files')

if __name__ == '__main__':
    for a in sys.argv[1:]: unbundle(a)
