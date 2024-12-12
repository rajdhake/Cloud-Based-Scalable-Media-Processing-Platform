import pika, json, tempfile, os
from bson.objectid import ObjectId
import moviepy.editor
from contextlib import contextmanager

def start(message, fs_videos, fs_mp3s, channel):
    try:
        message = json.loads(message)

        # Temporary directory for video processing
        tmp_dir = tempfile.mkdtemp()
        video_path = os.path.join(tmp_dir, f"{message['video_fid']}.mp4")
        mp3_path = os.path.join(tmp_dir, f"{message['video_fid']}.mp3")
        
        # Retrieve video from GridFS
        print(f"Fetching video {message['video_fid']} from GridFS.")
        out = fs_videos.get(ObjectId(message["video_fid"]))
        with open(video_path, "wb") as f:
            f.write(out.read())

        # create audio from temp video file
        print(f"Converting video {video_path} to audio.")
        video = moviepy.editor.VideoFileClip(video_path)
        audio = video.audio
        try:
            audio.write_audiofile(mp3_path)
        finally:
            # Clean up moviepy resources
            audio.close()
            video.close()
            del audio, video

        # save file to mongo
        print(f"Saving MP3 to GridFS: {mp3_path}.")
        with open(mp3_path, "rb") as f:
            mp3_data  = f.read()
            fid = fs_mp3s.put(mp3_data)

        # Clean up temp mp3 file
        os.remove(video_path)
        os.remove(mp3_path)
        os.rmdir(tmp_dir)

        message["mp3_fid"] = str(fid)

        # Publish to queue
        channel.basic_publish(
            exchange="",
            routing_key=os.environ.get("MP3_QUEUE"),
            body=json.dumps(message),
            properties=pika.BasicProperties(
                delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE
            ),
        )
        print(f"Successfully processed video {message['video_fid']}.")
        return None

    except Exception as err:
        print(f"Error processing video: {str(err)}")
        if 'fid' in locals():
            fs_mp3s.delete(fid)
        if 'tf_path' in locals() and os.path.exists(tmp_dir):
            for temp_file in os.listdir(tmp_dir):
                os.remove(os.path.join(tmp_dir, temp_file))
            os.rmdir(tmp_dir)
        return f"Error processing video: {str(err)}"