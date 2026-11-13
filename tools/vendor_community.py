#!/usr/bin/env python3
"""Copy an open-source community game into community/<id>/ for the Game Hub.

Usage: python3 tools/vendor_community.py <clone-dir> <id> <entry> <include>... [--three]

- <clone-dir>: a checkout of the game's repository (read only; nothing in it is executed)
- <id>:        the community game id (folder name under community/)
- <entry>:     the game's start page, relative to the clone (e.g. game/index.html)
- <include>:   files/folders to copy, relative to the clone. A path under the entry's folder keeps
               its place relative to the entry; the entry's folder becomes community/<id>/.
- --three:     replace jsDelivr three@0.170.0 imports with a local copy (vendor-dl) and drop GoatCounter.

Every copied .html page gets <script src=".../community/shim.js"></script> as its first script,
so the game runs with the sandbox storage shim (see community/shim.js). LICENSE is always copied.
"""
import os, re, shutil, subprocess, sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
THREE_SRC = '/home/claude/vendor-dl/three/package'


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    three = '--three' in sys.argv
    src, gid, entry, includes = args[0], args[1], args[2], args[3:]
    assert re.fullmatch(r'[a-z0-9-]+', gid)
    base = os.path.dirname(entry)            # entry folder inside the clone
    dst = os.path.join(REPO, 'community', gid)
    if os.path.exists(dst):
        shutil.rmtree(dst)
    os.makedirs(dst)
    for inc in includes:
        rel = os.path.relpath(inc, base) if base else inc
        assert not rel.startswith('..'), f'{inc} is outside the entry folder {base}'
        s, d = os.path.join(src, inc), os.path.join(dst, rel)
        if os.path.isdir(s):
            shutil.copytree(s, d, symlinks=False)
        else:
            os.makedirs(os.path.dirname(d), exist_ok=True)
            shutil.copy2(s, d)
    for name in os.listdir(src):
        if re.match(r'(?i)^(license|licence|copying)(\.|$)', name):
            shutil.copy2(os.path.join(src, name), os.path.join(dst, name))
    if three:
        vd = os.path.join(dst, 'vendor', 'three')
        os.makedirs(os.path.join(vd, 'build'), exist_ok=True)
        os.makedirs(os.path.join(vd, 'examples', 'jsm', 'utils'), exist_ok=True)
        shutil.copy2(os.path.join(THREE_SRC, 'build', 'three.module.js'), os.path.join(vd, 'build'))
        shutil.copy2(os.path.join(THREE_SRC, 'examples', 'jsm', 'utils', 'BufferGeometryUtils.js'), os.path.join(vd, 'examples', 'jsm', 'utils'))
        shutil.copy2(os.path.join(THREE_SRC, 'LICENSE'), os.path.join(vd, 'LICENSE'))
    patched = []
    for root, _, files in os.walk(dst):
        for f in files:
            if not f.endswith('.html'):
                continue
            p = os.path.join(root, f)
            html = open(p, encoding='utf-8').read()
            depth = os.path.relpath(root, os.path.join(REPO, 'community')).count(os.sep) + 1
            tag = '<script src="' + '../' * depth + 'shim.js"></script>'
            if three:
                html = html.replace('https://cdn.jsdelivr.net/npm/three@0.170.0/build/three.module.js', './vendor/three/build/three.module.js')
                html = html.replace('https://cdn.jsdelivr.net/npm/three@0.170.0/examples/jsm/', './vendor/three/examples/jsm/')
                html = re.sub(r'"integrity"\s*:\s*\{[^}]*\}\s*,?', '', html)  # integrity keys named the CDN URLs
                html = re.sub(r',\s*\}\s*</script>', '}</script>', html)
                html = re.sub(r'<script[^>]*gc\.zgo\.at/count\.js[^>]*></script>\s*', '', html)
            m = re.search(r'<head(\s[^>]*)?>', html, re.I)
            if m:
                html = html[:m.end()] + '\n' + tag + html[m.end():]
            else:
                html = tag + '\n' + html
            open(p, 'w', encoding='utf-8').write(html)
            patched.append(os.path.relpath(p, dst))
    sha = subprocess.run(['git', '-C', src, 'rev-parse', 'HEAD'], capture_output=True, text=True).stdout.strip()
    print(gid, 'commit', sha, 'patched', patched)


if __name__ == '__main__':
    main()
