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
    # Construct the base message data from the incoming payload
    message_data = {
        "object": data.object,
        "entry": data.entry
    }
    
    inbound_payload_logger.info(message_data)
    
    # Parse the incoming message data into a structured WhatsAppMessage object
    whatsapp_message = WhatsAppMessage(message_data)
    
    # If there's no author_id, it's not a user message (e.g., status update)
    if not whatsapp_message.author_id:
        return {"status": "success"}
        
    try:
        # Route the parsed message through the chat flow state machine
        step = chat_flow.next_step(whatsapp_message.author_id, whatsapp_message)
        global_logger.info(f"Moving to step: {step} for user: {whatsapp_message.author_id}")
    except Exception as e:
        global_logger.error(e)
    return {"status": "success"}
    
    