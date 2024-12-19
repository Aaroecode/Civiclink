from elasticsearch import Elasticsearch
from utils.logging import elastic_logger
import uuid, os, json
uuid_file =  os.path.join(os.getcwd(), "database", "uuids.json")

cert_path = os.path.join(os.getcwd(), "database", "http_ca.crt")
class Elastic(Elasticsearch):
    def __init__(self, host, username: str, password:str) -> None:
        super().__init__(hosts=[host], http_auth=(username, password), verify_certs=True, ca_certs=cert_path)
        if self.ping():
            elastic_logger.info("Connected to Elastic")
        else:
            elastic_logger.error("Failed to connect to Elastic")


    def generate_uuid(self):
        with open(uuid_file, "r") as file:
            uuids = set(json.load(file))
        new_id = str(uuid.uuid4())
        while new_id in uuids:
            new_id = str(uuid.uuid4())
        uuids.add(new_id)
        
        with open(uuid_file, "w") as f:
            json.dump(list(uuids), f)
        return new_id

    def add(self, index, data, id=None):
        try:
            if not self.indices.exists(index=index):
                self.indices.create(index=index)
                elastic_logger.info(f"Index created successfully: {index}")
        except Exception as e:
            elastic_logger.error(f"Error checking or creating index: {e}")
            print(f"Error checking or creating index: {e}")
        if id is None:
            id = self.generate_uuid()
            
        
        try:
            response = self.index(index=index, id=id, document=data)
            elastic_logger.info(f"Data indexed successfully with ID: {response['result']}, Data: {data}")
        except Exception as e:
            elastic_logger.error(f"Error indexing data: {e}")
        return id
    
    def find(self, index, id):
        try:
            response = self.get(index=index, id= id)
            elastic_logger.info(f"Data found successfully with ID: {id}, Data: {response['_source']}")
            return response["_source"]
        except Exception as e:
            elastic_logger.error(f"Error finding data: {e}")
            return None
    
    def get_all_document_ids(self, index):
        try:
            if not self.indices.exists(index=index):        
                self.indices.create(index=index)
            elastic_logger.info(f"Index created successfully: {index}")
        except Exception as e:
            elastic_logger.error(f"Error checking or creating index: {e}")

        try:
            response = self.search(
                index=index,
                body={"query": {"match_all": {}}},
                _source=False, 
                scroll="2m",    
                size=1000       
            )
            document_ids = []

            scroll_id = response['_scroll_id']
            hits = response['hits']['hits']

            document_ids.extend([hit['_id'] for hit in hits])

            while len(hits) > 0:
                response = self.scroll(
                    scroll_id=scroll_id,
                    scroll="2m"
                )
                hits = response['hits']['hits']
                document_ids.extend([hit['_id'] for hit in hits])
            
            elastic_logger.info(f"Document IDs fetched successfully: {document_ids}")
            return document_ids
        except Exception as e:
            elastic_logger.error(f"Error fetching document IDs: {e}")
            return None

