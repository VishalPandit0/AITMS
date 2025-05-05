import os
from flask import Flask, request, jsonify
from detect import detect_cars
from algo import optimize_traffic
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

if not os.path.exists('uploads'):
    os.makedirs('uploads')

@app.route('/')
def home():
    return "🚦 AI Traffic Optimizer with Emergency Priority is live."

@app.route('/ping')
def ping():
    return "pong"

@app.route('/upload', methods=['POST'])
def upload_files():
    if 'videos' not in request.files or len(request.files.getlist('videos')) != 4:
        return jsonify({"error": "Please upload exactly 4 videos (lane1 to lane4)."}), 400

    video_files = request.files.getlist('videos')
    video_paths = []
    directions = ['lane1', 'lane2', 'lane3', 'lane4']

    try:
        for i, video in enumerate(video_files):
            if not video.filename.endswith(('.mp4', '.avi', '.mov')):
                return jsonify({"error": "Only MP4, AVI, and MOV formats are allowed."}), 400
            path = f"uploads/{directions[i]}.mp4"
            video.save(path)
            video_paths.append(path)

        traffic_data = []
        for i, video_path in enumerate(video_paths):
            detection = detect_cars(video_path)
            if detection is None:
                return jsonify({"error": f"Error processing video: {video_path}"}), 500
            traffic_data.append({
                'direction': directions[i],
                'vehicle_count': detection['vehicle_count'],
                'ambulance_detected': detection['ambulance_detected']
            })

        signal_durations = optimize_traffic(traffic_data)
        if not signal_durations:
            return jsonify({"error": "Traffic optimization failed."}), 500

        return jsonify({
            "optimized_times": {
                "lane1": signal_durations['lane1'],
                "lane2": signal_durations['lane2'],
                "lane3": signal_durations['lane3'],
                "lane4": signal_durations['lane4']
            },
            "priority": signal_durations['priority'],
            "traffic_data": traffic_data
        })

    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True)
