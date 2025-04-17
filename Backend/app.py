import os
from flask import Flask, request, jsonify
from detect import detect_cars  
from algo import optimize_traffic  
from flask_cors import CORS  

app = Flask(__name__)
CORS(app)

# Ensure upload directory exists
if not os.path.exists('uploads'):
    os.makedirs('uploads')

@app.route('/')
def home():
    return "🚦 AI Traffic Optimizer is live."

@app.route('/ping')
def ping():
    return "pong"

@app.route('/upload', methods=['POST'])
def upload_files():
    if 'videos' not in request.files or len(request.files.getlist('videos')) != 4:
        return jsonify({"error": "Please upload exactly 4 videos."}), 400

    video_files = request.files.getlist('videos')
    video_paths = []

    try:
        # Save uploaded videos
        for i, video in enumerate(video_files):
            if not video.filename.endswith(('.mp4', '.avi', '.mov')):
                return jsonify({"error": "Only MP4, AVI, and MOV formats are allowed."}), 400
            video_filename = f"uploads/video_{i}.mp4"
            video.save(video_filename)
            video_paths.append(video_filename)

        # Process videos and detect cars
        car_counts = []
        for video_path in video_paths:
            car_count = detect_cars(video_path)
            if car_count is None:
                return jsonify({"error": f"Error processing video: {video_path}"}), 500
            car_counts.append(car_count)

        # Optimize traffic signals
        signal_durations = optimize_traffic(car_counts)
        if not signal_durations or len(signal_durations) != 4:
            return jsonify({"error": "Traffic optimization failed."}), 500

        return jsonify({
            "north": signal_durations['north'],
            "south": signal_durations['south'],
            "west": signal_durations['west'],
            "east": signal_durations['east']
        })

    except Exception as e:
        print(f"Exception: {str(e)}")
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500
