import os, gridfs, pika, json
from flask import Flask, request, send_file
from flask_pymongo import PyMongo
from auth import validate
from auth_svc import access
from storage import util
from bson.objectid import ObjectId

server = Flask(__name__)

#server.config["MONGO_URI"] = "mongodb://mongodb-service:27017/videos"

#mongo = PyMongo(server)

mongo_video = PyMongo(server, uri="mongodb://mongodb-service:27017/videos", connect=False)

mongo_mp3 = PyMongo(server, uri="mongodb://mongodb-service:27017/mp3s", connect=False)

fs_videos = gridfs.GridFS(mongo_video.db)
fs_mp3s = gridfs.GridFS(mongo_mp3.db)

#fs = gridfs.GridFS(mongo.db)

connection = pika.BlockingConnection(pika.ConnectionParameters(host="rabbitmq.default.svc.cluster.local", port=5672, heartbeat=600, blocked_connection_timeout=300))
channel = connection.channel()

@server.route("/login", methods=["POST"])
def login():
    token, err = access.login(request)

    if not err:
        return token
    else:
        return err
    
@server.route("/upload", methods=["POST"])
def upload():
    try:
        access, err = validate.token(request)

        if err:
            server.logger.error(f"Token validation failed: {err}")
            return err

        try:
            access = json.loads(access)
        except Exception as e:
            server.logger.error(f"Failed to parse access: {e}")
            return "Invalid token format", 400

        if access["admin"]:
            if len(request.files) > 1 or len(request.files) < 1:
                return "exactly 1 file required", 400

            for _, f in request.files.items():
                err = util.upload(f, fs_videos, channel, access)

                if err:
                    server.logger.error(f"File upload failed: {err}")
                    return err

            return "success!", 200
        else:
            return "not authorized", 401
    except Exception as e:
        server.logger.error("Unexpected error during upload")
        return str(e), 500
    
@server.route("/download", methods=["GET"])
def download():
    pass

if __name__ == "__main__":
    server.run(host="0.0.0.0", port=8080)