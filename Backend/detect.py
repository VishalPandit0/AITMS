import os
from ultralytics import YOLO
import cv2 as cv
import time
from collections import deque
import numpy as np
from scipy.signal import find_peaks

def detect_cars(video_file):
    COLOR_VEHICLE = (0, 255, 0)
    COLOR_AMBULANCE = (0, 0, 255)  # Red for ambulance

    # Load YOLOv8 model
    model_path = os.path.join('Models', 'new.pt')
    model = YOLO(model_path)

    # Define vehicle-related classes
    VEHICLE_CLASSES = {'Ambulance', 'Auto', 'Bus', 'Car', 'Cargo-Van', 'E-Rickshaw',
                       'Fire-Engine-Ambulance', 'JCB', 'Motorcycle', 'Rickshaw',
                       'Roller-compactor', 'Scooty', 'Taxi', 'Truck', 'Van'}
    
    AMBULANCE_CLASSES = {'Ambulance', 'Fire-Engine-Ambulance'}

    cap = cv.VideoCapture(video_file)
    starting_time = time.time()
    frame_counter = 0

    cv.namedWindow('frame', cv.WINDOW_NORMAL)
    cv.setWindowProperty('frame', cv.WND_PROP_FULLSCREEN, cv.WINDOW_FULLSCREEN)

    car_counts = deque()
    ambulance_detected = False

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame_counter += 1
        results = model.predict(frame, conf=0.3, verbose=False)[0]

        car_count = 0
        current_ambulance = False
        
        for box in results.boxes:
            class_id = int(box.cls.item())
            confidence = float(box.conf.item())
            label = model.names[class_id]

            if label in VEHICLE_CLASSES:
                car_count += 1
                coords = box.xyxy[0].cpu().numpy().astype(int)
                
                # Use red color for ambulance
                color = COLOR_AMBULANCE if label in AMBULANCE_CLASSES else COLOR_VEHICLE
                cv.rectangle(frame, (coords[0], coords[1]), (coords[2], coords[3]), color, 2)
                cv.putText(frame, f'{label}: {confidence:.2f}', (coords[0], coords[1] - 10),
                           cv.FONT_HERSHEY_COMPLEX, 0.5, color, 2)
                
                if label in AMBULANCE_CLASSES:
                    current_ambulance = True

        ambulance_detected = ambulance_detected or current_ambulance
        current_time = time.time()
        car_counts.append((current_time, car_count, current_ambulance))

        while car_counts and car_counts[0][0] < current_time - 30:
            car_counts.popleft()

        car_count_values = [count for _, count, _ in car_counts]
        peaks, _ = find_peaks(car_count_values)
        mean_peak_value = np.mean([car_count_values[i] for i in peaks]) if peaks.size > 0 else (
            np.mean(car_count_values) if car_count_values else 0)

        ending_time = time.time()
        fps = frame_counter / (ending_time - starting_time)
        
        # Display ambulance alert if detected
        if ambulance_detected:
            cv.putText(frame, 'AMBULANCE DETECTED!', (20, 120),
                      cv.FONT_HERSHEY_COMPLEX, 1, (0, 0, 255), 3)
        
        cv.putText(frame, f'FPS: {fps:.2f}', (20, 50),
                   cv.FONT_HERSHEY_COMPLEX, 0.7, (0, 255, 0), 2)
        cv.putText(frame, f'Mean Peak Vehicles: {mean_peak_value:.2f}', (20, 80),
                   cv.FONT_HERSHEY_COMPLEX, 0.7, (0, 255, 255), 2)

        cv.imshow('frame', frame)
        if cv.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv.destroyAllWindows()

    return {
        'vehicle_count': mean_peak_value,
        'ambulance_detected': ambulance_detected
    }