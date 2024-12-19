from fastapi import APIRouter, HTTPException, Query # type: ignore
from models.payload import WebhookPayload
from utils.wautils import WhatsAppMessage
from utils.logging import inbound_payload_logger, global_logger
from services.chatflow import chat_flow

router = APIRouter()

@router.get("/")
def verify(hub_mode: str = Query(None, alias="hub.mode"), 
           hub_verify_token: str =  Query(None, alias="hub.verify_token"), 
           hub_challenge: str =  Query(None, alias="hub.challenge") ):
     
    print(hub_challenge, hub_mode, hub_verify_token)
    if hub_mode == 'subscribe' and hub_verify_token == "tensorlabz":
        return int(hub_challenge)

    else:
        return HTTPException(403)


@router.post("/")
async def webhook(data: WebhookPayload):
    payload = {
        "object": data.object,
        "entry": data.entry
    }
    
    inbound_payload_logger.info(payload)
    payload = WhatsAppMessage(payload)
    if not payload.author_id:
        return {"status": "success"}
    try:
        step = chat_flow.next_step(payload.author_id, payload)
        global_logger.info(f"Moving to step: {step} for user: {payload.author_id}")
    except Exception as e:
        global_logger.error(e)
    return {"status": "success"}
    
    