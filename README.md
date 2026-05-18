# Real-Time Person Tracker

Tracks people through a webcam and builds a local image database. Each new face gets its own folder. Returning faces get updated photos on a configurable interval.

I built this to experiment with face recognition and to log who comes and goes at a fixed camera — no cloud, no accounts, everything stays on disk.

---

## Setup

```bash
git clone https://github.com/mighty-baseplate/Real-Time-Person-Tracker.git
cd Real-Time-Person-Tracker
pip install -r requirements.txt
```

**dlib note:** `face-recognition` depends on dlib, which needs CMake and a C++ compiler.

- Linux: `sudo apt-get install build-essential cmake python3-dev`
- Windows: install CMake (`pip install cmake`) and Visual Studio build tools, or grab a pre-built `.whl` for your Python version

---

## Usage

```bash
python tracker.py
```

Press `q` to quit the video window.

### Options

| Argument | Default | Description |
|---|---|---|
| `--camera_id` | `0` | Webcam index |
| `--database_path` | `./database` | Where to store images |
| `--update_interval` | `300` | Seconds between re-saving the same person |
| `--similarity_threshold` | `0.6` | Match strictness — lower is stricter |
| `--min_face_size` | `(50, 50)` | Minimum face size in pixels to track |
| `--detection_confidence` | `0.8` | Minimum confidence for face detection |
| `--face_detection_model` | `hog` | `hog` (CPU, faster) or `cnn` (GPU, more accurate) |
| `--no_preview` | — | Disable the live video window |

**Examples:**

```bash
# Use a specific camera and skip the preview
python tracker.py --camera_id 1 --no_preview

# Use CNN model with stricter matching
python tracker.py --face_detection_model cnn --similarity_threshold 0.5
```

---

## How it works

Each frame, detected faces are compared against the known-faces database using L2 distance on face encodings (dlib under the hood). A new face creates a new `Person_N` folder and saves an initial photo. Known faces get a new photo after the update interval expires.

The database folder structure:

```
database/
├── Person_1/
│   ├── Person_1_20240101_120000.jpg
│   └── Person_1_20240101_120500.jpg
├── Person_2/
│   └── ...
└── metadata.json
```

---

## Known issues / TODO

- Folder names are generic (`Person_1`, `Person_2`) with no way to rename via the CLI
- On slower machines the HOG model can drop frames; the 100ms sleep between frames helps but isn't adaptive
- Only the first image in a person's folder is loaded as the reference encoding on startup, so accuracy doesn't improve from accumulated photos
- No deduplication if the database already has the same person under two different folders

---

## Disclaimer

This stores face images locally. Make sure you have consent from anyone being recorded.
