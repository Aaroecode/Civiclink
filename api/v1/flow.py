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

temp = {}


start_body = "Hello!👋 \n Welcome to *Civiclink*, Your road issue reporting assistant.🚧\nHere's how you can use this service:\n 1️⃣ Click on _Report Issue_\n2️⃣ Share Image with us.\n3️⃣ Share your location\n Your reports will contribute to safer and better roads for everyone!"
languages = [{"title": "Select Language", "rows": 
                     [{"id":"en", "title":"English"},
                      {"id":"hi", "title":"Hindi"},
                      {"id":"te", "title":"Telugu"},
                      {"id":"ta", "title":"Tamil"},
                      {"id":"pa", "title":"Punjabi"}]}]

translator = Translator()  #fix rate limit issue later


@chat_flow.step("start")
def start(ctx: WhatsAppMessage):

    users = elastic.get_all_document_ids("users")

    
    issue_button_title = "Report Issue"
    language_button_title = "Change Language"

    if ctx.author_id in users:
        user = elastic.find("users", ctx.author_id)
        body = translator.translate(start_body, dest=user["language"])
        issue_button_title = translator.translate(issue_button_title, dest=user["language"])
        language_button_title = translator.translate(language_button_title, dest=user["language"])

    buttons = [{"id": "report", "title": issue_button_title},{"id": "ch_lang", "title": language_button_title}]
    message = waengine.create_media_button_message(ctx.author_id, image_url="https://vox-cpaas.com/blog/wp-content/uploads/2022/05/whatsapp.jpg", text = body, buttons=buttons)
    waengine.send_message(message)
    return "option_select"

@chat_flow.step("option_select")
def option_select(ctx: WhatsAppMessage):
    users = elastic.get_all_document_ids("users")
    if ctx.author_id not in users:
        body = "Invalid Interaction"
        message = waengine.create_text_message(ctx.author_id, body)
        waengine.send(message)
        return "start"

    if ctx.interaction_type == "button":
        if ctx.interaction_id == "ch_lang":
            message = waengine.create_list_message(ctx.author_id, "Please select your preferred language below.", "Languages", languages)
            waengine.send_message(message)
            return "language_selection"

        user = elastic.find("users", ctx.author_id)
        body = "Click and share image!"
        body = translator.translate(body, user["language"])
        message = waengine.create_text_message(ctx.author_id, body )
        waengine.send_message(message)
        return "get_image"

@chat_flow.step("language_selection")
def language_selection(ctx: WhatsAppMessage):
    if ctx.interaction_type == "list":
        data = {"language": ctx.interaction_id}
        elastic.add("users", data, ctx.author_id)
        issue_button_title = "Report Issue"
        language_button_title = "Change Language"
        body = translator.translate(start_body, dest=ctx.interaction_id)
        issue_button_title = translator.translate(issue_button_title, dest=ctx.interaction_id)
        language_button_title = translator.translate(language_button_title, dest=ctx.interaction_id)
        buttons = [{"id": "report", "title": issue_button_title},{"id": "ch_lang", "title": language_button_title}]
        message = waengine.create_media_button_message(ctx.author_id, image_url="https://vox-cpaas.com/blog/wp-content/uploads/2022/05/whatsapp.jpg", text = body, buttons=buttons)
        waengine.send_message(message)
        return "option_select"


@chat_flow.step("get_image")
def get_image(ctx: WhatsAppMessage):
    user = elastic.find("users", str(ctx.author_id))

    if ctx.media_type == "image":
        body = "Please wait until we process your image"
        body = translator.translate(body, dest=user["language"])
        message = waengine.create_text_message(ctx.author_id, str(body))
        waengine.send_message(message)


        image_url = waengine.get_media_url(ctx.media_id)
        
        temp[ctx.author_id] = {}
        temp[ctx.author_id]["id"] = elastic.generate_uuid()
        
        image_path = waengine.download_image(image_url, temp[ctx.author_id]["id"])
        temp[ctx.author_id]["image_url"] = f"https://whatsapp.datawork.in/images/{temp[ctx.author_id]['id']}.jpg"

        
        detected_issue =  waengine.detect_road_issue(image_path=image_path)

        if detected_issue[0] == 0:
            body = "Unable to detect issue\nPlease describe your issue in less than 50 words"
            body = translator.translate(body, dest=user["language"])
            message = waengine.create_text_message(ctx.author_id, body)
            waengine.send_message(message)
            return "other_issue"

        body = detected_issue[2]
        temp[ctx.author_id]["issue"] = body
        body = translator.translate(body, dest=user["language"], cache=False)
        temp[ctx.author_id]["type"] = detected_issue[1]
        message = waengine.create_text_message(ctx.author_id, body)
        waengine.send_message(message)

        body = "Please share location with us!"
        body = translator.translate(body, user["language"])
        message = waengine.create_text_message(ctx.author_id, body)
        waengine.send_message(message)

        return "get_location"
    
    else:
        body = "Invalid Interaction"
        body = translator.translate(body, dest=user["language"])
        message = waengine.create_text_message(ctx.author_id, str(body))
        waengine.send_message(message)
        return "start"

