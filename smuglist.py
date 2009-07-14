#!/usr/bin/env python2.6

#
# lists SmugMug galleries
#

from smugmugapi.functional import *

import config as conf
import smugmug_common as smug

def main():
    config = conf.load()
    sapi = SmugMugAPI(config.smugmug_api_key)
    sessionId = smug.login(sapi, config)
    albums = sapi.albums_get(SessionID=sessionId).Albums[0].Album
    for album in albums:
        print "%s %s" % (album["id"], album["Title"])

if __name__ == "__main__":
    main()
