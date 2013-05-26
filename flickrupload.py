#!/usr/bin/python

import ConfigParser
import md5
from optparse import OptionParser
import os
from os import path
import sys
import traceback
import yaml

from flickrapi import *
from flickrapi.exceptions import FlickrError

from smugmugapi.functional import *

import config as conf
import helper


class Flickrizer:

    progress_per_image = 10

    def __init__(self, options):
        # NOTE: this is clunky
        private_or = lambda x: 0 if options.private else x
        self.__is_public = private_or(1)
        self.__is_friend = private_or(1)
        self.__is_family = private_or(1)
        self.__hidden = private_or(2)

        # read config
        self.config = conf.load()

    def set_exists(self, title, sets):
        return len([s for s in sets if s.find("title").text == title]) > 0

    def set_with_name(self, sets, photoSetName):
        return [s for s in sets if s.find("title").text == photoSetName][0]

    def progress(self, progress, done):
        if done:
            helper.log(":")
        else:
            progress = int(progress)
            # only shows progress if we've moved a significant enough amount
            if (progress % 5 == 0):
                helper.log(".", newline=False)

    def sorted_albums(self, sapi, sessionId):
        albums = sapi.albums_get(SessionID=sessionId, Heavy=1).Albums[0].Album
        albums.sort(lambda a,b : cmp(a["LastUpdated"], b["LastUpdated"]))
        return albums

    def upload(self, flickr, img_fn, meta):
        fn=meta["FileName"]
        caption=meta["Caption"]

        # changes tags to lowercase
        tags=meta["Keywords"].lower()

        try:
            kw = dict(title=fn,
                      tags=tags,
                      is_public=self.__is_public,
                      is_friend=self.__is_friend,
                      is_family=self.__is_family,
                      hidden=self.__hidden,
                      format="etree")
            helper.log("%s " % img_fn, newline=False)
            return flickr.upload(filename=str(img_fn), callback=self.progress, **kw).find("photoid").text
        except Exception, e:
            traceback.print_exc(sys.stderr)
            return None

    # photoset names are unique but smugmug album names aren't.  this method
    # derives a unique photoset name
    def derive_photo_set_name(self, albums, this_album):
        candidates = [a for a in albums if a["Title"] == this_album["Title"]]
        if len(candidates) == 1:
            return this_album["Title"]
        else:
            # create a unique photoset name
            index = [a["id"] for a in candidates].index(this_album["id"]) + 1
            return "%s (%d)" % (this_album["Title"], index)

    def run(self, input_dir, progress_log):
        flickr = FlickrAPI(self.config.flickr_api_key, self.config.flickr_api_secret, username=self.config.flickr_user_id)
        (token, frob) = flickr.get_token_part_one(perms='write')

        if not token:
            raw_input("Press ENTER after you authorized this program")

        tok = flickr.get_token_part_two((token, frob))
        sets = flickr.photosets_getList(api_key=self.config.flickr_api_key).find('photosets').findall('photoset')

        # login to smugmug
        smapi = SmugMugAPI(self.config.smugmug_api_key)
        result=smapi.login_withPassword (EmailAddress = self.config.smugmug_email, Password = self.config.smugmug_passwd)
        smSessionId = result.Login[0].Session[0]["id"]

        previous_uploads = set()
        if path.exists(progress_log):
            with open(progress_log, 'r') as log_stream:
                for line in log_stream:
                    previous_uploads.add(line.strip())
        helper.log("found %s previous upload(s)" % len(previous_uploads))

#        for u in previous_uploads:
#            helper.log("'%s'" % u)

        with open(progress_log, 'a') as log_stream:
            sm_albums = self.sorted_albums(smapi, smSessionId)
            for album in sm_albums:
                photoset = self.derive_photo_set_name(sm_albums, album)
                dirName = helper.build_album_dirname(album["Title"], album["id"])

                helper.log("%s -> '%s'@flickr" % (dirName, photoset))

                # get images from disk
                for f in os.listdir(input_dir + "/" + dirName):
                    if not f.upper().endswith("JPG"):
                        continue

                    img_fn = input_dir + "/" + dirName + "/" + f

                    # skips if we've already uploaded this image
                    if img_fn in previous_uploads:
                        helper.log("%s (skipping)" % img_fn)
                        continue

                    meta = yaml.load(file(img_fn + ".yaml", 'r'))

                    photo_id = self.upload(flickr, img_fn, meta)
                    if photo_id is None:
                        helper.error("error uploading image " + img_fn + " (continuing)")
                        continue

                    log_stream.write("%s\n" % img_fn)
                    log_stream.flush()

                    try :
                        # create a photoset for this album
                        if not self.set_exists(photoset, sets):
                            # if you create a set with a primary photo it is implicitly added to the set
                            helper.log("creating photoset '%s'" % photoset)
                            flickr.photosets_create(api_key=self.config.flickr_api_key, title=photoset, primary_photo_id=photo_id)
                            # reload the sets
                            sets = flickr.photosets_getList(api_key=self.config.flickr_api_key).find('photosets').findall('photoset')
                        else:
                            # add it to an existing set
                            #print "adding photo %s to set %s" % (photo_id, photoset)
                            theSet = self.set_with_name(sets, photoset)
                            flickr.photosets_addPhoto(api_key=self.config.flickr_api_key,photoset_id=theSet.attrib['id'], photo_id=photo_id)
                    except Exception, e:
                        # here's what can happen: you add a photo successfully; flickr gives
                        # you an id, you try to immediately reference that id to add the photo
                        # to a set and it complains that the photo doesn't exist.  My guess
                        # is that this is a master/slave delay, we just log such errors
                        traceback.print_exc(file=sys.stderr)

if __name__ == '__main__':
    parser = OptionParser(usage="%prog [options] <input_dir> <progress_log>")
    parser.add_option("-p", "--private",
                      dest="private",
                      help="set uploaded images as private",
                      action="store_true")
    parser.add_option("-i", "--id",
                      dest="id",
                      help="smugmug album id")

    (options, args) = parser.parse_args()

    if not len(args) == 2:
        parser.print_help(sys.stderr)
        sys.exit(1)

    input_dir = args[0]
    progress_log = args[1]
    Flickrizer(options).run(input_dir, progress_log)
