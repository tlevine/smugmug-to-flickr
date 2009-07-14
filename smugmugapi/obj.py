# Copyright (c) 2007 by the respective coders, see
# http://code.google.com/p/smugmug-api/
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import smugmugapi as SI
import logging 

########################################################################
class LazyLoad (object):
    def __init__ (self, instance, load_var, load_class, args):
        # since the lazy load instanc is set in the class, the context
        # has to be stored outside of the lazyload instance as the
        # instance will be shared amongst multiple instances of the
        # class.
        setattr (instance, '_lazyload_%s'%load_var, {"load_var":load_var, "load_class":load_class, "args":args})
        self.load_var = load_var # this is the key to access context
        return

    def __get__(self, inst, obj_type=None):
        if not hasattr(inst, '_cache_%s'%self.load_var):
            load_info = getattr (inst, '_lazyload_%s'%self.load_var)
            print load_info
            try:
                actual_instance = load_info["load_class"].get(**load_info["args"])
            except SI.SmugMugError:
                actual_instance = None
            setattr (inst, '_cache_%s'%self.load_var, actual_instance)
        return getattr (inst, '_cache_%s'%self.load_var)

########################################################################
class Session (object):
    def __init__ (self, api, email=None, password=None, fail_on_error = True):
        if email is not None and password is not None:
            result = api.login_withPassword (EmailAddress = email, Password = password)
        else:
            result = api.login_anonymously ()
        
        self.api = api
        self.id = result.Login[0].Session[0]["id"]
        SI.set_log_level(logging.DEBUG)
        return

    def logout ():
        return

########################################################################
class SmugBase (object):
    def __init__ (self, **args):
        self.__load_required = False
        self.__def_gets = {}

        # assign None/default values to all the variables
        # TODO : Change None to appropriate construct to derive the default value 
        for var in self.__class__._readonly.iterkeys():
            setattr (self, "__"+var, None )                
        for var in self.__class__._readwrite.iterkeys():
            setattr (self, var, None)
#         for var in self.__class__._all_foreign_keys.iterkeys():
#             setattr (self, var, None)
        setattr (self, self.__class__._primary_key.keys()[0], None)  # at the moment only one primary key is supported
            
        # now assign the arguments
        for a in args.iterkeys():
            if a in self.__class__._readonly_vars:
                raise AttributeError("The attribute %s is read-only." % a)
            elif a in self.__class__._readwrite_vars:
                setattr (self, a, args[a])
            elif a in self.__class__._all_foreign_keys_vars:
                setattr (self, a, args[a])
            elif a in self.__class__._primary_key.keys():
                setattr (self, a, args[a])
            else:
                raise AttributeError("The attribute %s is unknown." % a)
        return

    def __repr__ (self):
        return "%s : %s" % (self.__class__.__name__, getattr (self, self.__class__._primary_key.keys()[0]))
    __str__ = __repr__

    @classmethod
    def get (cls, session, args):
        raise AttributeError, "This method is undefined"

    @classmethod
    def get_all (cls, session, id):
        raise AttributeError, "This method is undefined"

    @classmethod
    def create (cls, session, id):
        raise AttributeError, "This method is undefined"

    @classmethod
    def save (cls, session, id):
        raise AttributeError, "This method is undefined"

    @classmethod
    def delete (cls, session, id):
        raise AttributeError, "This method is undefined"

    def _prepare_for_save (self):
        if getattr (self, self._primary_key.keys()[0]) == None:
            raise AttributeError("Mandatory primary_key %s is required." % prop)            
        
        args = {}
        for prop in self._non_null_foreign_keys:
            if getattr(self, prop) is None:
                raise AttributeError("Mandatory foreign_key %s is required." % prop)
            else:
                args[self._non_null_foreign_keys [prop]["variable"]] = (getattr(self, prop)).id

        for prop in self._null_foreign_keys:
            if getattr(self, prop) is not None:
                args[self._null_foreign_keys [prop]["variable"]] = (getattr(self, prop)).id
            else:
                args[self._null_foreign_keys [prop]["variable"]] = 0

        for prop in self._readwrite:
            args [prop] = getattr (self, prop)

        args[self._primary_key ["id"]["variable"]] = self.id
        return args

