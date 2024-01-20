from pymongo import MongoClient
from bson import ObjectId
from flask import Flask, request, jsonify
from pymongo.errors import DuplicateKeyError
from bson import json_util
from pydantic import BaseModel
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
import nltk

class UserInput(BaseModel):
    text: str
    userId: str

# Download NLTK resources (you can also do this manually outside of the code)
nltk.download('stopwords')
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')


class MongoDBHandler:
    # Class variable for MongoDB URI
    mongo_uri = 'mongodb+srv://passwordisSArthak:passwordisSArthak@cluster0.b8muydt.mongodb.net/chatbotDb?retryWrites=true&w=majority'

    # def __init__(self):
    #     self.client = MongoClient(self.mongo_uri)
    #     self.db = self.client.get_default_database()

    def connect_to_mongo(self, dbName):
        try:
            mongo_uri = f'mongodb+srv://passwordisSArthak:passwordisSArthak@cluster0.b8muydt.mongodb.net/{dbName}?retryWrites=true&w=majority'
            client = MongoClient(mongo_uri)
            return client.get_default_database()
        except Exception as e:
            print(f"Error connecting to MongoDB: {str(e)}")
            raise e

    def add_data(self, new_data,  dbName ,collection_name='Sample'):
        db = self.connect_to_mongo(dbName)
        self.create_collection_if_not_exists(collection_name, new_data, db)
        db[collection_name].insert_one(new_data)

        return {'message': 'Data added successfully'}

    def create_collection_if_not_exists(self, collection_name, data, db):
        collection = db[collection_name]

        if collection_name not in db.list_collection_names():
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
            collection_info = db.collectioninfos.find_one({'collectionName': collection_name})
            new_fields = set(list(data.keys()))
            existing_fields = set(collection_info.get('fields', []))
            updated_fields = list(existing_fields.union(new_fields))

            db.collectioninfos.update_one(
                {'collectionName': collection_name},
                {'$set': {'fields': updated_fields}}
            )

    def get_collection_info(self, collection_name, dbName):
        try:
            db = self.connect_to_mongo(dbName)

            collection_info = db.collectioninfos.find_one({'collectionName': collection_name})

            if not collection_info:
                return {'error': 'Collection not found'}

            return {'collectionName': collection_info['collectionName'], 'fields': collection_info.get('fields', [])}
        except Exception as e:
            return {'error': str(e)}

    def get_all_collections(self, dbName):
        try:
            db = self.connect_to_mongo(dbName)

            all_collections_data = db.allcollections.find_one()
            collection_names = all_collections_data.get('collectionNames', []) if all_collections_data else []
            return {'allCollections': collection_names}
        except Exception as e:
            return {'error': str(e)}

    def process_input_api(self, user_input: UserInput):
      try:
          text = user_input.text
          words = word_tokenize(text)
          sentences = sent_tokenize(text)
          stop_words = set(stopwords.words('english'))
          filtered_words = [word for word in words if word.lower() not in stop_words]

          userId = user_input.userId
          db = self.connect_to_mongo(userId)
          collection = db["allcollections"]
          collection_info = db["collectioninfos"]

          result_collections = []
          remaining_strings = set(filtered_words)

          result = collection.find_one()
          if result and "collectionNames" in result:
              user_collections = set(result["collectionNames"])
              result_collections = list(user_collections.intersection(remaining_strings))
              remaining_strings -= set(result_collections)

          collection_objects = []

          if not result_collections:
              matching_docs = collection_info.find({"fields": {"$in": list(remaining_strings)}})
              for doc in matching_docs:
                  collection_name = doc["collectionName"]
                  fields = doc["fields"]
                  matching_fields = list(set(remaining_strings).intersection(set(fields)))
                  if matching_fields:
                      collection_objects.append({
                          "collectionName": collection_name,
                          "fields": matching_fields
                      })
                      remaining_strings -= set(matching_fields)
          else:
              for collection_name in result_collections:
                  info_doc = collection_info.find_one({"collectionName": collection_name})
                  if info_doc and "fields" in info_doc:
                      matching_fields = list(set(remaining_strings).intersection(set(info_doc["fields"])))
                      if matching_fields:
                          collection_objects.append({
                              "collectionName": collection_name,
                              "fields": matching_fields
                          })
                          remaining_strings -= set(matching_fields)
          
          if not collection_objects:
            return self.calculate_sum_of_amount(db, collection_name)

          leftover_strings = list(remaining_strings)

          if len(leftover_strings)==0 or len(collection_objects[0]["fields"]):
            return self.calculate_sum_of_amount(db, collection_objects[0]["collectionName"])

          result_array = []
          for item in collection_objects:
              collection_name = item.get('collectionName')

              if not collection_name:
                  continue

              fields = item.get('fields', [])
              collection = db[collection_name]
              query = {field: {"$exists": True} for field in fields}  # Modified this line

              all_documents = list(collection.find(query))
              
              for x in all_documents:
                  for key, value in x.items():
                      if isinstance(value, ObjectId):
                          x[key] = str(value)

                  flag = all(x[field] in leftover_strings for field in fields)
                  if flag:
                      result_array.append(x)

          return result_array

      except Exception as e:
          raise e

# Helper function to calculate total amount

    def calculate_sum_of_amount(self, db, collectionName):
      try:
          collection = db[collectionName]
          total_amount = 0
          for document in collection.find():
              amount = document.get("amount")
              if amount is not None:
                  try:
                      amount = float(amount)
                      total_amount += amount
                  except ValueError:
                      print(f"Skipping invalid amount in document with _id: {document.get('_id')}")

          return {"total_sum": str(total_amount)}

      except Exception as e:
          print(f"An error occurred: {str(e)}")
          raise e


app = Flask(__name__)
mongo_handler = MongoDBHandler()

@app.get("/")
def read_root():
    return {"message": "Hello, World!"}

@app.route('/add_data', methods=['POST'])
def add_data():
    try:
        data = request.json
        dbName = data.get('dbName')
        collection_name = data.get('collectionName', 'Sample')
        new_data = data.get('newData', {})

        result = mongo_handler.add_data(new_data, dbName, collection_name)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/get_collection_info', methods=['GET'])
def get_collection_info():
    try:
        collection_name = request.args.get('collectionName')
        dbName = request.args.get('dbName')

        result = mongo_handler.get_collection_info(collection_name, dbName)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/get_all_collections', methods=['GET'])
def get_all_collections():
    try:
        dbName = request.args.get('dbName')

        result = mongo_handler.get_all_collections(dbName)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route("/process_input_api", methods=["POST"])
def process_input_api():
    try:
        user_input = UserInput(**request.json)
        result = mongo_handler.process_input_api(user_input)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)})



# Get the dev server port (defaults to 5000 for Flask, can be overridden with `--port` when starting the server)
port = 5000

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=port)
