## Face Recognition Person Tracker

A simple Python tool for real-time face recognition and automatic image collection using your webcam.

---

## 🛠️ Installation

**Install all dependencies with:**
```
pip install -r requirements.txt
```

Or manually:
```
pip install opencv-python face-recognition numpy dlib
```

> **Note:** `face-recognition` depends on `dlib`, which can be tricky to install on some systems.

---

## 🧠 How It Works

- Opens your webcam and captures frames in real time.
- Detects all faces in each frame.
- Encodes faces and compares them to known people.
- For new faces:
  - Creates a folder for the person.
  - Saves their face image.
- For recognized faces:
  - Saves a new image only after a set time interval.

---

## 📁 Project Structure

project/<br>
│<br>
├── database/ # Auto-created; stores folders for each person<br>
│ ├── Person_1/<br>
│ ├── Person_2/<br>
│ └── ...<br>
│<br>
├── person_tracker.py # Main script<br>
├── requirements.txt<br>
└── README.md<br>



---

## 🚀 Usage

Run the tracker:
```
python person_tracker.py
```

- Press `q` to quit.

---

## ⚙️ Customization

Edit these parameters in `SimplePersonTracker`:

- `update_interval`: Seconds to wait before saving a new image of the same person.
- `threshold`: Similarity threshold for face matching.
- `min_size`: Minimum face size (in pixels) to consider valid.

---

## 📦 Dependencies

| Package           | Purpose                                   |
|-------------------|-------------------------------------------|
| OpenCV            | Computer vision, webcam access            |
| face_recognition  | Face detection and recognition            |
| numpy             | Numerical operations                      |
| dlib              | Core library for face_recognition         |

---

## 🔧 Dlib Installation Tips

**If you get errors installing `dlib` on Windows:**
1. Install CMake:
    ```
    pip install cmake
    ```
2. Install dlib:
    ```
    pip install dlib
    ```
3. If that fails, download a pre-built `.whl` file for your Python version from:
   - [Gohlke’s Unofficial Windows Binaries](https://www.lfd.uci.edu/~gohlke/pythonlibs/#dlib)
4. Install the wheel:
    ```
    pip install path/to/dlib‑<version>‑cp<python-version>‑cp<python-version>m‑win_amd64.whl
    ```

---

## ⚠️ Common Installation Errors & Solutions

| Error Message                                   | Cause                          | Solution                                                                                 |
|-------------------------------------------------|--------------------------------|------------------------------------------------------------------------------------------|
| `fatal error: Python.h: No such file or directory` | Missing Python dev headers     | Linux: `sudo apt-get install build-essential cmake python3-dev`                          |
| `'cmake' is not recognized`                       | CMake not installed            | `pip install cmake` or install system-wide                                               |
| Compiler/CMake build failed                       | Missing tools/config           | Use a pre-built `.whl` from Gohlke or trusted sources                                    |
| Persistent pip install errors                     | Dependency/conflict            | Try a conda environment or install from GitHub/master branch                             |

**Tips:**
- Upgrade pip before installing:
    ```
    pip install --upgrade pip
    ```
- On cloud/Streamlit, consider using `conda` to avoid compilation issues.

---

## 🛡️ Disclaimer

This project stores face images locally. Use responsibly and ensure you have consent from all people being recorded.

---

## ❤️ Credits

Built with OpenCV, face_recognition, and Python by mighty-baseplate.

---

> For more troubleshooting, see the [official dlib documentation](https://dlib.net/compile.html) and community forums.