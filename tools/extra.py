
class Extra:

    def __init__(self):
        self.__ext = {}

    async def put(self, key: str, value):
        self.__ext[key] = value

    async def get(self, key: str, default_value = None):
        if key in self.__ext:
            return self.__ext[key]
        return default_value

    async def fetch(self, key: str, default_value=None):
        if key in self.__ext:
            fetched = self.__ext[key]
            del self.__ext[key]
            return fetched
        return default_value

    async def purge(self):
        self.__ext = {}