import os
import uuid

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    flash,
    url_for,
    Response
)

import config
from services.yolo_service import yolo_service

# ==========================================================
# Flask App
# ==========================================================

app = Flask(__name__)

app.secret_key = config.SECRET_KEY

app.config["UPLOAD_FOLDER"] = config.UPLOAD_FOLDER
app.config["OUTPUT_FOLDER"] = config.OUTPUT_FOLDER
app.config["MAX_CONTENT_LENGTH"] = config.MAX_CONTENT_LENGTH


# ==========================================================
# Helper Functions
# ==========================================================

def allowed_image(filename):

    if "." not in filename:
        return False

    extension = filename.rsplit(".", 1)[1].lower()

    return extension in config.ALLOWED_IMAGE_EXTENSIONS


def allowed_video(filename):

    if "." not in filename:
        return False

    extension = filename.rsplit(".", 1)[1].lower()

    return extension in config.ALLOWED_VIDEO_EXTENSIONS


def generate_filename(filename):

    extension = filename.rsplit(".", 1)[1].lower()

    return f"{uuid.uuid4().hex}.{extension}"


# ==========================================================
# HOME
# ==========================================================

@app.route("/")
def home():

    return render_template("index.html")


# ==========================================================
# IMAGE DETECTION
# ==========================================================

@app.route("/image", methods=["GET", "POST"])
def image():

    if request.method == "POST":

        if "image" not in request.files:

            flash("Please choose an image.", "warning")

            return redirect(request.url)

        file = request.files["image"]

        if file.filename == "":

            flash("No image selected.", "warning")

            return redirect(request.url)

        if not allowed_image(file.filename):

            flash("Unsupported image format.", "danger")

            return redirect(request.url)

        filename = generate_filename(file.filename)

        upload_path = os.path.join(

            app.config["UPLOAD_FOLDER"],

            filename

        )

        file.save(upload_path)

        result = yolo_service.detect_image(upload_path)

        if not result["success"]:

            flash("Detection failed.", "danger")

            return redirect(request.url)

        result["original"] = filename

        return render_template(

            "image.html",

            result=result

        )

    return render_template("image.html")
# ==========================================================
# VIDEO DETECTION
# ==========================================================

@app.route("/video", methods=["GET", "POST"])
def video():

    if request.method == "POST":

        if "video" not in request.files:

            flash("Please choose a video.", "warning")

            return redirect(request.url)

        file = request.files["video"]

        if file.filename == "":

            flash("No video selected.", "warning")

            return redirect(request.url)

        if not allowed_video(file.filename):

            flash("Unsupported video format.", "danger")

            return redirect(request.url)

        filename = generate_filename(file.filename)

        upload_path = os.path.join(

            app.config["UPLOAD_FOLDER"],

            filename

        )

        file.save(upload_path)

        result = yolo_service.detect_video(upload_path)

        if not result["success"]:

            flash(result.get("message", "Video processing failed."), "danger")

            return redirect(request.url)

        result["original"] = filename

        return render_template(

            "video.html",

            result=result

        )

    return render_template("video.html")


# ==========================================================
# LIVE DETECTION
# ==========================================================

@app.route("/live")
def live():

    return render_template("live.html")


@app.route("/video_feed")
def video_feed():

    return Response(

        yolo_service.stream_camera(),

        mimetype="multipart/x-mixed-replace; boundary=frame"

    )


# ==========================================================
# ABOUT
# ==========================================================

@app.route("/about")
def about():

    return render_template("about.html")
# ==========================================================
# ERROR HANDLERS
# ==========================================================

@app.errorhandler(404)
def page_not_found(error):

    return render_template(

        "404.html",

        error=error

    ), 404


@app.errorhandler(413)
def file_too_large(error):

    flash(

        "Uploaded file exceeds the maximum allowed size.",

        "danger"

    )

    return redirect(url_for("home"))


@app.errorhandler(500)
def internal_server_error(error):

    return render_template(

        "500.html",

        error=error

    ), 500


# ==========================================================
# RUN APPLICATION
# ==========================================================

if __name__ == "__main__":

    app.run(

        debug=True,

        host="0.0.0.0",

        port=5000

    )