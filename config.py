import ConfigParser


class Configuration:

    def __init__(self, path):
        # read config
        config = ConfigParser.ConfigParser()
        config.read(path)

        self.smugmug_email = config.get('SmugMug', "email")
        self.smugmug_api_key = config.get('SmugMug', "api_key")
        self.smugmug_passwd = config.get('SmugMug', "passwd")
        self.smugmug_short_username = config.get('SmugMug', "username")
    
        self.flickr_api_key=config.get('Flickr', "api_key")
        self.flickr_api_secret=config.get('Flickr', "api_secret")
        self.flickr_user_id=config.get('Flickr', "user_id")

# returns:
#   a Configuration instance
def load():
    return Configuration("config.cfg")
