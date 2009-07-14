import re
import sys

# used to translate SmugMug albums names to directory names
album_title_regex = re.compile("[^\w()]+")

# returns:
#   prettified album title
def build_album_dirname(raw_title, id):
    sanitized_title = album_title_regex.sub("-", raw_title)
    return "%s-%s" % (sanitized_title, id)

def log(message, newline=True):
    if newline:
        message = message + "\n"

    sys.stdout.write(message)
    sys.stdout.flush()

def error(message):
    sys.stderr.write("%s\n" % message)
    sys.stderr.flush()

def fail(message, code=1):
    error("ERROR - %s\n" % message)
    sys.exit(code)
