from dotenv import dotenv_values


_temp = dotenv_values()["SECRET_KEY"]
if _temp is None:
    raise Exception("Secret_key is none")
SECRET_KEY = _temp