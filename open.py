import openai, base64
client = openai.OpenAI(api_key="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")



app = Flask(__name__)

@app.route("/", methods=["POST"])
def detect_road_issue():
    """
    Detect road infrastructure issues in an image using OpenAI API.

     Args:
        image_path (str): Path to the image file.
        model (str): OpenAI model to use.
        prompt (str): Prompt to provide to the model.

     Returns:
        str: AI-generated response summarizing the detected issue.
    """
    data = request.json
    print(data)  # Debugging: print the request data to see its structure

    # Extract image path and other necessary data
    image_path = data.get("image_path")
    model="gpt-4o"
    prompt="Detect issue in the image and summarize it in one sentence."
    # Function to encode the image to base64
    def encode_image(image_path):
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")

     # Get base64 string of the image
    base64_image = encode_image(image_path)

     # Send the API request
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are an AI that detects and identifies road infrastructure issues."},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}},
                ],
            },
        ],
    )

     # Return the response content
    return jsonify({"detected_issues": response.choices[0].message.content})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8321, debug=True)