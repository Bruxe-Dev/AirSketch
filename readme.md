# Gesture Control System

A Python-based hand gesture recognition system that uses your webcam to track hand movements and control a virtual desktop environment. Perfect for testing gesture controls before deploying to real system control.

## 🌟 Features

- **Real-time Hand Tracking**: Uses MediaPipe for accurate hand landmark detection
- **Multiple Gesture Recognition**:
  - ✋ Point with index finger to move cursor
  - 🤏 Pinch to click/drag windows
  - 👋 Swipe (with open hand) to move windows
  - 👊 Push (toward camera) to enlarge windows
  - ✊ Pull (away from camera) to shrink windows
- **Virtual Desktop Testing Environment**: Safe testing environment with draggable windows
- **Modular Architecture**: Easy to extend with new gestures or real system controls

## 📋 Prerequisites

- Python 3.8 or higher
- Webcam (built-in or external USB)
- Operating System: Windows, macOS, or Linux

## 🚀 Installation

### Step 1: Clone or Download the Project

If you have this folder, navigate to it:
```bash
cd gesture_control
```

### Step 2: Create Virtual Environment (Recommended)

```bash
# Create virtual environment
python -m venv venv

# Activate it
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

This will install:
- **OpenCV**: For webcam access and image processing
- **MediaPipe**: Google's hand tracking library (v0.10.30+)
- **NumPy**: For numerical computations

**Note:** On first run, the app will automatically download the hand landmark model (~10MB). This is a one-time download.

## 🎮 Usage

### Running the Application

```bash
python main.py
```

### Controls

**Hand Gestures:**
- **Point** (index finger extended): Move the cursor around the virtual desktop
- **Pinch** (thumb + index finger together): Click and drag windows by their title bar
- **Open Hand + Swipe**: Move the active window in the swipe direction
- **Push** (move hand toward camera): Enlarge the active window
- **Pull** (move hand away from camera): Shrink the active window

**Keyboard Shortcuts:**
- `c`: Toggle camera view on/off
- `r`: Reset all windows to default positions
- `q`: Quit the application

## 📁 Project Structure

```
gesture_control/
│
├── main.py                    # Main application entry point
├── hand_tracker.py           # Hand tracking with MediaPipe
├── gesture_recognizer.py     # Gesture pattern recognition
├── virtual_desktop.py        # Virtual desktop UI simulation
├── requirements.txt          # Python dependencies
└── README.md                 # This file
```

## 🔧 How It Works

### 1. Hand Tracker (`hand_tracker.py`)

The `HandTracker` class uses MediaPipe's new Tasks API to detect and track hand landmarks:

```python
tracker = HandTracker(max_hands=1)
frame = tracker.find_hands(frame, draw=True)
finger_pos = tracker.get_finger_tip_position()
is_pinching = tracker.is_pinching()
fingers_up = tracker.count_fingers_up()
```

**Key Methods:**
- `find_hands()`: Detects hands in the webcam frame using MediaPipe Tasks API
- `get_finger_tip_position()`: Returns (x, y) coordinates of index finger tip
- `is_pinching()`: Checks if thumb and index finger are close together
- `count_fingers_up()`: Counts how many fingers are extended
- `get_all_landmarks()`: Returns all 21 hand landmarks

**Note:** This version uses MediaPipe 0.10.30+ which requires the Tasks API instead of the deprecated Solutions API.

### 2. Gesture Recognizer (`gesture_recognizer.py`)

The `GestureRecognizer` analyzes position history to identify gestures:

```python
recognizer = GestureRecognizer(history_size=10)
recognizer.update(finger_pos)