#     def __setattr__(self, key, value):
#         " track changes."
#         self.modified = True # this flag will be reset when a save/load_properties is performed
#         super(self.__class__, self).__setattr__(key, value)


class Category (object):
    pass
########################################################################
class Highlight (SmugBase):
    _readonly = {}
    _readonly_vars = _readonly.keys()

    _readwrite = {}
    _readwrite_vars = _readwrite.keys()

    _non_null_foreign_keys = {'session': {"class": Session, "variable":"SessionID"},
                              'category': {"class": Category, "variable":"CategoryID"},}
    _null_foreign_keys = {}

    _all_foreign_keys = _non_null_foreign_keys
    _all_foreign_keys.update(_non_null_foreign_keys)    
    _all_foreign_keys_vars = _all_foreign_keys.keys()

    _primary_key = {"id":{"variable":"HighlightID"}} 

    @classmethod
    def get (cls, session, category, id):
        return None

########################################################################
class Community (SmugBase):
    _readonly = {}
    _readonly_vars = _readonly.keys()

    _readwrite = {}
    _readwrite_vars = _readwrite.keys()

    _non_null_foreign_keys = {'session': {"class": Session, "variable":"SessionID"},}
    _null_foreign_keys = {}

    _all_foreign_keys = _non_null_foreign_keys
    _all_foreign_keys.update(_non_null_foreign_keys)    
    _all_foreign_keys_vars = _all_foreign_keys.keys()

    _primary_key = {"id":{"variable":"CommunityID"}} 

    @classmethod
    def get (cls, session, id):
        return None

########################################################################
class Category (SmugBase):
    _readonly = {}
    _readonly_vars = _readonly.keys()

    _readwrite = {'Name':{},}
    _readwrite_vars = _readwrite.keys()

    _non_null_foreign_keys = {'session': {"class": Session, "variable":"SessionID"},}
    _null_foreign_keys = {}

    _all_foreign_keys = _non_null_foreign_keys
    _all_foreign_keys.update(_non_null_foreign_keys)    
    _all_foreign_keys_vars = _all_foreign_keys.keys()

    _primary_key = {"id":{"variable":"CategoryID"}} 

    @classmethod
    def get_all (cls, session, NickName=None, SitePassword=None):
        try:
            result = session.api.categories_get(SessionID=session.id, NickName=NickName, 
                                                SitePassword=SitePassword)
            category_list = []
            for category in result.Categories[0].Category:
                category_list.append(Category (session = session, id=category["id"], 
                                               Name=category["Name"]))
            return category_list
        except:
            raise
                                     
    @classmethod
    def get (cls, session, id):
        ''' This method is a hack as there is no way to enquire the site statistics '''
        category_list = Category.get_all(session)
        for category in category_list:
            if category.id == id:
                return category
        raise AttributeError #TBD

    @classmethod
    def create (cls, session, Name):
        result = session.api.categories_create (SessionID=session.id, Name=Name)
        return (Category(session=session, id=id, Name=Name)) # there is no way to fetch the category

    def delete (self):
        result = session.api.categories_delete (SessionID=self.session.id, CategoryID=self.id)
        return

    def save (self):
        ''' Will be mainly used for renames '''
        result = session.api.categories_rename (SessionID=self.session.id, CategoryID=self.id, Name=self.Name),
        return
        
    
        
