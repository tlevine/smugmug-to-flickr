#!/usr/bin/python

from smugmugapi.functional import *
from os.path import *
from os import mkdir
import httplib
import yaml
import sys
import ConfigParser

# read config
config = ConfigParser.ConfigParser()
config.read("config.cfg")

output_dir=config.get('Config', "image_dir") # dump albums to here
sm_email=config.get('SmugMug', "email")
smugmug_api_key=config.get('SmugMug', "api_key")
sm_passwd=config.get('SmugMug', "passwd")
sm_short_username=config.get('SmugMug', "username")


def login(sapi):
    result=sapi.login_withPassword (EmailAddress = sm_email, Password = sm_passwd)
    return result.Login[0].Session[0]["id"]

def meta_dir(image):
    r = {}
    for f in ["Caption", "Keywords", "Date", "LastUpdated", "FileName", "Latitude", "Longitude", "Altitude"]:
        try :
            r[f] = str(image[f])
        except:
            pass
    return r

def ingest_image(sapi, sessionId, image, dst):
    conn = httplib.HTTPConnection(sm_short_username + ".smugmug.com")
    
    fn = image["FileName"]

    # flickr doesn't support RAW photos so we download high-quality JPEGs
    if fn.endswith("CR2"): # it's raw
        fn = fn.replace(".CR2", ".JPG")
        url = image["X3LargeURL"]
    else:
        url = image["OriginalURL"]

    print "fetching " + url
    try:
        conn.request("GET", url)
        resp = conn.getresponse()
        
        if resp.status != 200:
            print "error fetching " + url
            print resp.reason
        else:
            meta_fn = dst + "/" + fn + ".yaml"
            meta_f = open (meta_fn, 'w')
            meta_f.write(yaml.dump(meta_dir(image)))
            meta_f.close()
            
            out_fn = dst + "/" + fn
            print "writing image to " + out_fn 
            f = open(out_fn, 'w') # TODO make / conditional
            f.write(resp.read())
            f.close()
    except:
        print "Unexpected error:", sys.exc_info()[0]
        print "error exporting image %s" % (dst+"/"+fn)
    finally:
        conn.close
        
def main():
    if not exists(output_dir):
        mkdir(output_dir)
    
    sapi = SmugMugAPI(smugmug_api_key)
    sessionId = login(sapi)
    albums = sapi.albums_get(SessionID=sessionId).Albums[0].Album
        
    for album in albums:
        # this assumes that albums have unique names which they may not
        album_dir = output_dir+"/"+album["id"]
        print "fetching images for album " + album["Title"]
        
        if not exists(album_dir):
            mkdir(album_dir)
        
        images = sapi.images_get(SessionID=sessionId, AlbumID=album["id"], AlbumKey=album["Key"], Heavy="1").Images[0].Image
        
        for img in images:
            ingest_image(sapi, sessionId, img, album_dir)

if __name__ == "__main__":
    main()

