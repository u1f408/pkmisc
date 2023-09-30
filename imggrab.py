#!/usr/bin/env python3
# SPDX-License-Identifier: CC0-1.0

"""\
imggrab.py - mass avatar/banner grabber from PluralKit export files

see https://github.com/u1f408/pkmisc for details.
licensed under CC0 / public domain.
"""

import os
import os.path
import sys

import re
import json
import urllib.request
from urllib.error import URLError
from urllib.parse import urlparse


USER_AGENT = "pk-avigrab/0.1 (https://github.com/u1f408/pkmisc)"


def sanitize_name(name):
    return re.sub(r'\W|[!\#\$%\&\'\*\+\-\.\^_`\|\~:]', '', name)


def maybe_grab(url, basefn, prefix):
    if url is None or url == "":
        return

    parseres = urlparse(url)
    outfn = os.path.join(prefix, basefn) + os.path.splitext(parseres.path)[1]

    try:
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        with urllib.request.urlopen(req) as resp:
            if resp.status != 200:
                return

            print(f"saving {outfn}")
            with open(outfn, 'wb') as fd:
                while True:
                    chunk = resp.read(128)
                    if chunk == b'':
                        break

                    fd.write(chunk)

    except URLError:
        return


def process_export(blob, prefix):
    maybe_grab(blob["avatar_url"], "system avatar", prefix)
    maybe_grab(blob["banner"], "system banner", prefix)

    for member in blob["members"]:
        maybe_grab(member["avatar_url"], "member " + sanitize_name(member["name"]) + " avatar", prefix)
        maybe_grab(member["webhook_avatar_url"], "member " + sanitize_name(member["name"]) + " proxyavatar", prefix)
        maybe_grab(member["banner"], "member " + sanitize_name(member["name"]) + " banner", prefix)

    for group in blob["groups"]:
        maybe_grab(group["icon"], "group " + sanitize_name(group["name"]) + " icon", prefix)
        maybe_grab(group["banner"], "group " + sanitize_name(group["name"]) + " banner", prefix)


def main(argv):
    if len(argv) == 0:
        print("To use this tool, you need a PluralKit export file, from the pk;export command.")
        print("Please drag-and-drop your PluralKit export file onto this window, and then press Enter.")
        argv = [input(">>> ")]

    for n in argv:
        if not os.path.exists(n):
            continue
        try:
            with open(n, 'r') as fh:
                blob = json.load(fh)
                if "version" not in blob and "switches" not in blob:
                    raise RuntimeError("unknown file type")

                prefix = os.path.join('.', blob["id"])
                os.makedirs(prefix, exist_ok=True)
                process_export(blob, prefix)

        except Exception as ex:
            print("Error processing file %r:" % n)
            print(str(ex))
            print('')


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))