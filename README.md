# 🛠️ Requirements

Install all dependencies using:
```bash
pip install -r requirements.txt
```
Or install them manually:
```bash
pip install opencv-python face-recognition numpy dlib
```

💡 **Note:** `face-recognition` depends on `dlib`, which can sometimes be tricky to install.

---

## 🔧 Dlib Installation Help (if issues occur)

If you're on Windows and encounter errors with `dlib`, try the following:

pip install cmake
pip install dlib

text

Or install from pre-built wheels (choose the `.whl` file matching your Python version and system):

👉 https://www.lfd.uci.edu/~gohlke/pythonlibs/#dlib

> **Tip:** Download the `.whl` file, navigate to its folder in your terminal, and run:
> 
> ```
> pip install dlib‑<version>‑cp<python-version>‑cp<python-version>m‑win_amd64.whl
> ```
> Replace `<version>` and `<python-version>` with your specific file details.

---
# ⚠️ Common Dlib Installation Errors & Fixes

---

## ❌ fatal error: Python.h: No such file or directory

This means your system is missing Python development headers.

**✅ Fix:** Install the necessary dev tools.

**Ubuntu/Debian:**
sudo apt-get install build-essential cmake python3-dev

text

**Windows:**
- This usually happens if CMake or a C++ compiler (like Visual Studio Build Tools) is not installed.

---

## ❌ 'cmake' is not recognized as an internal or external command

**✅ Fix:** Install cmake before installing dlib:

pip install cmake

text
- You may also need to install CMake system-wide or add it to your PATH on Windows.

---

## ❌ Compiler or CMake Build Failed

**✅ Fix:** Use a pre-built `.whl` file instead of compiling from source:

1. Visit: [https://www.lfd.uci.edu/~gohlke/pythonlibs/#dlib](https://www.lfd.uci.edu/~gohlke/pythonlibs/#dlib)
2. Download the `.whl` file that matches your Python version and system (e.g., `dlib‑19.24.0‑cp310‑cp310‑win_amd64.whl`).
3. Install it using pip:
    ```
    pip install path/to/your_downloaded_whl_file.whl
    ```

- For Python 3.13 and other recent versions, you can also find wheels on GitHub or other trusted sources. Example:
    ```
    pip install https://github.com/omwaman1/dlib-for-python3.13.2/releases/download/dlib/dlib-19.24.99-cp313-cp313-win_amd64.whl
    ```
    

---

## 💡 Additional Tips

- **Upgrade pip before installing dlib:**
    ```
    pip install --upgrade pip
    ```
    
- If you still encounter issues, try installing dlib from the master branch on GitHub or follow official compilation instructions.
- On cloud or Streamlit deployments, consider using `conda` instead of `pip` to avoid CMake and compilation issues. Create an `environment.yml` specifying dlib as a dependency for smoother installation.

---

## 📝 Summary Table

| Error Message                                   | Cause                          | Solution                                                                                 |
|-------------------------------------------------|--------------------------------|------------------------------------------------------------------------------------------|
| fatal error: Python.h: No such file or directory| Missing Python dev headers     | Install build tools: `sudo apt-get install build-essential cmake python3-dev` (Linux)     |
| 'cmake' is not recognized                       | CMake not installed            | `pip install cmake` or install CMake system-wide                                         |
| Compiler/CMake Build Failed                     | Missing tools or config issues | Use a pre-built `.whl` from Gohlke or trusted sources                                    |
| Persistent pip install errors                   | Dependency/conflict            | Try conda environment or install from GitHub/master branch                               |

---

> For more troubleshooting and platform-specific guides, refer to the [official dlib documentation](https://dlib.net/compile.html) and community forums.
---

# 🧠 How It Works

- Opens webcam and captures frames.
- Detects all faces in the frame.
- Encodes faces and checks against known people.
- If a new person is found:
  - Creates a folder for them.
  - Saves their face image.
- If known, saves new images only after a set time interval.

---

# 📁 Folder Structure

project/<br>
│<br>
├── database/ # Automatically created; stores person folders<br>
│ ├── Person_1/<br>
│ ├── Person_2/<br>
│ └── ...<br>
│<br>
├── person_tracker.py # Main script<br>
├── requirements.txt<br>
└── README.md<br>

---

# 🚀 Usage

Run the tracker directly:
```bash
python person_tracker.py
```


Then:

- Press `q` to quit the window.

---

# 📊 Customization

Modify these parameters in `SimplePersonTracker`:

- `update_interval`: Seconds to wait before saving another image of the same person
- `threshold`: Similarity threshold for matching
- `min_size`: Minimum face size to consider valid

---

# 📦 Dependencies

| Package           | Purpose                                   |
|-------------------|-------------------------------------------|
| OpenCV            | Computer vision and webcam access         |
| face_recognition  | Face detection and recognition            |
| numpy             | Numerical operations                      |
| dlib              | Underlying library for face_recognition   |

---

# 🛡️ Disclaimer

This project stores face images locally. Please use it responsibly and ensure you have consent from people being recorded.

---

# ❤️ Credits

Built with OpenCV, face_recognition, and Python by mighty-baseplate.