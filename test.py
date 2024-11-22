from database.elasticsearch import Elastic

elastic = Elastic("https://85.202.160.193:9200", "elastic", "i5rTHL8FwoMCP65-I7Vn" )

# data = {"Name": "Hitesh", "Class": "10"}

# elastic.add("test", data, "8920916103")

result = elastic.get_all_document_ids("test")
print(result)