from dotenv import load_dotenv
from database.elasticsearch import Elastic
from fastapi import APIRouter, HTTPException, Depends
from api.v1.auth import get_current_user
from models import agents
from elasticsearch import Elasticsearch

import os

INDEX_NAME = "tickets"

load_dotenv()

cert_path = os.path.join(os.getcwd(), "database", "http_ca.crt")
elastic = Elasticsearch(hosts="https://127.0.0.1:9200", http_auth=("elastic", "i5rTHL8FwoMCP65-I7Vn"),verify_certs=True, ca_certs=cert_path)

router = APIRouter()


@router.get("/data")
async def get_data(): #current_user: agents.User = Depends(get_current_user)):
    # Example: Fetch all user data (or adjust to fit your Elasticsearch queries)
    try:
        res = elastic.search(index=INDEX_NAME, query={"match_all": {}}, size = 1000)
        return {"data": [hit["_source"] for hit in res["hits"]["hits"]]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching data: {e}")


@router.get("/test")
async def test(current_user: agents.User = Depends(get_current_user)):
    return {"status": "success", "message": "Database is running"}