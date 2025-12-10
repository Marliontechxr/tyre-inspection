# Tyre Paint Dot Inspection System - Pi 5 Build Prompt

## Quick Start for Copilot CLI on Raspberry Pi 5

Pull this repo and run Copilot CLI with the prompt below.

---

## System Overview

**Purpose:** Real-time tyre paint dot defect detection with:
- ESP32-CAM for image capture
- Ultrasonic sensor for tyre detection
- Fingerprint sensor for user authentication
- Firebase for real-time data logging
- Next.js dashboard for analytics and control
- PLC GPIO output for accept/reject

---

## Hardware Connected to Pi 5

| Device | Connection | Pins/Port |
|--------|------------|-----------|
| ESP32-CAM | USB Serial (TTL adapter) | /dev/ttyUSB0 @ 921600 baud |
| HC-SR04 Ultrasonic | GPIO | TRIG=GPIO17, ECHO=GPIO27 (with voltage divider) |
| Fingerprint (R307/AS608) | UART | /dev/ttyAMA0 or USB |
| PLC Output | GPIO | ACCEPT=GPIO22, REJECT=GPIO23 |
| Ring Light | Always ON | External power |

---

## Pre-installed ESP32-CAM Firmware

The ESP32-CAM is already flashed with custom firmware:

**Commands:**
- `C` → Capture frame (returns JPEG with markers)
- `S` → Status check → `STATUS:OK`
- `F` → Fast exposure (anti-blur, needs bright light)
- `A` → Auto exposure (normal)

**Frame Protocol:**
```
[0xFF 0xAA 0x55 0xBB][4-byte length LE][JPEG data][0xFF 0xBB 0x55 0xAA]
```

---

## Copilot CLI Prompt

```
Build a tyre paint dot inspection system for Raspberry Pi 5 with the following components:

## 1. Python Backend (FastAPI)

### Camera Module (ESP32-CAM)
- Serial port: /dev/ttyUSB0 at 921600 baud
- Keep serial connection open between captures for speed
- Send 'C' to capture, parse response:
  - Start marker: 0xFF 0xAA 0x55 0xBB
  - 4-byte little-endian length
  - JPEG data
  - End marker: 0xFF 0xBB 0x55 0xAA
- Send 'F' on startup for fast exposure mode

### Detection Algorithm (OpenCV)
- Convert to HSV
- Yellow mask: H=15-45, S=60-255, V=60-255
- Red mask: H=0-10 + H=160-180, S=100-255, V=100-255
- Morphological cleanup: 5x5 kernel, close then open
- Find largest contour
- Calculate solidity = contour_area / convex_hull_area
- Threshold: solidity >= 0.92 → ACCEPT, else REJECT

### Ultrasonic Sensor (HC-SR04)
- TRIG: GPIO 17
- ECHO: GPIO 27 (5V→3.3V via voltage divider)
- Tyre detected when distance < 30cm
- Baseline (empty belt): ~50cm

### State Machine
- WAITING: Monitor ultrasonic, trigger on tyre detection
- TRIGGERED: Capture image, analyze, send PLC signal, log to Firebase
- COOLDOWN: 2 second wait, return to WAITING when tyre exits

### PLC Output
- GPIO 22: Accept signal (100ms pulse)
- GPIO 23: Reject signal (100ms pulse)

### Fingerprint Sensor (R307 or AS608)
- UART connection: /dev/ttyAMA0 or /dev/ttyUSB1
- Use pyfingerprint or adafruit-circuitpython-fingerprint library
- Operations requiring auth: Start/Stop inspection, change threshold, delete logs
- Store authorized fingerprint IDs in Firebase

### Firebase Integration
- Use firebase-admin SDK
- Real-time logging to Firestore collection 'inspections':
  {
    timestamp: server_timestamp,
    verdict: 'ACCEPT' | 'REJECT',
    solidity: float,
    tyre_number: int,
    operator_id: string (from fingerprint),
    image_url: string (optional, store in Firebase Storage)
  }
- Store system config in 'config' document:
  {
    solidity_threshold: 0.92,
    cooldown_seconds: 2,
    inspection_running: boolean
  }
- Listen to config changes to update parameters in real-time

### API Endpoints (FastAPI)
- GET /status - System status, stats
- POST /start - Start inspection (requires fingerprint)
- POST /stop - Stop inspection (requires fingerprint)
- POST /capture - Manual capture for testing
- GET /stats - Current session statistics
- POST /calibrate - Update threshold (requires fingerprint)
- POST /fingerprint/enroll - Enroll new fingerprint
- POST /fingerprint/verify - Verify fingerprint

## 2. Next.js Dashboard

### Pages
- / (Dashboard): Real-time stats, accept/reject counts, current status
- /history: Paginated inspection history with filters
- /analytics: Charts (hourly/daily rates, defect trends)
- /settings: Threshold adjustment, system config
- /operators: Manage authorized fingerprints

### Real-time Features
- Firestore onSnapshot listeners for live updates
- WebSocket or polling to Pi backend for immediate status
- Toast notifications on inspection events

### Authentication
- Firebase Auth for dashboard login
- Role-based access (admin, operator, viewer)

### UI Components
- Large accept/reject counters
- Solidity gauge/meter
- Live camera preview (optional)
- Start/Stop button with fingerprint prompt
- Threshold slider with live preview
- Export data to CSV

### Tech Stack
- Next.js 14 with App Router
- Tailwind CSS
- shadcn/ui components
- Firebase JS SDK
- Recharts for analytics

## 3. File Structure

```
/home/pi/tyre-inspection/
├── backend/
│   ├── main.py              # FastAPI app
│   ├── camera.py            # ESP32-CAM communication
│   ├── detector.py          # OpenCV detection
│   ├── ultrasonic.py        # HC-SR04 driver
│   ├── fingerprint.py       # Fingerprint sensor
│   ├── plc.py               # GPIO output
│   ├── firebase_client.py   # Firebase integration
│   ├── state_machine.py     # Inspection state machine
│   ├── config.py            # Configuration
│   └── requirements.txt
├── dashboard/
│   ├── app/
│   │   ├── page.tsx         # Main dashboard
│   │   ├── history/
│   │   ├── analytics/
│   │   ├── settings/
│   │   └── operators/
│   ├── components/
│   ├── lib/
│   │   └── firebase.ts
│   ├── package.json
│   └── tailwind.config.js
├── firebase/
│   ├── serviceAccountKey.json  # Firebase admin credentials
│   └── firestore.rules
├── systemd/
│   └── tyre-inspector.service  # Auto-start on boot
└── README.md
```

## 4. Installation Commands

```bash
# System packages
sudo apt update
sudo apt install python3-pip python3-opencv python3-dev libffi-dev

