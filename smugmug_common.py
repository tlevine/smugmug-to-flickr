def login(sapi, config):
    result=sapi.login_withPassword (EmailAddress = config.smugmug_email, Password = config.smugmug_passwd)
    return result.Login[0].Session[0]["id"]
