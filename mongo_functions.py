from pymongo import MongoClient

class MongoDBHandler:
    # Class variable for MongoDB URI
    mongo_uri = 'mongodb+srv://passwordisSArthak:passwordisSArthak@cluster0.b8muydt.mongodb.net/your_database_name?retryWrites=true&w=majority'

    def __init__(self):
        self.client = MongoClient(self.mongo_uri)
        self.db = self.client.get_default_database()

    def connect_to_mongo(self):
        try:
            client = MongoClient(self.mongo_uri)
            return client.get_default_database()
        except Exception as e:
            print(f"Error connecting to MongoDB: {str(e)}")
            raise e

    def add_data(self, new_data, collection_name='Sample'):
        db = self.connect_to_mongo()

        # Check if the collection exists, create it if not
        self.create_collection_if_not_exists(collection_name, new_data, db)

        # Save new data to the collection
        db[collection_name].insert_one(new_data)

        return {'message': 'Data added successfully'}

    def create_collection_if_not_exists(self, collection_name, data, db):
        collection = db[collection_name]

        if collection_name not in db.list_collection_names():
            # Collection doesn't exist, create it and update collection info
            collection_info = {
                'collectionName': collection_name,
                'fields': list(data.keys())
            }
            db.collectioninfos.insert_one(collection_info)

            all_collections_data = db.allcollections.find_one()
            if not all_collections_data:
                db.allcollections.insert_one({'collectionNames': [collection_name]})
            else:
                db.allcollections.update_one({}, {'$addToSet': {'collectionNames': collection_name}})
        else:
            # Collection exists, update collection info
            collection_info = db.collectioninfos.find_one({'collectionName': collection_name})
            new_fields = set(list(data.keys()))
            existing_fields = set(collection_info.get('fields', []))
            updated_fields = list(existing_fields.union(new_fields))

            db.collectioninfos.update_one(
                {'collectionName': collection_name},
                {'$set': {'fields': updated_fields}}
            )

    def get_collection_info(self, collection_name):
        try:
            db = self.connect_to_mongo()

            collection_info = db.collectioninfos.find_one({'collectionName': collection_name})

            if not collection_info:
                return {'error': 'Collection not found'}

            return {'collectionName': collection_info['collectionName'], 'fields': collection_info.get('fields', [])}
        except Exception as e:
            return {'error': str(e)}

    def get_all_collections(self):
        try:
            db = self.connect_to_mongo()

            all_collections_data = db.allcollections.find_one()
            collection_names = all_collections_data.get('collectionNames', []) if all_collections_data else []
            return {'allCollections': collection_names}
        except Exception as e:
            return {'error': str(e)}




mongo_handler = MongoDBHandler()

# Adding new data to a collection
new_data = {'field1': 'value1', 'field2': 'value2'}
response = mongo_handler.add_data(new_data, collection_name='ExampleCollection')
print(response)

# Getting information about a specific collection
collection_info = mongo_handler.get_collection_info('ExampleCollection')
print(collection_info)

# Getting information about all collections
all_collections = mongo_handler.get_all_collections()
print(all_collections)
