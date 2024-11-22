from pydantic import BaseModel



class WebhookPayload(BaseModel):
    object: str
    entry: list  