@chat_flow.step("other_issue")
def other_issue(ctx: WhatsAppMessage):
    user = elastic.find("users", ctx.author_id)

    if ctx.type == "text":
        temp[ctx.author_id]["type"] = "other"
        temp[ctx.author_id]["issue"] = translator.translate(ctx.text_content, "en", cache=False)

        body = "Share your *current location*"
        body = translator.translate(body, user["langugae"])
        message = waengine.create_text_message(ctx.author_id, body)
        waengine.send(message)

        return "get_location"
    else:
        body = "Invalid Interaction"
        body = translator.translate(body, dest=user["language"])
        message = waengine.create_text_message(ctx.author_id, str(body))
        waengine.send(message)
        return "start"



@chat_flow.step("get_location")
def get_location(context: WhatsAppMessage):
    user = elastic.find("users", str(context.author_id))

    if context.location_latitude is not None and context.location_longitude is not None:
        temp[context.author_id]["latitude"] = context.location_latitude
        temp[context.author_id]["longitude"] = context.location_longitude
        temp[context.author_id]["city"] = get_address(context.location_latitude, context.location_longitude).get('city', 'N/A')
        temp[context.author_id]["state"] = get_address(context.location_latitude, context.location_longitude).get('state', 'N/A')
        temp[context.author_id]["user"] = context.author_id
        temp[context.author_id]["timestamp"] = time.time()
        temp[context.author_id]["status"] = "open"
        temp[context.author_id]["assigned_to"] = "None"
        body = f"Your ticket has been recorded\n Your ticket id is: {temp[context.author_id]['id']}"
        body = translator.translate(body, dest=user["language"])
        message = waengine.create_text_message(context.author_id, str(body))
        waengine.send_message(message)
        id = elastic.add("tickets", temp[context.author_id], temp[context.author_id]["id"])
        if "tickets" not in user:
            user["tickets"] = []
        user["tickets"].append(id)
        elastic.add("users", user, context.author_id)
        return "start"
    
    else:
        body = "Invalid Interaction"
        body = translator.translate(body, dest=user["language"])
        message = waengine.create_text_message(context.author_id, str(body))
        return "start"

    


        





    









# @chat_flow.step("start")
# def start(context: WhatsAppMessage):
#     global_logger.info(f"Received message from {context.author_id}")
#     users = elastic.get_all_document_ids("users")

#     if context.author_id not in users:
#         sections = [{"title": "Select Language", "rows": 
#                      [{"id":"en", "title":"English"},
#                       {"id":"hi", "title":"Hindi"},
#                       {"id":"te", "title":"Telugu"},
#                       {"id":"ta", "title":"Tamil"},
#                       {"id":"pa", "title":"Punjabi"}]}]
#         message = waengine.create_list_message(context.author_id, "Please select your preferred language below.", "Languages", sections)
#         waengine.send_message(message)
#         return "language_selection"
    
#     elif context.type == "text":
#         query = {"bool": {"must": [{"term": {"user": str(context.author_id)}},{"range": {"timestamp": {"gt": float(time.time() - RATE_LIMIT_WINDOW)}}}]}}
#         tickets_filed = elastic.search(index = "tickets", query = query)
#         print(tickets_filed["hits"]["total"]["value"])
#         user = elastic.find("users", str(context.author_id))

#         if tickets_filed["hits"]["total"]["value"] >= RATE_LIMIT:
#             body = f"You have exceeded the rate limit. Please wait for a {humanfriendly.format_timespan(RATE_LIMIT_WINDOW)} before sending another message."
#             body = translator.translate(body, dest=user["language"])
#             message = waengine.create_text_message(context.author_id, str(body))
#             waengine.send_message(message)
#             return "start"

        
#         sections = [{"title": "Select Issue", "rows": 
#                     [{"id":"damaged_road", "title": translator.translate("Damaged Road", dest=user["language"])},
#                     {"id":"drainage_problem", "title": translator.translate("Drainage Problem", dest=user["language"])},
#                     {"id":"Pothole", "title": translator.translate("Pothole", dest=user["language"])} ]}]
#         body = "Please Select Your Issue"
#         body = translator.translate(body, dest=user["language"])
#         message = waengine.create_list_message(context.author_id, body, "Issues", sections)
#         waengine.send_message(message)
#         return "select_issue"
    
#     else:
#         user = elastic.find("users", str(context.author_id))
#         body = "Invalid Interaction"
#         body = translator.translate(body, dest=user["language"])
#         message = waengine.create_text_message(context.author_id, str(body))
#         return "start"


# @chat_flow.step("language_selection")
# def language_selection(context: WhatsAppMessage):
#     global_logger.info(f"Received message from {context.author_id}")

