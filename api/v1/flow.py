from services.chatflow import chat_flow
from utils.wautils import WaEngine, WhatsAppMessage
from utils.logging import outbound_payload_logger, inbound_payload_logger, global_logger, elastic_logger
from googletrans import Translator
from database.elasticsearch import Elastic
from utils.geo import get_address
from dotenv import load_dotenv
import time, os

load_dotenv()

elastic = Elastic("https://85.202.160.193:9200", "elastic", os.getenv("ELASTIC_PASSWORD"))


waengine = WaEngine(os.getenv("WA_TOKEN"), "260478600487118")
translator = Translator()


temp = {}

# @chat_flow.step("start")
# def start(context: WhatsAppMessage):
#     global_logger.info(f"Received message from {context.author_id}")
#     users = elastic.get_all_document_ids("users")

#     if context.author_id not in users:
#         sections = [{"title": "Select Language", "rows": 
#                      [{"id":"en", "title":"English"},
#                       {"id":"hi", "title":"Hindi"},
#                       {"id":"te", "title":"Telgu"},
#                       {"id":"ta", "title":"Tamil"},
#                       {"id":"pa", "title":"Punjabi"}]}]
#         message = waengine.create_list_message(context.author_id,"Please select your prefered language below.", "Languages", sections)
#         waengine.send_message(message)
#         return "language_selection"
    
#     elif context.type == "text":
#         user = elastic.find("users", str(context.author_id))
#         sections = [{"title": "Select Issue", "rows": 
#                     [{"id":"damaged_road", "title": translator.translate("Damaged Road", user["language"]).text},
#                     {"id":"drainage_problem", "title":translator.translate("Drainage Problem", user["language"]).text},
#                     {"id":"Pothole", "title":translator.translate("Pothole", user["language"]).text} ]}]
#         body = "Please Select You Issue"
#         body = translator.translate(body, user["language"]).text
#         message = waengine.create_list_message(context.author_id, body, "Issues", sections)
#         waengine.send_message(message)
#         return "select_issue"
    

#     else:
#         user = elastic.find("users", str(context.author_id))
#         body = "Invalid Interaction"
#         body = translator.translate(body, user["language"]).text
#         message = waengine.create_text_message(context.author_id, str(body))
#         return "start"


# @chat_flow.step("language_selection")
# def language_selection(context: WhatsAppMessage):
#     global_logger.info(f"Received message from {context.author_id}")
#     users = elastic.get_all_document_ids("users")

#     if context.author_id in users and context.interaction_type == "list":
#         data = {"language": str(context.interaction_id)}
#         elastic.add("users", data=data, id = context.author_id)
#         sections = [{"title": "Select Issue", "rows": 
#                     [{"id":"damaged_road", "title": str(translator.translate("Damaged Road", str(context.interaction_id)))},
#                     {"id":"drainage_problem", "title":str(translator.translate("Drainage Problem", str(context.interaction_id)))},
#                     {"id":"Pothole", "title":str(translator.translate("Pothole", str(context.interaction_id)))}]}]
#         body = "Please Select You Issue"
#         body = translator.translate(body, users[context.author_id]["language"]).text
#         message = waengine.create_list_message(context.author_id, body, "Issues", sections)
#         waengine.send_message(message)
#         return "select_issue"
    
#     else:
#         sections = [{"title": "Select Language", "rows": 
#                      [{"id":"en", "title":"English"},
#                       {"id":"hi", "title":"Hindi"},
#                       {"id":"te", "title":"Telgu"},
#                       {"id":"ta", "title":"Tamil"},
#                       {"id":"pa", "title":"Punjabi"} ]}]
#         message = waengine.create_list_message(context.author_id,"Invalid Interaction! Please select your prefered language below.", "Languages", sections)
#         waengine.send_message(message)
#         return "language_selection"


# @chat_flow.step("select_issue")
# def select_issue(context: WhatsAppMessage):
#     user = elastic.find("users", str(context.author_id))

#     if context.interaction_type == "list":
#         temp[context.author_id] = {}
#         temp[context.author_id]["type"] = context.interaction_id
#         body = "Please share image with us"
#         body = translator.translate(body, user["language"]).text
#         message = waengine.create_text_message(context.author_id, str(body))
#         waengine.send_message(message)
#         return "get_image"
    
#     else:
#         body = "Invalid Interaction"
#         body = translator.translate(body, user["language"]).text
#         message = waengine.create_text_message(context.author_id, str(body))
#         return "start"



# @chat_flow.step("get_image")
# def get_image(context: WhatsAppMessage):
#     user = elastic.find("users", str(context.author_id))

#     if context.media_type == "image":
#         image_url = waengine.get_media_url(context.media_id)
#         temp[context.author_id]["image_url"] =  image_url
#         image_path = waengine.download_image(image_url)
#         detected_isuue = requests.post("http://127.0.0.1:8321/", json={"image_path": image_path})
#         body = detected_isuue.json()
#         body = translator.translate(body.get("detected_issues"), user["language"]).text
#         message = waengine.create_text_message(context.author_id, str(body))
#         waengine.send_message(message)
#         body = "Please share location with us"
#         body = translator.translate(body, user["language"]).text
#         message = waengine.create_text_message(context.author_id, str(body))
#         waengine.send_message(message)
#         return "get_location"
    

#     else:
#         body = "Invalid Interaction"
#         body = translator.translate(body, user["language"]).text
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
#         body = "Your ticket has been recorded"
#         body = translator.translate(body, user["language"]).text
#         message = waengine.create_text_message(context.author_id, str(body))
#         waengine.send_message(message)
#         id = elastic.add("tickets", temp[context.author_id])
#         if "tickets" not in user:
#             user["tickets"] = []
#         user["tickets"].append(id)
#         print(user)
#         elastic.add("users", user, context.author_id)
#         return "start"
    
