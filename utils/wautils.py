
from typing import Dict, List
import requests
import os, base64
from utils.logging import outbound_payload_logger
from fastapi import FastAPI, HTTPException # type: ignore
import openai, base64, os
from dotenv import load_dotenv
from utils.image import rescale_and_encode_image

env_path = os.path.join(os.getcwd(), ".env")
load_dotenv(env_path)
print(os.getenv("OPENAI_API_KEY"))

client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = FastAPI()



class WhatsAppMessage:
    def __init__(self, payload):
        # Initialize attributes with default values
        self.id = None
        self.author_id = None
        self.type = None
        self.text_content = None
        self.media_id = None
        self.media_type = None
        self.media_caption = None
        self.location_latitude = None
        self.location_longitude = None
        self.location_name = None
        self.interaction_type = None
        self.interaction_id = None
        self.interaction_title = None

        # Extract important information from the payload
        entry = payload.get("entry", [])
        for entry_item in entry:
            changes = entry_item.get("changes", [])
            for change in changes:
                value = change.get("value", {})
                messages = value.get("messages", [])
                for message in messages:
                    self.id = message.get("id")
                    self.author_id = message.get("from")
                    self.type = message.get("type")

                    # Extract text content
                    if self.type == "text":
                        self.text_content = message.get("text", {}).get("body")

                    # Extract media content (image, video, etc.)
                    elif self.type in ["image", "video", "audio", "document"]:
                        media = message.get(self.type, {})
                        self.media_id = media.get("id")
                        self.media_type = self.type
                        self.media_caption = media.get("caption")
                    

                    # Extract location content
                    elif self.type == "location":
                        location = message.get("location", {})
                        self.location_latitude = location.get("latitude")
                        self.location_longitude = location.get("longitude")
                        self.location_name = location.get("name")

                    # Extract button or list interactions
                    elif self.type == "interactive":
                        interactive = message.get("interactive", {})
                        if "button_reply" in interactive:
                            self.interaction_type = "button"
                            self.interaction_id = interactive["button_reply"].get("id")
                            self.interaction_title = interactive["button_reply"].get("title")
                        elif "list_reply" in interactive:
                            self.interaction_type = "list"
                            self.interaction_id = interactive["list_reply"].get("id")
                            self.interaction_title = interactive["list_reply"].get("title")

    def __repr__(self):
        return f"<WhatsAppMessage author_id={self.author_id} type={self.type}>"