# Detect gestures
direction = recognizer.detect_swipe()  # Returns 'left', 'right', 'up', 'down'
is_push = recognizer.detect_push()     # Returns True if pushing
is_pull = recognizer.detect_pull()     # Returns True if pulling
```

**Key Features:**
- Tracks position history over time
- Detects directional swipes based on movement patterns
- Identifies push/pull gestures (Z-axis approximation)
- Includes cooldown to prevent rapid re-triggering

### 3. Virtual Desktop (`virtual_desktop.py`)

Simulates a desktop environment for safe testing:

```python
desktop = VirtualDesktop(width=1280, height=720)
desktop.handle_cursor(x, y, is_pinching)
desktop.handle_swipe('left')
desktop_frame = desktop.render()
```

**Features:**
- Multiple draggable windows
- Taskbar showing all windows
- Window activation and focus
- Status messages for user feedback

## 🎯 Understanding the Code Flow

### Main Loop (`main.py`)

```python
while running:
    # 1. Capture webcam frame
    ret, frame = cap.read()
    frame = cv2.flip(frame, 1)  # Mirror for natural interaction
    
    # 2. Process hand tracking
    frame = hand_tracker.find_hands(frame)
    finger_pos = hand_tracker.get_finger_tip_position()
    
    # 3. Update gesture recognizer
    gesture_recognizer.update(finger_pos)
    
    # 4. Map webcam coords to desktop coords
    desktop_x = (finger_pos[0] / 640) * 1280
    desktop_y = (finger_pos[1] / 480) * 720
    
    # 5. Handle interactions
    is_pinching = hand_tracker.is_pinching()
    virtual_desktop.handle_cursor(desktop_x, desktop_y, is_pinching)
    
    # 6. Detect and handle gestures
    if hand_tracker.count_fingers_up() == 5:  # Open hand
        direction = gesture_recognizer.detect_swipe()
        if direction:
            virtual_desktop.handle_swipe(direction)
    
    # 7. Render and display
    desktop_frame = virtual_desktop.render()
    cv2.imshow("Virtual Desktop", desktop_frame)
```

## 🔍 Key Concepts Explained

### Hand Landmarks

MediaPipe detects 21 landmarks on each hand:
- **0**: Wrist
- **4**: Thumb tip
- **8**: Index finger tip
- **12**: Middle finger tip
- **16**: Ring finger tip
- **20**: Pinky tip

### Gesture Detection Algorithm

**Pinch Detection:**
```python
# Calculate distance between thumb tip (4) and index tip (8)
distance = sqrt((thumb_x - index_x)² + (thumb_y - index_y)²)
is_pinching = distance < threshold  # threshold = 40 pixels
```

**Swipe Detection:**
```python
# Track last 10 positions
# Calculate total displacement
dx = end_x - start_x
dy = end_y - start_y

# Determine primary direction
if |dx| > |dy|:
    direction = 'right' if dx > 0 else 'left'
else:
    direction = 'down' if dy > 0 else 'up'
```

## 🚀 Next Steps: Real System Control

After testing with the virtual desktop, you can extend to real system control:

### Option 1: Mouse Control (Cross-platform)
```python
import pyautogui

# In your main loop, replace virtual_desktop.handle_cursor with:
pyautogui.moveTo(desktop_x, desktop_y)
if is_pinching:
    pyautogui.click()
```

### Option 2: Keyboard Control
```python
import pyautogui

# Trigger keyboard shortcuts with gestures
if gesture == 'swipe_left':
    pyautogui.hotkey('alt', 'tab')
```

### Option 3: Application Control
```python
# Control specific applications
if gesture == 'push':
    os.system('open -a "Music"')  # macOS
    # or
    subprocess.run(['start', 'spotify'], shell=True)  # Windows
```

## 🐛 Troubleshooting

### Camera Not Working
```python
# Try different camera IDs
app = GestureControlApp(camera_id=1)  # or 2, 3, etc.
```

### Hand Not Detected
- Ensure good lighting
- Keep hand within frame
- Adjust detection confidence:
```python
tracker = HandTracker(
    min_detection_confidence=0.5,  # Lower for easier detection
    min_tracking_confidence=0.3
)
```

### Gestures Too Sensitive
```python
# Increase thresholds
recognizer.detect_swipe(threshold=150)  # Default is 100
recognizer.detect_push(threshold=200)   # Default is 150
```

### Performance Issues
- Reduce camera resolution
- Lower max_hands to 1
- Disable camera preview with 'c' key

## 📚 Learning Resources

- **MediaPipe Hands**: https://google.github.io/mediapipe/solutions/hands.html
- **OpenCV Python**: https://docs.opencv.org/4.x/d6/d00/tutorial_py_root.html
- **NumPy**: https://numpy.org/doc/stable/

## 🤝 Contributing Ideas
**Next improvement steps:** 

1. Add more gestures (peace sign, thumbs up, etc.)
2. Multi-hand support for advanced controls
3. Gesture customization UI
4. Voice command integration
5. Record and playback gesture macros
6. Integration with smart home devices

## 📝 License

This project is provided as-is for educational purposes.

## 💡 Tips for Best Results

1. **Lighting**: Use good, even lighting for best hand detection
2. **Background**: Plain backgrounds work better than cluttered ones
3. **Distance**: Keep your hand 1-2 feet from the camera
4. **Calibration**: Spend a minute getting used to the cursor mapping
5. **Gestures**: Make deliberate, clear gestures - not too fast or slow

---

Happy gesture controlling! 🎉