#     if context.interaction_type == "list":
#         data = {"language": str(context.interaction_id)}
#         elastic.add("users", data=data, id=context.author_id)
#         sections = [{"title": "Select Issue", "rows": 
#                     [{"id":"damaged_road", "title": str(translator.translate("Damaged Road", dest=context.interaction_id))},
#                     {"id":"drainage_problem", "title": str(translator.translate("Drainage Problem", dest=context.interaction_id))},
#                     {"id":"Pothole", "title": str(translator.translate("Pothole", dest=context.interaction_id))}]}]
#         body = "Please Select Your Issue"
#         body = translator.translate(body, dest=context.interaction_id)
#         message = waengine.create_list_message(context.author_id, body, "Issues", sections)
#         waengine.send_message(message)
#         return "select_issue"
    
#     else:
#         sections = [{"title": "Select Language", "rows": 
#                      [{"id":"en", "title":"English"},
#                       {"id":"hi", "title":"Hindi"},
#                       {"id":"te", "title":"Telugu"},
#                       {"id":"ta", "title":"Tamil"},
#                       {"id":"pa", "title":"Punjabi"}]}]
#         message = waengine.create_list_message(context.author_id, "Invalid Interaction! Please select your preferred language below.", "Languages", sections)
#         waengine.send_message(message)
#         return "language_selection"


# @chat_flow.step("select_issue")
# def select_issue(context: WhatsAppMessage):
#     global_logger.info("Yes")
#     user = elastic.find("users", str(context.author_id))
#     global_logger.info("yes2")

#     if context.interaction_type == "list":
#         temp[context.author_id] = {}
#         temp[context.author_id]["type"] = context.interaction_id
#         body = "Please share an image with us"
#         body = translator.translate(body, dest=user["language"])
#         message = waengine.create_text_message(context.author_id, str(body))
#         waengine.send_message(message)
#         return "get_image"
    
#     else:
#         body = "Invalid Interaction"
#         body = translator.translate(body, dest=user["language"])
#         message = waengine.create_text_message(context.author_id, str(body))
#         return "start"


# @chat_flow.step("get_image")
# def get_image(context: WhatsAppMessage):
#     global_logger.info("1")
#     user = elastic.find("users", str(context.author_id))
#     global_logger.info("2")

#     if context.media_type == "image":
#         global_logger.info("3")

#         body = "Please wait until we process your image"
#         global_logger.info("4")
#         body = translator.translate(body, dest=user["language"])
#         global_logger.info("5")
#         message = waengine.create_text_message(context.author_id, str(body))
#         global_logger.info("6")
#         waengine.send_message(message)
#         global_logger.info("7")
#         image_url = waengine.get_media_url(context.media_id)
#         temp[context.author_id]["id"] = elastic.generate_uuid()
#         image_path = waengine.download_image(image_url, temp[context.author_id]["id"])
#         temp[context.author_id]["image_url"] = f"https://whatsapp.datawork.in/images/{temp[context.author_id]['id']}.jpg"
#         detected_issue =  waengine.detect_road_issue(image_path=image_path)  
#         body = detected_issue[2]
#         temp[context.author_id]["issue"] = body
#         body = translator.translate(body, dest=user["language"], cache=False)
#         message = waengine.create_text_message(context.author_id, str(body))
#         waengine.send_message(message)
#         body = "Please share your location with us"
#         body = translator.translate(body, dest=user["language"])
#         message = waengine.create_text_message(context.author_id, str(body))
#         waengine.send_message(message)
#         return "get_location"
    
#     else:
#         body = "Invalid Interaction"
#         body = translator.translate(body, dest=user["language"])
#         message = waengine.create_text_message(context.author_id, str(body))
#         return "start"


# @chat_flow.step("get_location")
# def get_location(context: WhatsAppMessage):
#     user = elastic.find("users", str(context.author_id))

#     if context.location_latitude is not None and context.location_longitude is not None:
#         temp[context.author_id]["latitude"] = context.location_latitude
#         temp[context.author_id]["longitude"] = context.location_longitude
#         temp[context.author_id]["city"] = get_address(context.location_latitude, context.location_longitude).get('city', 'N/A')
#         temp[context.author_id]["state"] = get_address(context.location_latitude, context.location_longitude).get('state', 'N/A')
#         temp[context.author_id]["user"] = context.author_id
#         temp[context.author_id]["timestamp"] = time.time()
#         temp[context.author_id]["status"] = "open"
#         temp[context.author_id]["assigned_to"] = "None"
#         body = "Your ticket has been recorded"
#         body = translator.translate(body, dest=user["language"])
#         message = waengine.create_text_message(context.author_id, str(body))
#         waengine.send_message(message)
#         id = elastic.add("tickets", temp[context.author_id], temp[context.author_id]["id"])
#         if "tickets" not in user:
#             user["tickets"] = []
#         user["tickets"].append(id)
#         elastic.add("users", user, context.author_id)
#         return "start"
    
#     else:
#         body = "Invalid Interaction"
#         body = translator.translate(body, dest=user["language"])
#         message = waengine.create_text_message(context.author_id, str(body))
#         return "start"
