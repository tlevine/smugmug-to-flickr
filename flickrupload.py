#!/usr/bin/python

from flickrapi import *
import md5
import sys
import os
import yaml
from flickrapi.exceptions import FlickrError
from smugmugapi.functional import *
import ConfigParser

# read config
config = ConfigParser.ConfigParser()
config.read("config.cfg")

input_dir=config.get('Config', "image_dir") # input to flickr is output of smugmug
flickr_api_key=config.get('Flickr', "api_key")
flickr_api_secret=config.get('Flickr', "api_secret")
flickr_user_id=config.get('Flickr', "user_id")

sm_email=config.get('SmugMug', "email")
smugmug_api_key=config.get('SmugMug', "api_key")
sm_passwd=config.get('SmugMug', "passwd")


flickr = FlickrAPI(flickr_api_key, flickr_api_secret, username=flickr_user_id)
(token, frob) = flickr.get_token_part_one(perms='write')

if not token: raw_input("Press ENTER after you authorized this program")

tok = flickr.get_token_part_two((token, frob))
sets = flickr.photosets_getList(api_key=flickr_api_key).find('photosets').findall('photoset')

# login to smugmug
smapi = SmugMugAPI(smugmug_api_key)
result=smapi.login_withPassword (EmailAddress = sm_email, Password = sm_passwd)
smSessionId = result.Login[0].Session[0]["id"]


def set_exists(title):
    return len([s for s in sets if s.find("title").text == title]) > 0

def set_with_name(sets, photoSetName):
    return [s for s in sets if s.find("title").text == photoSetName][0]

def is_blacklisted(albumId):
    return False #not (int(albumId) in [8303177])

def progress(progress, done):
    if done:
        print "upload complete"
    else:
        print "At %s%% progress" % progress

def sorted_albums(sapi, sessionId):
    albums = sapi.albums_get(SessionID=sessionId, Heavy=1).Albums[0].Album
    albums.sort(lambda a,b : cmp(a["LastUpdated"], b["LastUpdated"]))
    return albums

def upload(flickr, img_fn, meta):
    fn=meta["FileName"]
    tags=meta["Keywords"]
    caption=meta["Caption"]
    try :
        return flickr.upload(filename=str(img_fn), title=caption, tags=tags, format="etree", callback=progress).find("photoid").text
    except:
        print "upload err " , sys.exc_info()
        return None

# photoset names are unique but smugmug album names aren't.  this method 
# derives a unique photoset name
def derive_photo_set_name(albums, this_album):
    candidates = [a for a in albums if a["Title"] == this_album["Title"]]
    if len(candidates) == 1:
        return this_album["Title"]
    else:
        # create a unique photoset name
        index = [a["id"] for a in candidates].index(this_album["id"]) + 1
        return "%s (%d)" % (this_album["Title"], index)

sm_albums = sorted_albums(smapi, smSessionId)
for album in sm_albums:
    
    if is_blacklisted(album["id"]):
       continue
    
    photoset = derive_photo_set_name(sm_albums, album) # album["Title"]
    dirName = album["id"]
    
    print "uploading images for %s %s" % (photoset, dirName)
    
    # get images from disk
    for f in os.listdir(input_dir + "/" + dirName):
        
        if not f.upper().endswith("JPG"):
            continue
        
        img_fn = input_dir + "/" + dirName + "/" + f
        meta = yaml.load(file(img_fn + ".yaml", 'r'))
        
        photo_id = upload(flickr, img_fn, meta)
        if photo_id is None:
            print "error uploading image " + img_fn + " (continuing)"
            continue
        
        try :
            # create a photoset for this album
            if not set_exists(photoset):
                # if you create a set with a primary photo it is implicitly added to the set
                print "creating photoset %s with photo %s" % (photoset, photo_id)
                flickr.photosets_create(api_key=flickr_api_key, title=photoset, primary_photo_id=photo_id)
                # reload the sets
                sets = flickr.photosets_getList(api_key=flickr_api_key).find('photosets').findall('photoset')
            else:
                # add it to an existing set
                print "adding photo %s to set %s" % (photo_id, photoset)
                theSet = set_with_name(sets, photoset)
                flickr.photosets_addPhoto(api_key=flickr_api_key,photoset_id=theSet.attrib['id'], photo_id=photo_id)
        except :
            # here's what can happen: you add a photo successfully; flickr gives
            # you an id, you try to immediately reference that id to add the photo
            # to a set and it complains that the photo doesn't exist.  My guess
            # is that this is a master/slave delay, we just log such errors
            print "FlickrError " , sys.exc_info()[0]
            
            
            