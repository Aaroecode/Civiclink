from services.chatflow import chat_flow
from utils.wautils import WaEngine, WhatsAppMessage
from utils.logging import outbound_payload_logger, inbound_payload_logger, global_logger, elastic_logger
from utils.translator import Translator
from database.elasticsearch import Elastic
from utils.geo import get_address
from dotenv import load_dotenv
import time, os, humanfriendly

load_dotenv()

elastic = Elastic("https://127.0.0.1:9200", "elastic", os.getenv("ELASTIC_PASSWORD"))

waengine = WaEngine(os.getenv("WA_TOKEN"), "260478600487118")
translator = Translator()
RATE_LIMIT = 5
RATE_LIMIT_WINDOW = 86400

# In-memory store for tracking the state of an active ticket creation flow for a user
ticket_session_data = {}


start_body = "Hello!👋 \n Welcome to *Civiclink*, Your road issue reporting assistant.🚧\nHere's how you can use this service:\n 1️⃣ Click on _Report Issue_\n2️⃣ Share Image with us.\n3️⃣ Share your location\n Your reports will contribute to safer and better roads for everyone!"
languages = [{"title": "Select Language", "rows": 
                     [{"id":"en", "title":"English"},
                      {"id":"hi", "title":"Hindi"},
                      {"id":"te", "title":"Telugu"},
                      {"id":"ta", "title":"Tamil"},
                      {"id":"pa", "title":"Punjabi"}]}]

translator = Translator()  #fix rate limit issue later


@chat_flow.step("start")
def start(message_ctx: WhatsAppMessage):
    """Initial step that greets the user and provides the main menu options."""
    existing_user_ids = elastic.get_all_document_ids("users")

    
    issue_button_title = "Report Issue"
    language_button_title = "Change Language"

    if message_ctx.author_id in existing_user_ids:
        user = elastic.find("users", message_ctx.author_id)
        body = translator.translate(start_body, dest=user["language"])
        issue_button_title = translator.translate(issue_button_title, dest=user["language"])
        language_button_title = translator.translate(language_button_title, dest=user["language"])

    buttons = [{"id": "report", "title": issue_button_title},{"id": "ch_lang", "title": language_button_title}]
    message = waengine.create_media_button_message(message_ctx.author_id, image_url="https://vox-cpaas.com/blog/wp-content/uploads/2022/05/whatsapp.jpg", text = body, buttons=buttons)
    waengine.send_message(message)
    return "option_select"

@chat_flow.step("option_select")
def option_select(message_ctx: WhatsAppMessage):
    """Handles the user's menu selection: either reporting an issue or changing language."""
    existing_user_ids = elastic.get_all_document_ids("users")
    if message_ctx.author_id not in existing_user_ids:
        body = "Invalid Interaction"
        message = waengine.create_text_message(message_ctx.author_id, body)
        waengine.send(message)
        return "start"

    if message_ctx.interaction_type == "button":
        if message_ctx.interaction_id == "ch_lang":
            message = waengine.create_list_message(message_ctx.author_id, "Please select your preferred language below.", "Languages", languages)
            waengine.send_message(message)
            return "language_selection"

        user = elastic.find("users", message_ctx.author_id)
        body = "Click and share image!"
        body = translator.translate(body, user["language"])
        message = waengine.create_text_message(message_ctx.author_id, body )
        waengine.send_message(message)
        return "get_image"

@chat_flow.step("language_selection")
def language_selection(message_ctx: WhatsAppMessage):
    """Updates user's preferred language and redirects to the main menu."""
    if message_ctx.interaction_type == "list":
        data = {"language": message_ctx.interaction_id}
        elastic.add("users", data, message_ctx.author_id)
        issue_button_title = "Report Issue"
        language_button_title = "Change Language"
        body = translator.translate(start_body, dest=message_ctx.interaction_id)
        issue_button_title = translator.translate(issue_button_title, dest=message_ctx.interaction_id)
        language_button_title = translator.translate(language_button_title, dest=message_ctx.interaction_id)
        buttons = [{"id": "report", "title": issue_button_title},{"id": "ch_lang", "title": language_button_title}]
        message = waengine.create_media_button_message(message_ctx.author_id, image_url="https://vox-cpaas.com/blog/wp-content/uploads/2022/05/whatsapp.jpg", text = body, buttons=buttons)
        waengine.send_message(message)
        return "option_select"


