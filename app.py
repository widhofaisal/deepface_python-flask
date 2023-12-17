from flask import Flask, request, jsonify, render_template
from deepface import DeepFace
from werkzeug.utils import secure_filename

import json
import os

app = Flask(__name__)


@app.route("/", methods=['POST'])
def compare_images():
    try:
        app.logger.info("Try to compare two images")
        # BINDING : uding form data type file
        image1 = request.files["image1"]
        image2 = request.files["image2"]

        # VALIDATE : file image format
        allowed_extensions = {'png', 'jpg', 'jpeg', 'raw', 'tiff', 'heic'}
        if not (image1.filename.split('.')[-1].lower() in allowed_extensions and
                image2.filename.split('.')[-1].lower() in allowed_extensions):
            raise ValueError("Invalid file format")

        # LOCAL WRITE : save image file to /temp directory
        temp_dir = "temp"
        os.makedirs(temp_dir, exist_ok=True)
        # image1
        image1_filename = secure_filename(image1.filename)
        image1_path = os.path.join(temp_dir, image1_filename)
        image1.save(image1_path)
        # image2
        image2_filename = secure_filename(image2.filename)
        image2_path = os.path.join(temp_dir, image2_filename)
        image2.save(image2_path)

        # AI : Compare the two images using DeepFace
        result = DeepFace.verify(image1_path, image2_path)

        # LOCAL DELETE : image from /temp directory
        if os.path.exists(image1_path) and os.path.exists(image2_path):
            os.remove(image1_path)
            os.remove(image2_path)
        else:
            raise ValueError("Path does not exists")

        # RESPONSE SUCCESS
        result = {
            "name": "compare images",
            "message": "success to compare two images",
            "code": 200,
            "data": {
                "match": int(result["verified"]),
            }
        }
        return json.dumps(result, sort_keys=False)

    except Exception as e:
        # RESPONSE ERROR
        error_result = {
            "name": "Error",
            "message": str(e),
            "code": 500,
            "data": None
        }
        return json.dumps(error_result, sort_keys=True)


if __name__ == "__main__":
    app.run(debug=True)
