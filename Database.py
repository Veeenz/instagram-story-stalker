from pymongo import MongoClient

class Database:
    def __init__(self, database):
        client = MongoClient()
        self.db = client[database]
        pass

    def save(self, document, data):
        result = self.db[document].insert_one(data)
        return hasattr(result,'inserted_id')
    def fetch(self, document, key, value, multiple=False):
        if key == '' and value == '' and multiple == True:
            return self.db[document].find()
        if multiple:
            return self.db[document].find({key: value})    
        return self.db[document].find_one({key: value})

    def append(self, document, key, value, field, data):
        return self.db[document].update_one(
            {key:value}, 
            {
                '$push':
                    {
                        field: data
                    }
                }
            )
