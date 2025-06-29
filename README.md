# Real-Time Person Tracker 🕵️‍♂️

A privacy-focused, real-time person detection and tracking system that uses your webcam to identify and log unique individuals, creating an organized local database of their images.

---

## ✨ Features

- **Real-time Detection & Tracking:** Identifies and tracks people in live video streams.
- **Automatic Database Creation:** Organizes detected individuals into separate folders.
- **Privacy-Focused:** Stores images locally, no cloud uploads.
- **Configurable Parameters:** Easily adjust detection sensitivity, update intervals, and more via command-line arguments.
- **Flexible Face Detection:** Choose between `hog` (faster, CPU-based) and `cnn` (more accurate, GPU-accelerated) models.
- **Detailed Logging:** Provides informative output for tracking progress and issues.

---

## 🚀 Demo

*(This is a placeholder. You can replace this with a GIF or video of your project in action.)*

![Demo Placeholder](https://i.imgur.com/gJ7eD9b.gif)

---

## 🛠️ Installation

**1. Clone the repository:**
```bash
git clone https://github.com/mighty-baseplate/Real-Time-Person-Tracker.git
cd Real-Time-Person-Tracker
```

**2. Install all dependencies:**
```bash
pip install -r requirements.txt
```

> **Note:** `face-recognition` depends on `dlib`, which can be tricky to install on some systems. Refer to the [Dlib Installation Tips](#-dlib-installation-tips) section for guidance.

---

## 🧠 How It Works

- Opens your webcam and captures frames in real time.
- Detects all faces in each frame using either HOG or CNN models.
- Encodes detected faces and compares them to known individuals in the local database.
- For new faces:
  - Creates a new folder (`database/Person_X/`).
  - Saves their initial face image.
- For recognized faces:
  - Saves a new image only after a configurable time interval (`--update_interval`).

---

## 📁 Project Structure

```
Real-Time-Person-Tracker/
├── database/           # Auto-created; stores folders for each person
│   ├── Person_1/
│   ├── Person_2/
│   └── ...
├── .gitignore
├── LICENSE
├── README.md           # This file
├── requirements.txt
└── tracker.py          # Main script
```

---

## 🚀 Usage

Run the tracker from your terminal. You can customize its behavior using command-line arguments:

```bash
python tracker.py [OPTIONS]
```

**Basic Usage:**
```bash
python tracker.py
```

**Example with Custom Database Path and Preview Disabled:**
```bash
python tracker.py --database_path ./my_people_data --no_preview
```

**Example with CNN Face Detection Model and Higher Sensitivity:**
```bash
python tracker.py --face_detection_model cnn --similarity_threshold 0.5
```

**Press `q` in the video window to quit.**

---

## ⚙️ Configuration Options

| Argument                 | Type    | Default     | Description                                                                 |
|--------------------------|---------|-------------|-----------------------------------------------------------------------------|
| `--camera_id`            | `int`   | `0`         | ID of the webcam to use (e.g., 0 for default, 1 for external).              |
| `--database_path`        | `str`   | `./database`| Path to the directory where person folders and images will be stored.       |

| `--update_interval`      | `int`   | `300`       | Time in seconds (5 minutes) between saving new images for the same person.  |
| `--similarity_threshold` | `float` | `0.6`       | Face similarity threshold (lower value = more strict matching).             |
| `--min_face_size`        | `str`   | `(50, 50)`  | Minimum face size (width, height) in pixels to be detected.                 |
| `--detection_confidence` | `float` | `0.8`       | Minimum confidence score for face detection.                                |
| `--face_detection_model` | `str`   | `hog`       | Face detection model to use: `hog` (faster, CPU) or `cnn` (accurate, GPU).  |
| `--no_preview`           | `flag`  | `False`     | If set, disables the real-time video preview window.                        |

---

## 📦 Dependencies

| Package           | Purpose                                   |
|-------------------|-------------------------------------------|
| `opencv-python`   | Computer vision, webcam access            |
| `face-recognition`| Face detection and recognition            |
| `numpy`           | Numerical operations                      |
| `dlib`            | Core library for `face-recognition`       |
| `Pillow`          | Image processing (dependency of `face-recognition`) |

---

## 🔧 Dlib Installation Tips

**If you encounter issues installing `dlib` (especially on Windows):**

1.  **Install CMake:**
    ```bash
    pip install cmake
    ```
2.  **Try installing `dlib` again:**
    ```bash
    pip install dlib
    ```
3.  **If that fails, use a pre-built `.whl` file:**
    *   Download a pre-built `.whl` file for your Python version from [Gohlke’s Unofficial Windows Binaries](https://www.lfd.uci.edu/~gohlke/pythonlibs/#dlib).
    *   Install the wheel using pip:
        ```bash
        pip install path/to/dlib‑<version>‑cp<python-version>‑cp<python-version>m‑win_amd64.whl
        ```

---

## ⚠️ Common Errors & Solutions

| Error Message                                   | Cause                          | Solution                                                                                 |
|-------------------------------------------------|--------------------------------|------------------------------------------------------------------------------------------|
| `fatal error: Python.h: No such file or directory` | Missing Python development headers | Linux: `sudo apt-get install build-essential cmake python3-dev`                          |
| `'cmake' is not recognized`                       | CMake not installed            | `pip install cmake` or install system-wide                                               |
| Compiler/CMake build failed                       | Missing build tools/config     | Use a pre-built `.whl` from Gohlke or trusted sources                                    |
| Persistent pip install errors                     | Dependency/conflict            | Try a `conda` environment or install from GitHub/master branch                             |
| `ModuleNotFoundError`                           | Missing package                | Ensure your virtual environment is activated and run `pip install -r requirements.txt`   |
| Camera not detected                             | Incorrect camera ID            | Try different `--camera_id` values (0, 1, 2, etc.) or check camera permissions.          |

---

## 🛡️ Disclaimer

This project stores face images locally. Use responsibly and ensure you have consent from all people being recorded.

---

## ❤️ Credits

Built with OpenCV, face_recognition, and Python by mighty-baseplate.