# Python dependencies
pip3 install fastapi uvicorn pyserial firebase-admin RPi.GPIO pyfingerprint opencv-python-headless numpy

# Node.js for dashboard (if running on Pi)
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install nodejs

# Or deploy dashboard to Vercel and access remotely
```

## 5. Firebase Setup

1. Create Firebase project at console.firebase.google.com
2. Enable Firestore Database
3. Enable Authentication (Email/Password)
4. Generate service account key (Project Settings → Service Accounts)
5. Save as firebase/serviceAccountKey.json
6. Set Firestore rules for security

## 6. Systemd Service

Create /etc/systemd/system/tyre-inspector.service:
```ini
[Unit]
Description=Tyre Inspection System
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/tyre-inspection/backend
ExecStart=/usr/bin/python3 main.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable: sudo systemctl enable tyre-inspector

## 7. Performance Targets

- Capture + Transfer: < 200ms
- Detection: < 10ms
- Total cycle: < 250ms
- Supports: 60+ tyres/min

## 8. Testing Checklist

- [ ] ESP32-CAM responds to 'S' command
- [ ] Ultrasonic reads distance correctly
- [ ] Fingerprint sensor enrolls and verifies
- [ ] GPIO outputs toggle correctly
- [ ] Firebase writes inspection records
- [ ] Dashboard shows real-time updates
- [ ] Start/Stop requires fingerprint
- [ ] Threshold changes apply immediately
```

---

## Environment Variables

Create `.env` in backend/:
```
FIREBASE_CREDENTIALS=/home/pi/tyre-inspection/firebase/serviceAccountKey.json
SERIAL_PORT=/dev/ttyUSB0
SERIAL_BAUD=921600
FINGERPRINT_PORT=/dev/ttyAMA0
```

---

## Sample Firebase Document Structure

### inspections (collection)
```json
{
  "id": "auto-generated",
  "timestamp": "2025-12-11T10:30:00Z",
  "verdict": "ACCEPT",
  "solidity": 0.947,
  "tyre_number": 1542,
  "operator_id": "fp_001",
  "operator_name": "John Doe",
  "session_id": "session_abc123",
  "image_url": "gs://bucket/images/1542.jpg"
}
```

### config (document)
```json
{
  "solidity_threshold": 0.92,
  "cooldown_seconds": 2,
  "inspection_running": true,
  "current_session_id": "session_abc123",
  "started_at": "2025-12-11T08:00:00Z",
  "started_by": "fp_001"
}
```

### operators (collection)
```json
{
  "fingerprint_id": "fp_001",
  "name": "John Doe",
  "role": "operator",
  "enrolled_at": "2025-12-01T09:00:00Z",
  "enrolled_by": "admin"
}
```

---

## Notes

1. The ESP32-CAM firmware is already flashed - do not reflash unless needed
2. Ring light should be ON and bright for fast exposure mode to work
3. Ultrasonic ECHO needs voltage divider (1kΩ + 2kΩ) for 5V→3.3V
4. Test fingerprint sensor separately before integrating
5. Dashboard can run on Pi (localhost:3000) or deploy to Vercel for remote access
