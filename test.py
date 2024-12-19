from database.elasticsearch import Elastic
import time

RATE_LIMIT_WINDOW = 86400

elastic = Elastic("https://127.0.0.1:9200", "elastic", "i5rTHL8FwoMCP65-I7Vn" )

# data = {"Name": "Hitesh", "Class": "10"}

# elastic.add("test", data, "8920916103")

query = {"bool": {"must": [{ "term": { "user": "918920916103" } }],"filter": [{"range": {"timestamp": {"gt": time.time() - RATE_LIMIT_WINDOW}}}]}}
print(time.time() - RATE_LIMIT_WINDOW)
tickets_filed = elastic.search(index = "tickets", query = query, size = 1000)
print(tickets_filed)