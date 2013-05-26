#!/usr/bin/python2

import ConfigParser
import httplib
import os
from os import path
import re
import sys

from unidecode import unidecode

def log(arg, **kwargs):
    print 'log: ' + arg

def error(arg, **kwargs):
    print 'error: '+ arg

from smugmug_common import login
from smugmugapi.functional import *
import yaml

import config as conf
import helper
import smugmug_common


# read config
config = conf.load()

def meta_dir(image):
    r = {}
    for f in ["Caption", "Keywords", "Date", "LastUpdated", "FileName", "Latitude", "Longitude", "Altitude"]:
        try :
            r[f] = str(image[f])
        except:
            pass
    return r

def ingest_image(sapi, sessionId, image, dst):
    fn = image["FileName"]
    meta_fn = dst + "/" + fn + ".yaml"
    if path.exists(meta_fn):
        return

    conn = httplib.HTTPConnection(config.smugmug_short_username + ".smugmug.com")

    # flickr doesn't support RAW photos so we download high-quality JPEGs
    if fn.endswith("CR2"): # it's raw
        fn = fn.replace(".CR2", ".JPG")
        url = image["X3LargeURL"]
    else:
        url = image["OriginalURL"]

    log("%s -> " % url, newline=False)
    try:
        conn.request("GET", url)
        resp = conn.getresponse()

        if resp.status != 200:
            error("%s -> %s %s" % (url, resp.status, resp.reason))
        else:
            if not path.exists(meta_fn):
                meta_f = open (meta_fn, 'w')
                meta_f.write(yaml.dump(meta_dir(image)))
                meta_f.close()

            out_fn = path.join(dst, fn)

            if path.exists(out_fn):
                log("skipping")
            else:
                log(out_fn)
                f = open(out_fn, 'w') # TODO make / conditional
                f.write(resp.read())
                f.close()
    except Exception, e:
        error("error exporting image %s: %s" % (url, e))
    finally:
        conn.close

def main():
    if not len(sys.argv) == 2:
        fail("expecting: <output_dir>")

    output_dir = sys.argv[1]

    if not path.exists(output_dir):
        os.mkdir(output_dir)

    sapi = SmugMugAPI(config.smugmug_api_key)
    sessionId = login(sapi, config)
    albums = sapi.albums_get(SessionID=sessionId).Albums[0].Album


    for album in albums:
        # this assumes that albums have unique names which they may not
        raw_title = album["Title"]
        album_dir = path.join(output_dir, str(album['id']), raw_title)
        print unidecode("album: '%s'" % raw_title)

        if not path.exists(album_dir):
            os.makedirs(album_dir)

        images = sapi.images_get(SessionID=sessionId, AlbumID=album["id"], AlbumKey=album["Key"], Heavy="1").Images[0].Image

        for img in images:
            ingest_image(sapi, sessionId, img, album_dir)


if __name__ == "__main__":
    main()