########################################################################
class SubCategory (SmugBase):
    _readonly = {}
    _readonly_vars = _readonly.keys()

    _readwrite = {'Name':{},}
    _readwrite_vars = _readwrite.keys()

    _non_null_foreign_keys = {'session': {"class": Session, "variable":"SessionID"},
                              'category': {"class": Category, "variable":"CategoryID"},}
    _null_foreign_keys = {}

    _all_foreign_keys = _non_null_foreign_keys
    _all_foreign_keys.update(_non_null_foreign_keys)    
    _all_foreign_keys_vars = _all_foreign_keys.keys()

    _primary_key = {"id":{"variable":"SubCategoryID"}} 


    @classmethod
    def get_all (cls, session, category=None, NickName=None, SitePassword=None):
        try:
            if category:
                result = session.api.subcategories_get(SessionID=session.id, Category=category.id,
                                                       NickName=NickName, SitePassword=SitePassword)
            else:
                result = session.api.subcategories_get(SessionID=session.id, 
                                                       NickName=NickName, SitePassword=SitePassword)
            
            subcategory_list = []
            for subcategory in result.Subcategories[0].Subcategory:
                if not category:
                    category = XYZ 
                subcategory_list.append(SubCategory (session=session, category=category,
                                                     id=subcategory["id"], Name=subcategory["Name"]))
            return subcategory_list
        except:
            raise
                                     
    @classmethod
    def get (cls, session, id, category, NickName=None, SitePassword=None):
        ''' This method is a hack as there is no way to enquire the site statistics '''
        result = session.api.subcategories_get(SessionID=session.id, CategoryID=category.id,
                                               NickName=NickName, SitePassword=SitePassword)
        sub_category = SubCategory (session=session, id=id, category=category)
        for prop in cls._readwrite.iterkeys():
            setattr (sub_category, prop, result.Album[0][prop])
        for prop in cls._readonly.iterkeys():
            setattr (sub_category, prop, result.Album[0][prop])
        return (sub_category)
            
    @classmethod
    def create (cls, session, Name):
        result = session.api.categories_create (SessionID=session.id, Name=Name)
        return (Category(session=session, id=id, Name=Name)) # there is no way to fetch the category

    def delete (self):
        result = session.api.categories_delete (SessionID=self.session.id, CategoryID=self.id)
        return

    def save (self):
        ''' Will be mainly used for renames '''
        result = session.api.categories_rename (SessionID=self.session.id, CategoryID=self.id, Name=self.Name),
        return
        

########################################################################
class Album (SmugBase):

    # Meta descriptors - default, variable, class

    _readonly = {'LastUpdated':{},}
    _readonly_vars = _readonly.keys()

    _readwrite = {'Position': {}, 
                   'ImageCount': {}, 
                   'Title': {}, 
                   'Description': {}, 
                   'Keywords': {}, 
                   'Public': {}, 
                   'Password': {}, 
                   'PasswordHint': {}, 
                   'Printable': {}, 
                   'Filenames': {}, 
                   'Comments': {}, 
                   'External': {}, 
                   'Originals': {}, 
                   'EXIF': {}, 
                   'Share': {}, 
                   'SortMethod': {}, 
                   'SortDirection': {}, 
                   'FamilyEdit': {}, 
                   'FriendEdit': {}, 
                   'HideOwner': {}, 
                   'CanRank': {}, 
                   'Clean': {}, 
                   'Geography': {}, 
                   'SmugSearchable': {}, 
                   'WorldSearchable': {}, 
                   'X2Larges': {}, 
                   'X3Larges': (),
                   }
    _readwrite_vars = _readwrite.keys()

    _non_null_foreign_keys = {'session': {"class": Session, "variable":"SessionID"},
                               'category': {"class": Category, "variable":"CategoryID"},}

    _null_foreign_keys = {'subcategory':{"class": SubCategory, "variable":"SubCategoryID"},
                           'highlight':{"class": Highlight, "variable":"HighlightID"},
                           'community':{"class": Community, "variable":"CommunityID"},}

    _all_foreign_keys = _non_null_foreign_keys
    _all_foreign_keys.update(_non_null_foreign_keys)    
    _all_foreign_keys_vars = _all_foreign_keys.keys()

    _primary_key = {"id":{"variable":"AlbumID"}} # only one primary key is supported

    def save(self):
        args = self._prepare_for_save ()            
        result = self.session.api.albums_changeSettings (**args)
        return

    @classmethod
    def create (cls, session, Title, category, **args):
        
        result = session.api.albums_create (SessionID=session.id, Title=Title, 
                                            CategoryID=category.id)
        return Album.get (session=session, id=result.Album[0]["id"])
    
    @classmethod
    def get_all (cls, session, NickName=None, Heavy=None, SitePassword=None):
        result = session.api.albums_get (SessionID=session.id, NickName=NickName, 
                                         Heavy=Heavy, SitePassword=SitePassword)
        album_list=[]
        for album in result.Albums[0].Album:
            album_list.append(Album(session=session, id=album["id"]))
        return album_list

    @classmethod
    def get (cls, session, id):
        try:
            result = session.api.albums_getInfo(SessionID=session.id, AlbumID=id)
            a = Album (session=session, id=id)
            for prop in cls._readwrite.iterkeys():
                setattr (a, prop, result.Album[0][prop])
            for prop in cls._readonly.iterkeys():
                setattr (a, prop, result.Album[0][prop])
                
            a.__class__.category = LazyLoad (a, "category", Category, {"session":a.session, 
                                                                       "id":result.Album[0].Category[0]["id"]})
            a.__class__.subcategory = LazyLoad (a, "subcategory", SubCategory, {"session":a.session, "category":a.category, 
                                                                                "id":result.Album[0].SubCategory[0]["id"]})
            a.__class__.highlight = LazyLoad (a, "highlight", Highlight, {"session":a.session, "category":a.category, 
                                                                          "id":result.Album[0].Highlight[0]["id"]})
            a.__class__.community = LazyLoad (a, "community", Community, {"session":a.session, 
                                                                          "id":result.Album[0].Community[0]["id"]})
        except:
            raise
        return a

    def delete (self):
        response = self.session.api.albums_delete (SessionID=self.session.id, 
                                                   AlbumID = self.id)
        return

    def resort (self, By, Direction):
        return

    def upload ():
        return

    def get_statistics (self, Month=None, Year=None, Heavy=None):
        response = self.session.api.albums_getStats (SessionID=self.session.id, 
                                                     AlbumID = self.id, Month=Month, 
                                                     Year=Year, Heavy=Heavy)
        
        reply = {}
        reply["Bytes"] = response.Album[0]["Bytes"]
        reply["Tiny"] = response.Album[0]["Tiny"]
        reply["Thumb"] = response.Album[0]["Thumb"]
        reply["Small"] = response.Album[0]["Small"]
        reply["Medium"] = response.Album[0]["Medium"]
        reply["Large"] = response.Album[0]["Large"]
        reply["Original"] = response.Album[0]["Original"]
        return reply
    

