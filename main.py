from flask import Flask, request, jsonify, Response
from google import genai

from settings import PROJECT_ID, LOCATION, FLASK_PRODUCTION, PORT

app = Flask(__name__)

@app.route("/healthcheck", methods=["GET"])
def healthcheck():
    return Response(status=200)

def load_client():
    return genai.Client(project=PROJECT_ID, location=LOCATION, vertexai=True)

@app.route('/chat/blurb', methods=['POST'])
def generate_text():
    """
    Generates text using the Gemini model based on the provided prompt in the POST request.
    Returns a JSON response containing the generated text.
    """

    try:
        # Grab json inputs
        req_body = request.get_json()
        prompt = req_body.get('prompt') 
        model = req_body.get('model')

        if not prompt:
            return jsonify({"error": "Prompt is required in the request body"}), 400
        if not model:
            model = "gemini-2.0-flash"

        # Call Model
        response = client.models.generate_content(
            model = model,
            contents = prompt
        )

        # Return the generated text in a JSON response
        return response.model_dump_json(indent=2), 200

    except Exception as e:
        print(f"Error during text generation: {e}")
        return jsonify({"error": f"An error occurred: {e}"}), 500


if __name__ == '__main__':
    client = load_client()
    app.run(debug=FLASK_PRODUCTION, port=PORT)
