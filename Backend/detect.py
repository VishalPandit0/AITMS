import os
from ultralytics import YOLO
import cv2 as cv
import time
from collections import deque
import numpy as np
from scipy.signal import find_peaks

def detect_cars(video_file):
    # Green color for vehicle detection
    COLOR_VEHICLE = (0, 255, 0)

    # Load YOLOv8 model
    model_path = os.path.join('Models', 'best.pt')
    model = YOLO(model_path)

    # Print class names for confirmation
    print("Model classes:", model.names)

    # Open video file
    cap = cv.VideoCapture(video_file)
    starting_time = time.time()
    frame_counter = 0

    # Create full screen display window
    cv.namedWindow('frame', cv.WINDOW_NORMAL)
    cv.setWindowProperty('frame', cv.WND_PROP_FULLSCREEN, cv.WINDOW_FULLSCREEN)

    # To keep track of vehicle counts over time
    car_counts = deque()  # (timestamp, count)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame_counter += 1

        # Predict using YOLOv8
        results = model.predict(frame, conf=0.3, verbose=False)[0]

        # Count vehicles
        car_count = 0
        for box in results.boxes:
            class_id = int(box.cls.item())
            confidence = float(box.conf.item())
            label = model.names[class_id]

            if label == "Vehicle":
                car_count += 1
                coords = box.xyxy[0].cpu().numpy().astype(int)
                cv.rectangle(frame, (coords[0], coords[1]), (coords[2], coords[3]), COLOR_VEHICLE, 2)
                cv.putText(frame, f'{label}: {confidence:.2f}', (coords[0], coords[1] - 10),
                           cv.FONT_HERSHEY_COMPLEX, 0.5, COLOR_VEHICLE, 2)

        # Save current count with timestamp
        current_time = time.time()
        car_counts.append((current_time, car_count))

        # Keep only last 30 seconds of data
        while car_counts and car_counts[0][0] < current_time - 30:
            car_counts.popleft()

        # Extract counts for analysis
        car_count_values = [count for _, count in car_counts]
        peaks, _ = find_peaks(car_count_values)
        mean_peak_value = np.mean([car_count_values[i] for i in peaks]) if peaks.size > 0 else (
            np.mean(car_count_values) if car_count_values else 0)

        # Calculate and display FPS
        ending_time = time.time()
        fps = frame_counter / (ending_time - starting_time)
        cv.putText(frame, f'FPS: {fps:.2f}', (20, 50),
                   cv.FONT_HERSHEY_COMPLEX, 0.7, (0, 255, 0), 2)

        # Show mean peak vehicles
        cv.putText(frame, f'Mean Peak Vehicles: {mean_peak_value:.2f}', (20, 80),
                   cv.FONT_HERSHEY_COMPLEX, 0.7, (0, 255, 255), 2)

        # Show the processed frame
        cv.imshow('frame', frame)
        if cv.waitKey(1) & 0xFF == ord('q'):
            break

    # Cleanup
    cap.release()
    cv.destroyAllWindows()

    return mean_peak_value
