from pymongo import MongoClient

mongo_uri = 'mongodb+srv://passwordisSArthak:passwordisSArthak@cluster0.b8muydt.mongodb.net/your_database_name?retryWrites=true&w=majority'
client = MongoClient(mongo_uri)
db = client.get_default_database()

# CollectionInfo schema
collection_info_schema = {
    'collectionName': 'string',
    'fields': ['string'],
}

# AllCollections schema
all_collections_schema = {
    'collectionNames': ['string'],
}

# Function to connect to MongoDB
def connect_to_mongo():
    try:
        client = MongoClient(mongo_uri)
        return client.get_default_database()
    except Exception as e:
        print(f"Error connecting to MongoDB: {str(e)}")
        raise e

# Function to add new data to a collection
def add_data(new_data, collection_name='Sample'):
    db = connect_to_mongo()

    # Check if the collection exists, create it if not
    create_collection_if_not_exists(collection_name, new_data, db)

    # Save new data to the collection
    db[collection_name].insert_one(new_data)

    return {'message': 'Data added successfully'}

# Helper function to create a collection if it doesn't exist
def create_collection_if_not_exists(collection_name, data, db):
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


# Function to get collection information
def get_collection_info(collection_name):
    try:
        db = connect_to_mongo()

        collection_info = db.collectioninfos.find_one({'collectionName': collection_name})

        if not collection_info:
            return {'error': 'Collection not found'}

        return {'collectionName': collection_info['collectionName'], 'fields': collection_info.get('fields', [])}
    except Exception as e:
        return {'error': str(e)}

# Function to get all collections
def get_all_collections():
    try:
        db = connect_to_mongo()

        all_collections_data = db.allcollections.find_one()
        collection_names = all_collections_data.get('collectionNames', []) if all_collections_data else []
        return {'allCollections': collection_names}
    except Exception as e:
        return {'error': str(e)}


#How to implement:
# Example: Add data
data_to_add = {'name2': 'Sarthak', 'roll': 12}
add_data(data_to_add, 'new')
# Example: Get collection information
collection_info = get_collection_info('new')
print(collection_info)
# Example: Get all collections
all_collections = get_all_collections()
print(all_collections)