########################################################################
class Family (SmugBase):
    _readonly = {}
    _readonly_vars = _readonly.keys()

    _readwrite = {}
    _readwrite_vars = _readwrite.keys()

    _non_null_foreign_keys = {}
    _null_foreign_keys = {}

    _all_foreign_keys = _non_null_foreign_keys
    _all_foreign_keys.update(_non_null_foreign_keys)    
    _all_foreign_keys_vars = _all_foreign_keys.keys()

    _primary_key = {"id":{"variable":"FamilyID"}} 


########################################################################        
class Friend (SmugBase):
    _readonly = {}
    _readonly_vars = _readonly.keys()

    _readwrite = {}
    _readwrite_vars = _readwrite.keys()

    _non_null_foreign_keys = {}
    _null_foreign_keys = {}

    _all_foreign_keys = _non_null_foreign_keys
    _all_foreign_keys.update(_non_null_foreign_keys)    
    _all_foreign_keys_vars = _all_foreign_keys.keys()

    _primary_key = {"id":{"variable":"FriendID"}} 


########################################################################
class Order (SmugBase):
    _readonly = {}
    _readonly_vars = _readonly.keys()

    _readwrite = {}
    _readwrite_vars = _readwrite.keys()

    _non_null_foreign_keys = {}
    _null_foreign_keys = {}

    _all_foreign_keys = _non_null_foreign_keys
    _all_foreign_keys.update(_non_null_foreign_keys)    
    _all_foreign_keys_vars = _all_foreign_keys.keys()

    _primary_key = {"id":{"variable":"OrderID"}} 


########################################################################
class PropPricing (SmugBase):
    _readonly = {}
    _readonly_vars = _readonly.keys()

    _readwrite = {}
    _readwrite_vars = _readwrite.keys()

    _non_null_foreign_keys = {}
    _null_foreign_keys = {}

    _all_foreign_keys = _non_null_foreign_keys
    _all_foreign_keys.update(_non_null_foreign_keys)    
    _all_foreign_keys_vars = _all_foreign_keys.keys()

    _primary_key = {"id":{"variable":"PropPricingID"}} 


########################################################################
class Style (SmugBase):
    _readonly = {}
    _readonly_vars = _readonly.keys()

    _readwrite = {}
    _readwrite_vars = _readwrite.keys()

    _non_null_foreign_keys = {}
    _null_foreign_keys = {}

    _all_foreign_keys = _non_null_foreign_keys
    _all_foreign_keys.update(_non_null_foreign_keys)    
    _all_foreign_keys_vars = _all_foreign_keys.keys()

    _primary_key = {"id":{"variable":"StyleID"}} 

