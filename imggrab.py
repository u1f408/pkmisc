#!/usr/bin/env python3
# SPDX-License-Identifier: CC0-1.0

"""\
imggrab.py - mass avatar/banner grabber from PluralKit export files

see https://github.com/u1f408/pkmisc for details, and documentation on
how to use the script (if you're unsure, read the documentation!)

if you need support using this script, please join the PluralKit Discord
server (https://discord.gg/PczBt78) and ask in the #third-party-discussion
channel. please don't open github issues for support queries.

licensed under CC0 / public domain - no warranties given or implied.
"""

import os
import os.path
import sys

import re
import json
import mimetypes
from urllib.request import Request, urlopen
from urllib.error import URLError
from pathlib import Path


USER_AGENT = "pk-imggrab/0.1 (https://github.com/u1f408/pkmisc)"


def pathfix(path):
    if (path.startswith("'") and path.startswith("'")) or (path.startswith('"') and path.startswith('"')):
        path = path[1:-1]
    return path


def sanitize_name(name):
    return re.sub(r'\W|[!\#\$%\&\'\*\+\-\.\^_`\|\~:]', '', name)


def maybe_grab(url, basefn, prefix):
    if url is None or url == "":
        return

    try:
        req = Request(url, headers={"User-Agent": USER_AGENT})
        with urlopen(req) as resp:
            if resp.status != 200:
                return

            outext = mimetypes.guess_extension(resp.headers["Content-Type"].split(';')[0])
            outfn = Path(prefix) / (basefn + outext)

            print(f"saving {outfn.name}")
            with open(str(outfn), 'wb') as fd:
                while True:
                    chunk = resp.read(128)
                    if chunk == b'':
                        break

                    fd.write(chunk)

    except URLError:
        return


def process_export(blob, prefix):
    print(f"Processing export for system {blob['id']} - saving to: {prefix!s}")

    maybe_grab(blob["avatar_url"], "system avatar", prefix)
    maybe_grab(blob["banner"], "system banner", prefix)

    for member in blob["members"]:
        maybe_grab(member["avatar_url"], "member " + sanitize_name(member["name"]) + " avatar", prefix)
        maybe_grab(member["webhook_avatar_url"], "member " + sanitize_name(member["name"]) + " proxyavatar", prefix)
        maybe_grab(member["banner"], "member " + sanitize_name(member["name"]) + " banner", prefix)

    for group in blob["groups"]:
        maybe_grab(group["icon"], "group " + sanitize_name(group["name"]) + " icon", prefix)
        maybe_grab(group["banner"], "group " + sanitize_name(group["name"]) + " banner", prefix)

    print(f"Finished for system {blob['id']}")
    print('')


def main(argv):
    argv = [pathfix(a) for a in argv if os.path.exists(pathfix(a))]
    while len(argv) == 0:
        print("To use this tool, you need a PluralKit export file, from the pk;export command.")
        print("Please drag-and-drop your PluralKit export file onto this window, and then press Enter.")
        argv = [input(">>> ")]
        argv = [pathfix(a) for a in argv if os.path.exists(pathfix(a))]

    for n in argv:
        if not os.path.exists(n):
            continue
        try:
            with open(n, 'rb') as fh:
                blob = json.load(fh)
                if "version" not in blob and "switches" not in blob:
                    raise RuntimeError("unknown file type")

                attempt_prefix = [
                    Path(n).parent,
                    Path.cwd(),
                    Path.home() / "pk-imggrab",
                ]

                realprefix = None
                for prefix in attempt_prefix:
                    prefix = prefix / blob["id"]
                    try:
                        prefix.mkdir(exist_ok=True)
                        realprefix = prefix
                        break
                    except Exception as ex:
                        print(f"!! couldn't mkdir {prefix!s}, trying next ({ex!s})")
                        continue

                while realprefix is None:
                    print("!! Couldn't find a place to save the images to.")
                    print("Please create a new folder somewhere to save the images to, then drag-and-drop that")
                    print("folder onto this window and press Enter.")
                    tmp = pathfix(input(">>> ") or '')
                    if os.path.exists(tmp):
                        realprefix = Path(tmp)

                process_export(blob, realprefix)

        except KeyboardInterrupt:
            break

        except Exception as ex:
            print(f"!! Error processing file {n!r}: ")
            print(str(ex))
            print('')

    print("Script finished - press Enter to exit")
    input('')


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