#     else:
#         body = "Invalid Interaction"
#         body = translator.translate(body, user["language"]).text
#         message = waengine.create_text_message(context.author_id, str(body))
#         return "start"

#----------------------------------------------------------------------------------------------------------------



# Initialize the Translator
translator = Translator()

@chat_flow.step("start")
def start(context: WhatsAppMessage):
    global_logger.info(f"Received message from {context.author_id}")
    users = elastic.get_all_document_ids("users")

    if context.author_id not in users:
        sections = [{"title": "Select Language", "rows": 
                     [{"id":"en", "title":"English"},
                      {"id":"hi", "title":"Hindi"},
                      {"id":"te", "title":"Telugu"},
                      {"id":"ta", "title":"Tamil"},
                      {"id":"pa", "title":"Punjabi"}]}]
        message = waengine.create_list_message(context.author_id, "Please select your preferred language below.", "Languages", sections)
        waengine.send_message(message)
        return "language_selection"
    
    elif context.type == "text":
        user = elastic.find("users", str(context.author_id))
        sections = [{"title": "Select Issue", "rows": 
                    [{"id":"damaged_road", "title": translator.translate("Damaged Road", dest=user["language"]).text},
                    {"id":"drainage_problem", "title": translator.translate("Drainage Problem", dest=user["language"]).text},
                    {"id":"Pothole", "title": translator.translate("Pothole", dest=user["language"]).text} ]}]
        body = "Please Select Your Issue"
        body = translator.translate(body, dest=user["language"]).text
        message = waengine.create_list_message(context.author_id, body, "Issues", sections)
        waengine.send_message(message)
        return "select_issue"
    
    else:
        user = elastic.find("users", str(context.author_id))
        body = "Invalid Interaction"
        body = translator.translate(body, dest=user["language"]).text
        message = waengine.create_text_message(context.author_id, str(body))
        return "start"


@chat_flow.step("language_selection")
def language_selection(context: WhatsAppMessage):
    global_logger.info(f"Received message from {context.author_id}")

    if context.interaction_type == "list":
        data = {"language": str(context.interaction_id)}
        elastic.add("users", data=data, id=context.author_id)
        sections = [{"title": "Select Issue", "rows": 
                    [{"id":"damaged_road", "title": str(translator.translate("Damaged Road", dest=context.interaction_id).text)},
                    {"id":"drainage_problem", "title": str(translator.translate("Drainage Problem", dest=context.interaction_id).text)},
                    {"id":"Pothole", "title": str(translator.translate("Pothole", dest=context.interaction_id).text)}]}]
        body = "Please Select Your Issue"
        body = translator.translate(body, dest=context.interaction_id).text
        message = waengine.create_list_message(context.author_id, body, "Issues", sections)
        waengine.send_message(message)
        return "select_issue"
    
    else:
        sections = [{"title": "Select Language", "rows": 
                     [{"id":"en", "title":"English"},
                      {"id":"hi", "title":"Hindi"},
                      {"id":"te", "title":"Telugu"},
                      {"id":"ta", "title":"Tamil"},
                      {"id":"pa", "title":"Punjabi"}]}]
        message = waengine.create_list_message(context.author_id, "Invalid Interaction! Please select your preferred language below.", "Languages", sections)
        waengine.send_message(message)
        return "language_selection"


@chat_flow.step("select_issue")
def select_issue(context: WhatsAppMessage):
    user = elastic.find("users", str(context.author_id))

    if context.interaction_type == "list":
        temp[context.author_id] = {}
        temp[context.author_id]["type"] = context.interaction_id
        body = "Please share an image with us"
        body = translator.translate(body, dest=user["language"]).text
        message = waengine.create_text_message(context.author_id, str(body))
        waengine.send_message(message)
        return "get_image"
    
    else:
        body = "Invalid Interaction"
        body = translator.translate(body, dest=user["language"]).text
        message = waengine.create_text_message(context.author_id, str(body))
        return "start"


@chat_flow.step("get_image")
def get_image(context: WhatsAppMessage):
    user = elastic.find("users", str(context.author_id))

    if context.media_type == "image":

        body = "Please wait until we process your image"
        body = translator.translate(body, dest=user["language"]).text
        message = waengine.create_text_message(context.author_id, str(body))
        waengine.send_message(message)
        image_url = waengine.get_media_url(context.media_id)
        temp[context.author_id]["image_url"] = image_url
        image_path = waengine.download_image(image_url)
        detected_issue =  waengine.detect_road_issue(image_path=image_path)  
        body = detected_issue
        body = translator.translate(body, dest=user["language"]).text
        message = waengine.create_text_message(context.author_id, str(body))
        waengine.send_message(message)
        body = "Please share your location with us"
        body = translator.translate(body, dest=user["language"]).text
        message = waengine.create_text_message(context.author_id, str(body))
        waengine.send_message(message)
        return "get_location"
    
    else:
        body = "Invalid Interaction"
        body = translator.translate(body, dest=user["language"]).text
        message = waengine.create_text_message(context.author_id, str(body))
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
        body = "Your ticket has been recorded"
        body = translator.translate(body, dest=user["language"]).text
        message = waengine.create_text_message(context.author_id, str(body))
        waengine.send_message(message)
        id = elastic.add("tickets", temp[context.author_id])
        if "tickets" not in user:
            user["tickets"] = []
        user["tickets"].append(id)
        elastic.add("users", user, context.author_id)
        return "start"
    
    else:
        body = "Invalid Interaction"
        body = translator.translate(body, dest=user["language"]).text
        message = waengine.create_text_message(context.author_id, str(body))
        return "start"