########################################################################
class ShareGroup (SmugBase):
    _readonly = {}
    _readonly_vars = _readonly.keys()

    _readwrite = {}
    _readwrite_vars = _readwrite.keys()

    _non_null_foreign_keys = {}
    _null_foreign_keys = {}

    _all_foreign_keys = _non_null_foreign_keys
    _all_foreign_keys.update(_non_null_foreign_keys)    
    _all_foreign_keys_vars = _all_foreign_keys.keys()

    _primary_key = {"id":{"variable":"SharegroupID"}} 


########################################################################
class Theme (SmugBase):
    _readonly = {}
    _readonly_vars = _readonly.keys()

    _readwrite = {}
    _readwrite_vars = _readwrite.keys()

    _non_null_foreign_keys = {}
    _null_foreign_keys = {}

    _all_foreign_keys = _non_null_foreign_keys
    _all_foreign_keys.update(_non_null_foreign_keys)    
    _all_foreign_keys_vars = _all_foreign_keys.keys()

    _primary_key = {"id":{"variable":"ThemeID"}} 

########################################################################
class User (SmugBase):
    _readonly = {}
    _readonly_vars = _readonly.keys()

    _readwrite = {}
    _readwrite_vars = _readwrite.keys()

    _non_null_foreign_keys = {}
    _null_foreign_keys = {}

    _all_foreign_keys = _non_null_foreign_keys
    _all_foreign_keys.update(_non_null_foreign_keys)    
    _all_foreign_keys_vars = _all_foreign_keys.keys()

    _primary_key = {"id":{"variable":"UserID"}}


########################################################################
class Watermark (SmugBase):
    _readonly = {}
    _readonly_vars = _readonly.keys()

    _readwrite = {}
    _readwrite_vars = _readwrite.keys()

    _non_null_foreign_keys = {}
    _null_foreign_keys = {}

    _all_foreign_keys = _non_null_foreign_keys
    _all_foreign_keys.update(_non_null_foreign_keys)    
    _all_foreign_keys_vars = _all_foreign_keys.keys()

    _primary_key = {"id":{"variable":"WatermarkID"}}


########################################################################
class Image (SmugBase):
    _readonly = {'Position':{},
                 'Serial':{},
                 'Size':{},
                 'Width':{},
                 'Height':{},
                 'LastUpdated':{},
                 'FileName':{},
                 'MD5Sum':{},
                 'Watermark':{},
                 'Format':{},
                 'Date':{},
                 'AlbumURL':{},
                 'TinyURL':{},
                 'ThumbURL':{},
                 'SmallURL':{},
                 'MediumURL':{},
                 'LargeURL':{},
                 'XLargeURL':{},
                 'X2LargeURL':{},
                 'X3LargeURL':{},
                 'OriginalURL':{},
                 }
    _readonly_vars = _readonly.keys()

    _readwrite = {'Caption': {},
                  'Keywords':{},
                  }
    _readwrite_vars = _readwrite.keys()

    _non_null_foreign_keys ={'session': {"class": Session, "variable":"SessionID"},
                             'album': {"class": Category, "variable":"AlbumID"},}
    _null_foreign_keys = {}

    _all_foreign_keys = _non_null_foreign_keys
    _all_foreign_keys.update(_non_null_foreign_keys)    
    _all_foreign_keys_vars = _all_foreign_keys.keys()

    _primary_key = {"id":{"variable":"ImageID"}}

    @classmethod
    def get_all (cls, session, album, Heavy=None, Password=None, SitePassword=None):

        result = session.api.images_get(SessionID=session.id, AlbumID=album.id,
                                            Heavy=Heavy, Password=Password,
                                            SitePassword=SitePassword)

        image_list = []
        for image in result.Images[0].Image:
            image_list.append(Image (session = session, id=image["id"]))

        return image_list

    @classmethod
    def get (cls, id, Password=None, SitePassword=None):
        
        result = session.api.images_getInfo(SessionID=session.id, ImageID=id,
                                            Password=Password,
                                            SitePassword=SitePassword)
        image = Image (session=session, id=id)

        for prop in cls._readwrite.iterkeys():
            setattr (a, prop, result.Image[0][prop])
        for prop in cls._readonly.iterkeys():
            setattr (a, prop, result.Image[0][prop])

        image.album = Album.get(session=image.session, id=result.Image[0].Album[0]["id"])
        return image

    def getEXIF (self, id, Password=None, SitePassword=None):
        result = self.session.api.images_getEXIF (SessionID=self.session.id, ImageID=self.id,
                                                  Password = Password, SitePassword = SitePassword)
        return result.Image[0].attrib

    def save(self):
        args = self._prepare_for_save ()            
        result = self.session.api.images_changeSettings (**args)
        return