class WaEngine:
    def __init__(self, access_token: str, phone_number_id: str, log_file: str = "message_log.json"):
        self.access_token = access_token
        self.phone_number_id = phone_number_id
        self.log_file = log_file
        self.api_url = f"https://graph.facebook.com/v15.0/{self.phone_number_id}/messages"
        self.headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }

    def send_message(self, message_data: Dict) -> Dict:
    
        response = requests.post(self.api_url, headers=self.headers, json=message_data)
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.json())
        
        # Log the message
        outbound_payload_logger.info(message_data)
        return response.text


    def create_text_message(self, recipient: str, text: str) -> Dict:
        return {
            "messaging_product": "whatsapp",
            "to": recipient,
            "type": "text",
            "text": {"body": text}
        }

    def create_media_message(self, recipient: str, media_id: str, media_type: str = "image") -> Dict:
        return {
            "messaging_product": "whatsapp",
            "to": recipient,
            "type": media_type,
            media_type: {"id": media_id}
        }

    def create_button_message(self, recipient: str, text: str, buttons: list) -> Dict:
        return {
            "messaging_product": "whatsapp",
            "to": recipient,
            "type": "interactive",
            "interactive": {
                "type": "button",
                "body": {"text": text},
                "action": {
                    "buttons": [{"type": "reply", "reply": {"id": btn['id'], "title": btn['title']}} for btn in buttons]
                }
            }
        }
    
    def create_media_button_message(self, recipient: str, image_url: str, text: str, buttons: List[Dict]) -> Dict:

        return {
            "messaging_product": "whatsapp",
            "to": recipient,
            "type": "interactive",
            "interactive": {
                "type": "button",
                "header": {
                    "type": "image",
                    "image": {"link": image_url}
                },
                "body": {"text": text},
                "action": {
                    "buttons": [{"type": "reply", "reply": {"id": btn['id'], "title": btn['title']}} for btn in buttons]
                }
            }
        }

    def create_link_message(self, recipient: str, text: str, links: list) -> Dict:
        return {
            "messaging_product": "whatsapp",
            "to": recipient,
            "type": "interactive",
            "interactive": {
                "type": "list",
                "header": {"type": "text", "text": "Choose an option"},
                "body": {"text": text},
                "footer": {"text": "Links"},
                "action": {
                    "sections": [{"title": "Links", "rows": [{"id": link['id'], "title": link['title'], "description": link['url']} for link in links]}]
                }
            }
        }

    def create_location_request(self, recipient: str, body: str) -> Dict:
        return {
            "messaging_product": "whatsapp",
            "to": recipient,
            "type": "interactive",
            "interactive": {
                "type": "location",
                "body": {"text": body}
            }
        }
    def create_list_message(
        self,
        recipient: str, 
        body_text: str, 
        button_text: str, 
        sections: list[Dict]
    ) -> Dict:
        return {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": recipient,
            "type": "interactive",
            "interactive": {
                "type": "list",
                "body": {
                    "text": body_text
                },
                "action": {
                    "button": button_text,
                    "sections": sections
                }
            }
        }

    def get_media_url(self, media_id):
        """
        Fetches the media URL using the WhatsApp API.
        """
        url = f"https://graph.facebook.com/v16.0/{media_id}"
        headers = {
            "Authorization": f"Bearer {self.access_token}"
        }
        response = requests.get(url, headers=headers)
        print(f"Response Status Code: {response.status_code}")
        print(f"Response Text: {response.text}")  # Log the raw response for debugging

        if response.status_code == 200:
            print("Passed Media URL")
            return response.json().get("url")
        else:
            print("Failed Media URL")
            raise Exception(f"Failed to fetch media URL: {response.text}")



    def download_image(self, image_url, file_name) -> os.PathLike:
        """
        Downloads an image from the provided URL and saves it locally.
        """
        try:
            headers = {
                "Authorization": f"Bearer {self.access_token}"
            }

            # Make the GET request to download the image
            response = requests.get(image_url, headers=headers, stream=True)
            print(f"Download Response Status Code: {response.status_code}")
            print(f"Download Response Headers: {response.headers}")

            # Check for successful response
            if response.status_code == 200:
                print("Passed Media Download")
                file_path = os.path.join(os.getcwd(), "images", file_name+".jpg")
                print(f"File Path: {file_path}")
                with open(file_path, "wb") as file:
                    for chunk in response.iter_content(1024):
                        file.write(chunk)
                print(f"Image downloaded successfully: {file_path}")
                return file_path
            else:
                # Log the error details
                print("Failed Media Download 1")
                raise Exception(f"Failed to download image: {response.text}")

        except Exception as e:
            print("Failed Media Download 2")
            print(f"Error in downloading image: {str(e)}")
            raise
    
    def detect_road_issue(self, image_path, model="gpt-4o", prompt="Detect issue in the image and summarize it in one sentence."):
        """
        Detect road infrastructure issues in an image using OpenAI API.

        Args:
            image_path (str): Path to the image file.
            model (str): OpenAI model to use.
            prompt (str): Prompt to provide to the model.

        Returns:
            str: AI-generated response summarizing the detected issue.
        """
        # Function to encode the image to base64
        def encode_image(image_path):
            
            with open(image_path, "rb") as image_file:
                img =  image_file.read()

            return rescale_and_encode_image(img)

        # Get base64 string of the image
        try:
            base64_image = encode_image(image_path)
        except Exception as e:
            print(f"Error in encoding image: {str(e)}") 

        # Send the API request
        response = client.chat.completions.create(
          model=model,
          messages=[
            {
              "role": "system", 
              "content": """You are an AI that detects and identifies road infrastructure issues. 
                          If issue is not related to road infrastructure, 
                          respond with 'No issue detected in the image related to road infrastructure.' 
                          then give the summary of the issue in one sentence starting with 'However'.
                          """
            },{
              "role": "user",
              "content": [
                {
                  "type": "text",
                  "text": "Detect issue in the image and summarize it in one sentence.",
                },
                {
                  "type": "image_url",
                  "image_url": {
                    "url":  f"data:image/jpeg;base64,{base64_image}"
                  },},],}],)
        issues = {'manhole', 'potholes', 'object on the road','broken railing' }
        try:
            ai_response = response.choices[0].message.content.strip()

            if "No issue detected in the image related to road infrastructure." in ai_response:
                status_code = 0
                category = "None"
                description = ai_response.split("However", 1)[1].strip() if "However" in ai_response else "No further details provided."
            else:
                # Extract the description and categorize
                description = ai_response
                matches = [issue for issue in issues if issue in description.lower()]
                category = " ".join(matches) if matches else "Other"
                status_code = 1

            final_response = (status_code, category, description)
            return final_response
        except Exception as e:
            print( (0, "Error", f"An error occurred: {str(e)}"))

        return response.choices[0].message.content



