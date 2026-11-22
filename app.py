from flask import Flask, render_template, request
from PIL import Image
import cv2
import numpy as np
import re

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/scan", methods=["POST"])
def scan():

    file = request.files.get("qr_image")

    if not file or file.filename == "":
        return render_template(
            "index.html",
            result="Please upload a QR code image."
        )

    try:
        # Read uploaded QR image
        image = Image.open(file).convert("RGB")
        image_array = np.array(image)

        # Detect and decode QR code
        detector = cv2.QRCodeDetector()
        url, points, straight_qr = detector.detectAndDecode(
            image_array
        )

        if not url:
            return render_template(
                "index.html",
                result="No QR code found in this image."
            )

        # Suspicious URL keywords
        suspicious_words = [
            "login",
            "verify",
            "password",
            "bank",
            "gift",
            "urgent",
            "free-prize",
            "claim"
        ]

        found = [
            word for word in suspicious_words
            if word in url.lower()
        ]

        # Analyze extracted link
        if not re.match(r"^https?://", url, re.I):

            result = "WARNING: Suspicious or unsupported link format."

        elif found:

            result = (
                "WARNING: Suspicious keywords detected: "
                + ", ".join(found)
            )

        else:

            result = (
                "No suspicious keyword patterns detected. "
                "This does not guarantee that the link is safe."
            )

        return render_template(
            "index.html",
            result=result,
            url=url
        )

    except Exception as error:

        print("Error:", error)

        return render_template(
            "index.html",
            result="Unable to read this QR image."
        )


if __name__ == "__main__":
    app.run(debug=True)