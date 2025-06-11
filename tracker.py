
"""
Real-Time Person Detection and Tracking System
=============================================

A privacy-focused computer vision system that detects and tracks people using webcam,
creating a local database with organized folders for each unique individual.

Requirements:
- opencv-python
- face-recognition
- numpy
- pillow

Install with: pip install opencv-python face-recognition numpy pillow
"""

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
                 database_path: str = "./database",
                 update_interval: int = 300,  # 5 minutes in seconds
                 similarity_threshold: float = 0.6,
                 min_face_size: Tuple[int, int] = (50, 50),
                 detection_confidence: float = 0.8):
        """
        Initialize the Person Tracker system.
        
        Args:
            database_path: Path to store person folders
            update_interval: Time in seconds between image updates for same person
            similarity_threshold: Face similarity threshold (lower = more strict)
            min_face_size: Minimum face size to detect (width, height)
            detection_confidence: Minimum confidence for face detection
        """
        self.database_path = database_path
        self.update_interval = update_interval
        self.similarity_threshold = similarity_threshold
        self.min_face_size = min_face_size
        self.detection_confidence = detection_confidence
        
        # Initialize tracking variables
        self.known_faces = []
        self.known_names = []
        self.person_count = 0
        self.last_update_time = {}
        self.person_metadata = {}
        
        # Setup logging
        logging.basicConfig(level=logging.INFO, 
                          format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)
        
        # Create database directory
        os.makedirs(database_path, exist_ok=True)
        
        # Load existing database
        self._load_existing_database()
        
        # Initialize camera
        self.cap = None
        self._initialize_camera()
    
    def _initialize_camera(self):
        """Initialize the webcam."""
        try:
            self.cap = cv2.VideoCapture(0)
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            
            if not self.cap.isOpened():
                raise Exception("Could not open webcam")
            
            self.logger.info("Camera initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize camera: {e}")
            raise
    
    def _load_existing_database(self):
        """Load existing persons from database."""
        if not os.path.exists(self.database_path):
            return
        
        metadata_file = os.path.join(self.database_path, "metadata.json")
        
        # Load metadata if exists
        if os.path.exists(metadata_file):
            with open(metadata_file, 'r') as f:
                self.person_metadata = json.load(f)
        
        # Load known faces
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
                            
                            # Update person count
                            person_num = int(person_id.split('_')[1])
                            self.person_count = max(self.person_count, person_num)
                            
                            self.logger.info(f"Loaded existing person: {person_id}")
                    except Exception as e:
                        self.logger.warning(f"Could not load reference image for {person_id}: {e}")
    
    def _save_metadata(self):
        """Save person metadata to JSON file."""
        metadata_file = os.path.join(self.database_path, "metadata.json")
        with open(metadata_file, 'w') as f:
            json.dump(self.person_metadata, f, indent=2)
    
    def _create_person_folder(self, person_id: str) -> str:
        """Create folder for new person."""
        person_folder = os.path.join(self.database_path, person_id)
        os.makedirs(person_folder, exist_ok=True)
        
        # Initialize metadata
        self.person_metadata[person_id] = {
            'created': datetime.now().isoformat(),
            'total_images': 0,
            'last_seen': datetime.now().isoformat()
        }
        
        self._save_metadata()
        return person_folder
    
    def _save_person_image(self, frame: np.ndarray, face_location: Tuple, person_id: str) -> str:
        """Save image of detected person."""
        # Extract face region with some padding
        top, right, bottom, left = face_location
        padding = 50
        
        # Ensure coordinates are within frame bounds
        height, width = frame.shape[:2]
        top = max(0, top - padding)
        bottom = min(height, bottom + padding)
        left = max(0, left - padding)
        right = min(width, right + padding)
        
        # Extract face region
        face_image = frame[top:bottom, left:right]
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{person_id}_{timestamp}.jpg"
        
        # Create person folder if it doesn't exist
        person_folder = os.path.join(self.database_path, person_id)
        if not os.path.exists(person_folder):
            person_folder = self._create_person_folder(person_id)
        
        # Save image
        filepath = os.path.join(person_folder, filename)
        cv2.imwrite(filepath, face_image)
        
        # Update metadata
        if person_id in self.person_metadata:
            self.person_metadata[person_id]['total_images'] += 1
            self.person_metadata[person_id]['last_seen'] = datetime.now().isoformat()
            self._save_metadata()
        
        self.logger.info(f"Saved image: {filepath}")
        return filepath
    
    def _detect_faces(self, frame: np.ndarray) -> Tuple[List, List]:
        """Detect faces in the frame and return locations and encodings."""
        # Convert BGR to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Find face locations and encodings
        face_locations = face_recognition.face_locations(rgb_frame, model="hog")
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
        
        # Filter faces by minimum size
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
        """Identify person based on face encoding."""
        if not self.known_faces:
            return None
        
        # Compare with known faces
        distances = face_recognition.face_distance(self.known_faces, face_encoding)
        min_distance = np.min(distances)
        
        if min_distance < self.similarity_threshold:
            best_match_index = np.argmin(distances)
            return self.known_names[best_match_index]
        
        return None
    
    def _register_new_person(self, face_encoding: np.ndarray) -> str:
        """Register a new person."""
        self.person_count += 1
        person_id = f"Person_{self.person_count}"
        
        # Add to known faces
        self.known_faces.append(face_encoding)
        self.known_names.append(person_id)
        self.last_update_time[person_id] = time.time()
        
        self.logger.info(f"Registered new person: {person_id}")
        return person_id
    
    def _should_update_person(self, person_id: str) -> bool:
        """Check if person should be updated based on time interval."""
        current_time = time.time()
        last_update = self.last_update_time.get(person_id, 0)
        
        return (current_time - last_update) >= self.update_interval
    
    def _draw_detections(self, frame: np.ndarray, face_locations: List, person_ids: List) -> np.ndarray:
        """Draw bounding boxes and labels on frame."""
        for location, person_id in zip(face_locations, person_ids):
            top, right, bottom, left = location
            
            # Draw rectangle
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
            
            # Draw label
            label = person_id
            cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 255, 0), cv2.FILLED)
            cv2.putText(frame, label, (left + 6, bottom - 6), 
                       cv2.FONT_HERSHEY_DUPLEX, 0.6, (255, 255, 255), 1)
        
        return frame
    
    def start_tracking(self, show_preview: bool = True):
        """Start the real-time tracking system."""
        self.logger.info("Starting person tracking system...")
        
        try:
            while True:
                ret, frame = self.cap.read()
                if not ret:
                    self.logger.error("Failed to read frame from camera")
                    break
                
                # Detect faces
                face_locations, face_encodings = self._detect_faces(frame)
                
                person_ids = []
                
                # Process each detected face
                for face_location, face_encoding in zip(face_locations, face_encodings):
                    # Try to identify person
                    person_id = self._identify_person(face_encoding)
                    
                    # If unknown person, register them
                    if person_id is None:
                        person_id = self._register_new_person(face_encoding)
                        # Save first image immediately
                        self._save_person_image(frame, face_location, person_id)
                    else:
                        # Check if we should update existing person
                        if self._should_update_person(person_id):
                            self._save_person_image(frame, face_location, person_id)
                            self.last_update_time[person_id] = time.time()
                    
                    person_ids.append(person_id)
                
                # Show preview if enabled
                if show_preview:
                    display_frame = self._draw_detections(frame.copy(), face_locations, person_ids)
                    
                    # Add system info
                    info_text = f"Tracked Persons: {len(self.known_names)} | Press 'q' to quit"
                    cv2.putText(display_frame, info_text, (10, 30), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                    
                    cv2.imshow('Person Tracker', display_frame)
                    
                    # Check for quit
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break
                
                # Small delay to prevent excessive CPU usage
                time.sleep(0.1)
        
        except KeyboardInterrupt:
            self.logger.info("Tracking stopped by user")
        except Exception as e:
            self.logger.error(f"Error during tracking: {e}")
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Clean up resources."""
        self.logger.info("Cleaning up resources...")
        
        if self.cap:
            self.cap.release()
        
        cv2.destroyAllWindows()
        
        # Save final metadata
        self._save_metadata()
        
        self.logger.info("Cleanup completed")
    
    def get_statistics(self) -> Dict:
        """Get tracking statistics."""
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
    """Main function to run the person tracking system."""
    print("Person Detection and Tracking System")
    print("===================================")
    
    # Configuration
    config = {
        'database_path': './database',
        'update_interval': 300,  # 5 minutes
        'similarity_threshold': 0.6,
        'min_face_size': (50, 50),
        'detection_confidence': 0.8
    }
    
    try:
        # Initialize tracker
        tracker = PersonTracker(**config)
        
        # Display configuration
        print(f"Database Path: {config['database_path']}")
        print(f"Update Interval: {config['update_interval']} seconds")
        print(f"Similarity Threshold: {config['similarity_threshold']}")
        print("\nStarting tracking... Press 'q' in the video window to quit.")
        
        # Start tracking
        tracker.start_tracking(show_preview=True)
        
        # Display final statistics
        stats = tracker.get_statistics()
        print(f"\nFinal Statistics:")
        print(f"Total Persons Tracked: {stats['total_persons']}")
        for person_id, data in stats['persons'].items():
            print(f"  {person_id}: {data['total_images']} images")
    
    except Exception as e:
        print(f"Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
