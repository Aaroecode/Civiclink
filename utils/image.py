import base64
from openai import OpenAI
client = OpenAI()

# Function to encode the imageimport openai
import base64
from PIL import Image
import io

# # Set of known road infrastructure issues
# issues = {"pothole", "missing manhole cover", "broken railing", "cracks in road", "faded road markings"}

def rescale_and_encode_image(image_data, max_resolution=(800, 800)):
    """
    Rescales the image to the specified maximum resolution if it exceeds the size, 
    and then encodes it into base64 format.

    Parameters:
        image_data (bytes): The raw image data.
        max_resolution (tuple): The maximum width and height for the image.

    Returns:
        str: The base64 encoded string of the rescaled image.
    """
    try:
        image = Image.open(io.BytesIO(image_data))

        # Print the format of the image
        print(f"Image format: {image.format}")

        # Check if resizing is needed
        if image.size[0] > max_resolution[0] or image.size[1] > max_resolution[1]:
            image.thumbnail(max_resolution)

        # Convert back to base64
        buffer = io.BytesIO()
        image.save(buffer, format="JPEG")
        rescaled_image = base64.b64encode(buffer.getvalue()).decode('utf-8')
        return rescaled_image

    except Exception as e:
        raise ValueError(f"Failed to rescale and encode image: {str(e)}")

# # Path to your image
# image_path = "images.jpeg"
# issues = {'manhole', 'potholes', 'object on the road','broken railing' }
# # Getting the base64 string
# with open(image_path, "rb") as image_file:
#     image_data = image_file.read()
# rescaled_encoded_img = rescale_and_encode_image(image_data)

# response = client.chat.completions.create(
#   model="gpt-4o",
#   messages=[
#     {
#       "role": "system", 
#       "content": """You are an AI that detects and identifies road infrastructure issues. 
#                   If issue is not related to road infrastructure, 
#                   respond with 'No issue detected in the image related to road infrastructure.' 
#                   then give the summary of the issue in one sentence starting with 'However'.
#                   """
#     },
    
#     {
      
#       "role": "user",
#       "content": [
#         {
#           "type": "text",
#           "text": "Detect issue in the image and summarize it in one sentence.",
#         },
#         {
#           "type": "image_url",
#           "image_url": {
#             "url":  f"data:image/jpeg;base64,{rescaled_encoded_img}"
#           },
#         },
#       ],
#     }
#   ],
# )

# try:
#     ai_response = response.choices[0].message.content.strip()

#     if "No issue detected in the image related to road infrastructure." in ai_response:
#         status_code = 0
#         category = "None"
#         description = ai_response.split("However", 1)[1].strip() if "However" in ai_response else "No further details provided."
#     else:
#         # Extract the description and categorize
#         description = ai_response
#         category = next((issue for issue in issues if issue in description.lower()), "Other")
#         status_code = 1

#     final_response = (status_code, category, description)
#     print(final_response)
# except Exception as e:
#     print( (0, "Error", f"An error occurred: {str(e)}"))