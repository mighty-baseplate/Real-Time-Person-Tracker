import argparse
import cv2
import face_recognition
import numpy as np
import os
import json
import time
from datetime import datetime
from typing import List, Dict, Tuple, Optional
import logging

class PersonTracker:
    def __init__(self, 
                 camera_id: int = 0,
                 database_path: str = "./database",
                 update_interval: int = 300,  # 5 minutes in seconds
                 similarity_threshold: float = 0.6,
                 min_face_size: Tuple[int, int] = (50, 50),
                 detection_confidence: float = 0.8,
                 face_detection_model: str = "hog"):
        self.camera_id = camera_id
        self.database_path = database_path
        self.update_interval = update_interval
        self.similarity_threshold = similarity_threshold
        self.min_face_size = min_face_size
        self.detection_confidence = detection_confidence
        self.face_detection_model = face_detection_model

        self.known_faces = []
        self.known_names = []
        self.person_count = 0
        self.last_update_time = {}
        self.person_metadata = {}

        logging.basicConfig(level=logging.INFO,
                          format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)

        os.makedirs(database_path, exist_ok=True)
        self._load_existing_database()

        self.cap = None
        self._initialize_camera()
    
    def _initialize_camera(self):
        try:
            self.cap = cv2.VideoCapture(self.camera_id)
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            
            if not self.cap.isOpened():
                raise Exception("Could not open webcam")
            
            self.logger.info("Camera initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize camera: {e}")
            raise
    
    def _load_existing_database(self):
        if not os.path.exists(self.database_path):
            return
        
        metadata_file = os.path.join(self.database_path, "metadata.json")

        if os.path.exists(metadata_file):
            with open(metadata_file, 'r') as f:
                self.person_metadata = json.load(f)
        
        for person_folder in os.listdir(self.database_path):
            person_path = os.path.join(self.database_path, person_folder)
            
            if os.path.isdir(person_path) and person_folder.startswith("Person_"):
                person_id = person_folder
                
                # Load first image as reference
                images = [f for f in os.listdir(person_path) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
                
                if images:
                    ref_image_path = os.path.join(person_path, images[0])
                    try:
                        reference_image = face_recognition.load_image_file(ref_image_path)
                        face_encodings = face_recognition.face_encodings(reference_image)
                        
                        if face_encodings:
                            self.known_faces.append(face_encodings[0])
                            self.known_names.append(person_id)
                            self.last_update_time[person_id] = 0

                            person_num = int(person_id.split('_')[1])
                            self.person_count = max(self.person_count, person_num)
                            
                            self.logger.info(f"Loaded existing person: {person_id}")
                    except Exception as e:
                        self.logger.warning(f"Could not load reference image for {person_id}: {e}")
    
    def _save_metadata(self):
        metadata_file = os.path.join(self.database_path, "metadata.json")
        with open(metadata_file, 'w') as f:
            json.dump(self.person_metadata, f, indent=2)
    
    def _create_person_folder(self, person_id: str) -> str:
        person_folder = os.path.join(self.database_path, person_id)
        os.makedirs(person_folder, exist_ok=True)

        self.person_metadata[person_id] = {
            'created': datetime.now().isoformat(),
            'total_images': 0,
            'last_seen': datetime.now().isoformat()
        }
        
        self._save_metadata()
        return person_folder
    
    def _save_person_image(self, frame: np.ndarray, face_location: Tuple, person_id: str) -> str:
        top, right, bottom, left = face_location
        padding = 50

        # Clamp to frame bounds
        height, width = frame.shape[:2]
        top = max(0, top - padding)
        bottom = min(height, bottom + padding)
        left = max(0, left - padding)
        right = min(width, right + padding)

        face_image = frame[top:bottom, left:right]

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{person_id}_{timestamp}.jpg"

        person_folder = os.path.join(self.database_path, person_id)
        if not os.path.exists(person_folder):
            person_folder = self._create_person_folder(person_id)

        filepath = os.path.join(person_folder, filename)
        cv2.imwrite(filepath, face_image)

        if person_id in self.person_metadata:
            self.person_metadata[person_id]['total_images'] += 1
            self.person_metadata[person_id]['last_seen'] = datetime.now().isoformat()
            self._save_metadata()
        
        self.logger.info(f"Saved image: {filepath}")
        return filepath
    
    def _detect_faces(self, frame: np.ndarray) -> Tuple[List, List]:
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        face_locations = face_recognition.face_locations(rgb_frame, model=self.face_detection_model)
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

        filtered_locations = []
        filtered_encodings = []
        
        for location, encoding in zip(face_locations, face_encodings):
            top, right, bottom, left = location
            face_width = right - left
            face_height = bottom - top
            
            if face_width >= self.min_face_size[0] and face_height >= self.min_face_size[1]:
                filtered_locations.append(location)
                filtered_encodings.append(encoding)
        
        return filtered_locations, filtered_encodings
    
    def _identify_person(self, face_encoding: np.ndarray) -> Optional[str]:
        if not self.known_faces:
            return None

        distances = face_recognition.face_distance(self.known_faces, face_encoding)
        min_distance = np.min(distances)
        
        if min_distance < self.similarity_threshold:
            best_match_index = np.argmin(distances)
            return self.known_names[best_match_index]
        
        return None
    
    def _register_new_person(self, face_encoding: np.ndarray) -> str:
        self.person_count += 1
        person_id = f"Person_{self.person_count}"

        self.known_faces.append(face_encoding)
        self.known_names.append(person_id)
        self.last_update_time[person_id] = time.time()
        
        self.logger.info(f"Registered new person: {person_id}")
        return person_id
    
    def _should_update_person(self, person_id: str) -> bool:
        current_time = time.time()
        last_update = self.last_update_time.get(person_id, 0)
        
        return (current_time - last_update) >= self.update_interval
    
    def _draw_detections(self, frame: np.ndarray, face_locations: List, person_ids: List) -> np.ndarray:
        for location, person_id in zip(face_locations, person_ids):
            top, right, bottom, left = location

            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)

            label = person_id
            cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 255, 0), cv2.FILLED)
            cv2.putText(frame, label, (left + 6, bottom - 6), 
                       cv2.FONT_HERSHEY_DUPLEX, 0.6, (255, 255, 255), 1)
        
        return frame
    
    def start_tracking(self, show_preview: bool = True):
        self.logger.info("Starting person tracking system...")
        
        try:
            while True:
                ret, frame = self.cap.read()
                if not ret:
                    self.logger.error("Failed to read frame from camera")
                    break
                
                face_locations, face_encodings = self._detect_faces(frame)

                person_ids = []

                for face_location, face_encoding in zip(face_locations, face_encodings):
                    person_id = self._identify_person(face_encoding)

                    if person_id is None:
                        person_id = self._register_new_person(face_encoding)
                        # Save first image immediately
                        self._save_person_image(frame, face_location, person_id)
                    else:
                        if self._should_update_person(person_id):
                            self._save_person_image(frame, face_location, person_id)
                            self.last_update_time[person_id] = time.time()
                    
                    person_ids.append(person_id)
                
                if show_preview:
                    display_frame = self._draw_detections(frame.copy(), face_locations, person_ids)

                    info_text = f"Tracked Persons: {len(self.known_names)} | Press 'q' to quit"
                    cv2.putText(display_frame, info_text, (10, 30), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                    
                    cv2.imshow('Person Tracker', display_frame)

                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break

                time.sleep(0.1)  # avoid pegging the CPU between frames
        
        except KeyboardInterrupt:
            self.logger.info("Tracking stopped by user")
        except Exception as e:
            self.logger.error(f"Error during tracking: {e}")
        finally:
            self.cleanup()
    
    def cleanup(self):
        self.logger.info("Cleaning up resources...")

        if self.cap:
            self.cap.release()

        cv2.destroyAllWindows()
        self._save_metadata()

        self.logger.info("Cleanup completed")
    
    def get_statistics(self) -> Dict:
        stats = {
            'total_persons': len(self.known_names),
            'database_path': self.database_path,
            'persons': {}
        }
        
        for person_id in self.known_names:
            person_folder = os.path.join(self.database_path, person_id)
            if os.path.exists(person_folder):
                images = [f for f in os.listdir(person_folder) 
                         if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
                stats['persons'][person_id] = {
                    'total_images': len(images),
                    'metadata': self.person_metadata.get(person_id, {})
                }
        
        return stats

def main():
    parser = argparse.ArgumentParser(description="Real-Time Person Detection and Tracking System.")
    parser.add_argument("--camera_id", type=int, default=0, help="Webcam ID (0 for default).")
    parser.add_argument("--database_path", type=str, default="./database", help="Where to store person folders.")
    parser.add_argument("--update_interval", type=int, default=300, help="Seconds between saving new images for the same person.")
    parser.add_argument("--similarity_threshold", type=float, default=0.6, help="Face match threshold (lower = stricter).")
    parser.add_argument("--min_face_size", type=str, default="(50, 50)", help='Minimum face size in pixels, e.g. "(50, 50)".')
    parser.add_argument("--detection_confidence", type=float, default=0.8, help="Minimum confidence for face detection.")
    parser.add_argument("--face_detection_model", type=str, default="hog", choices=["hog", "cnn"],
                        help="Detection model: hog (CPU) or cnn (GPU).")
    parser.add_argument("--no_preview", action="store_true", help="Disable the live video window.")
    args = parser.parse_args()

    try:
        min_face_size_tuple = tuple(map(int, args.min_face_size.strip("()").split(",")))
        if len(min_face_size_tuple) != 2:
            raise ValueError
    except ValueError:
        print('Error: --min_face_size must be in "(width, height)" format, e.g. "(50, 50)".')
        return 1

    print("Person Detection and Tracking System")
    print("=====================================")

    try:
        tracker = PersonTracker(
            camera_id=args.camera_id,
            database_path=args.database_path,
            update_interval=args.update_interval,
            similarity_threshold=args.similarity_threshold,
            min_face_size=min_face_size_tuple,
            detection_confidence=args.detection_confidence,
            face_detection_model=args.face_detection_model,
        )

        print(f"Database:           {args.database_path}")
        print(f"Update interval:    {args.update_interval}s")
        print(f"Threshold:          {args.similarity_threshold}")
        print(f"Min face size:      {min_face_size_tuple}")
        print(f"Detection model:    {args.face_detection_model}")
        print("\nPress 'q' in the video window to quit.\n")

        tracker.start_tracking(show_preview=not args.no_preview)

        stats = tracker.get_statistics()
        print(f"\nTotal persons tracked: {stats['total_persons']}")
        for person_id, data in stats["persons"].items():
            print(f"  {person_id}: {data['total_images']} images")

    except Exception as e:
        print(f"Error: {e}")
        return 1

    return 0

if __name__ == "__main__":
    exit(main())
