import os
import re
import cv2
import numpy as np
from PIL import Image
from flask import Flask, render_template, request

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "templates"),
    static_folder=os.path.join(BASE_DIR, "static")
)

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
        image = Image.open(file).convert("RGB")
        image_array = np.array(image)

        detector = cv2.QRCodeDetector()
        url, points, straight_qr = detector.detectAndDecode(image_array)

        if not url:
            return render_template(
                "index.html",
                result="No QR code found in this image."
            )

        suspicious_words = [
            "login", "verify", "password", "bank",
            "gift", "urgent", "free-prize", "claim"
        ]

        found = [
            word for word in suspicious_words
            if word in url.lower()
        ]

        if not re.match(r"^https?://", url, re.I):
            result = "WARNING: Suspicious or unsupported link format."
        elif found:
            result = "WARNING: Suspicious keywords detected: " + ", ".join(found)
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
        app.logger.exception("QR scanning error")
        return render_template(
            "index.html",
            result="Unable to read this QR image."
        )


if __name__ == "__main__":
    app.run(debug=True)