########################################################################
class AlbumTemplate (SmugBase):
    _readonly = {}
    _readonly_vars = _readonly.keys()

    _readwrite = {"AlbumTemplateName" : {},
                  "SortMethod" : {},
                  "SortDirection" : {},
                  "Public" : {},
                  "Password" : {},
                  "PasswordHint" : {},
                  "Printable" : {},
                  "Filenames" : {},
                  "Comments" : {},
                  "External" : {},
                  "Originals" : {},
                  "EXIF" : {},
                  "Share" : {},
                  "Header" : {},
                  "Larges" : {},
                  "XLarges" : {},
                  "X2Larges" : {},
                  "X3Larges" : {},
                  "Clean" : {},
                  "Protected" : {},
                  "Watermarking" : {},
                  "FamilyEdit" : {},
                  "FriendEdit" : {},
                  "HideOwner" : {},
                  "DefaultColor" : {},
                  "Geography" : {},
                  "CanRank" : {},
                  "ProofDays" : {},
                  "Backprinting" : {},
                  "SmugSearchable" : {},
                  "UnsharpAmount" : {},
                  "UnsharpRadius" : {},
                  "UnsharpThreshold" : {},
                  "UnsharpSigma" : {},
                  "WorldSearchable" : {},
                  }
    _readwrite_vars = _readwrite.keys()

    _non_null_foreign_keys ={'session': {"class": Session, "variable":"SessionID"},
                             'highlight': {"class": Highlight, "variable":"HighlightID"},
#                             'template': {"class": Template, "variable":"TemplateID"},
                             'community': {"class": Community, "variable":"CommunityID"},
                             'watermark': {"class": Watermark, "variable":"WatermarkID"},
                             }
    _null_foreign_keys = {}

    _all_foreign_keys = _non_null_foreign_keys
    _all_foreign_keys.update(_non_null_foreign_keys)    
    _all_foreign_keys_vars = _all_foreign_keys.keys()

    _primary_key = {"id":{"variable":"AlbumTemplateID"}}
        


def main ():
    
    session = Session (SI.SmugMugAPI("29qIYnAB9zHcIhmrqhZ7yK7sPsdfoV0e"), email = '', password = '')

    print "------------------------------------------------------------------------------------------------"
    album = Album.get (session=session, id=3914389)
    print album.Position
    import random
    album.Title = "dXYXYXYXYXYwYsd" + str (random.randint(1,1000000))
    album.save()
    print album.get_statistics (1,2007)


    print "------------------------------------------------------------------------------------------------"
    # Image tests #######################
    album = Album.get (session=session, id=3914389)
    print "Enter a key to view the category"
    raw_input()
    print album.category

    print "------------------------------------------------------------------------------------------------"
    image_list = Image.get_all (session=session, album=album)


    # Album tests #######################
    # get the test album
    print "------------------------------------------------------------------------------------------------"
    album = Album.get (session=session, id=3914389)
    print album.Position
    import random
    album.Title = "dXYXYXYXYXYwYsd" + str (random.randint(1,1000000))
    album.save()
    print album.get_statistics (1,2007)

    print "------------------------------------------------------------------------------------------------"
    album = Album.get (session=session, id=3914389)
    new_album = Album.create (session, "This is a test", album.category)
    print "Enter a key to delete the created album"
    raw_input()
    new_album.delete()
    # Get album list
    print "------------------------------------------------------------------------------------------------"
    album_list = Album.get_all(session)
    print "------------------------------------------------------------------------------------------------"


# run main if we're not being imported:
if __name__ == "__main__":
    main()
    
