from .Database import MyDatabase

client = MyDatabase.get_instance().client

LoginDatabase = client["login"]