@chat_flow.step("get_image")
def get_image(message_ctx: WhatsAppMessage):
    """Processes an incoming image, detects issues using AI, and asks for location."""
    user = elastic.find("users", str(message_ctx.author_id))

    if message_ctx.media_type == "image":
        body = "Please wait until we process your image"
        body = translator.translate(body, dest=user["language"])
        message = waengine.create_text_message(message_ctx.author_id, str(body))
        waengine.send_message(message)


        image_url = waengine.get_media_url(message_ctx.media_id)
        
        ticket_session_data[message_ctx.author_id] = {}
        ticket_session_data[message_ctx.author_id]["id"] = elastic.generate_uuid()
        
        image_path = waengine.download_image(image_url, ticket_session_data[message_ctx.author_id]["id"])
        ticket_session_data[message_ctx.author_id]["image_url"] = f"https://whatsapp.datawork.in/images/{ticket_session_data[message_ctx.author_id]['id']}.jpg"

        
        detected_issue =  waengine.detect_road_issue(image_path=image_path)

        if detected_issue[0] == 0:
            body = "Unable to detect issue\nPlease describe your issue in less than 50 words"
            body = translator.translate(body, dest=user["language"])
            message = waengine.create_text_message(message_ctx.author_id, body)
            waengine.send_message(message)
            return "other_issue"

        body = detected_issue[2]
        ticket_session_data[message_ctx.author_id]["issue"] = body
        body = translator.translate(body, dest=user["language"], cache=False)
        ticket_session_data[message_ctx.author_id]["type"] = detected_issue[1]
        message = waengine.create_text_message(message_ctx.author_id, body)
        waengine.send_message(message)

        body = "Please share location with us!"
        body = translator.translate(body, user["language"])
        message = waengine.create_text_message(message_ctx.author_id, body)
        waengine.send_message(message)

        return "get_location"
    
    else:
        body = "Invalid Interaction"
        body = translator.translate(body, dest=user["language"])
        message = waengine.create_text_message(message_ctx.author_id, str(body))
        waengine.send_message(message)
        return "start"

@chat_flow.step("other_issue")
def other_issue(message_ctx: WhatsAppMessage):
    """Fallback step if AI fails to detect the issue automatically."""
    user = elastic.find("users", message_ctx.author_id)

    if message_ctx.type == "text":
        ticket_session_data[message_ctx.author_id]["type"] = "other"
        ticket_session_data[message_ctx.author_id]["issue"] = translator.translate(message_ctx.text_content, "en", cache=False)

        body = "Share your *current location*"
        body = translator.translate(body, user["langugae"])
        message = waengine.create_text_message(message_ctx.author_id, body)
        waengine.send(message)

        return "get_location"
    else:
        body = "Invalid Interaction"
        body = translator.translate(body, dest=user["language"])
        message = waengine.create_text_message(message_ctx.author_id, str(body))
        waengine.send(message)
        return "start"

@chat_flow.step("get_location")
def get_location(message_ctx: WhatsAppMessage):
    """Saves the location data, creates the ticket in Elasticsearch, and ends the flow."""
    user = elastic.find("users", str(message_ctx.author_id))

    if message_ctx.location_latitude is not None and message_ctx.location_longitude is not None:
        ticket_session_data[message_ctx.author_id]["latitude"] = message_ctx.location_latitude
        ticket_session_data[message_ctx.author_id]["longitude"] = message_ctx.location_longitude
        ticket_session_data[message_ctx.author_id]["city"] = get_address(message_ctx.location_latitude, message_ctx.location_longitude).get('city', 'N/A')
        ticket_session_data[message_ctx.author_id]["state"] = get_address(message_ctx.location_latitude, message_ctx.location_longitude).get('state', 'N/A')
        ticket_session_data[message_ctx.author_id]["user"] = message_ctx.author_id
        ticket_session_data[message_ctx.author_id]["timestamp"] = time.time()
        ticket_session_data[message_ctx.author_id]["status"] = "open"
        ticket_session_data[message_ctx.author_id]["assigned_to"] = "None"
        
        body = f"Your ticket has been recorded\n Your ticket id is: {ticket_session_data[message_ctx.author_id]['id']}"
        body = translator.translate(body, dest=user["language"])
        message = waengine.create_text_message(message_ctx.author_id, str(body))
        waengine.send_message(message)
        
        # Save ticket
        id = elastic.add("tickets", ticket_session_data[message_ctx.author_id], ticket_session_data[message_ctx.author_id]["id"])
        if "tickets" not in user:
            user["tickets"] = []
        user["tickets"].append(id)
        elastic.add("users", user, message_ctx.author_id)
        return "start"
    
    else:
        body = "Invalid Interaction"
        body = translator.translate(body, dest=user["language"])
        message = waengine.create_text_message(message_ctx.author_id, str(body))
        waengine.send_message(message)
        return "start"
