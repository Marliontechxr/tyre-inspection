# ESP32-CAM Firmware for Tyre Paint Dot Inspection

## Customizations for Your Use Case

### 1. Triggered Mode (Default)
The firmware uses **triggered capture** - the Pi sends a command, ESP32 captures and returns one frame. This is optimal for:
- Conveyor belt inspection (capture when tyre detected)
- Low bandwidth usage
- Synchronized with ultrasonic trigger

### 2. Frame Protocol
```
[START: FF AA 55 BB][LENGTH: 4 bytes][JPEG DATA][END: FF BB 55 AA]
```
This ensures reliable frame parsing even with serial noise.

### 3. Camera Settings Optimized For
- Ring light illumination
- Yellow/Red paint dot color detection
- Fast exposure for moving tyres

---

## Flashing Instructions (Mac Mini)

### Step 1: Install Arduino IDE
Download from: https://www.arduino.cc/en/software

### Step 2: Add ESP32 Board Support
1. Open Arduino IDE
2. Go to `File → Preferences`
3. Add this URL to "Additional Board Manager URLs":
   ```
   https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json
   ```
4. Go to `Tools → Board → Boards Manager`
5. Search "esp32" and install **ESP32 by Espressif Systems**

### Step 3: Select Board
1. `Tools → Board → ESP32 Arduino → AI Thinker ESP32-CAM`

### Step 4: Wire for Flashing
```
ESP32-CAM              TTL-USB Adapter
─────────              ───────────────
   GND  ──────────────  GND
   5V   ──────────────  VCC (5V)
   U0T  ──────────────  RXD
   U0R  ──────────────  TXD
  GPIO0 ──────────────  GND   ← CRITICAL: Connect only during upload!
```

### Step 5: Upload
1. Open `tyre_cam_firmware.ino`
2. Select port: `Tools → Port → /dev/cu.usbserial-XXXX`
3. Click Upload (→ button)
4. When you see "Connecting...", press the RESET button on ESP32-CAM
5. Wait for "Done uploading"

### Step 6: Disconnect GPIO0
**IMPORTANT:** Remove the GPIO0-to-GND wire after flashing!

### Step 7: Test
1. Open Serial Monitor (`Tools → Serial Monitor`)
2. Set baud rate to `921600`
3. You should see: `STATUS:READY`
4. Type `C` and press Enter - should receive JPEG data
5. Type `S` - should see `STATUS:OK`

---

## Commands Reference

| Command | Response | Description |
|---------|----------|-------------|
| `C` | Frame data | Capture and send JPEG frame |
| `S` | `STATUS:OK` | Health check |
| `R` | `RESOLUTION:QVGA` | Switch to 320x240 |
| `V` | `RESOLUTION:VGA` | Switch to 640x480 |
| `L` | `LED:ON` | Turn on flash LED (for alignment) |
| `O` | `LED:OFF` | Turn off flash LED |
| `F` | `EXPOSURE:FAST` | Fast exposure ~5ms (anti-blur, needs bright light!) |
| `M` | `EXPOSURE:MEDIUM` | Medium exposure ~15ms (balanced) |
| `A` | `EXPOSURE:AUTO` | Auto exposure (normal mode) |

---

## Exposure Modes (Anti-Motion Blur)

| Mode | Exposure | Use When |
|------|----------|----------|
| **Fast (F)** | ~5ms | Conveyor moving, bright ring light |
| **Medium (M)** | ~15ms | Slower conveyor, moderate light |
| **Auto (A)** | Variable | Stationary objects, testing |

**Default on boot:** Fast mode (factory optimized)

---

## Configuration Options

Edit these in the firmware if needed:

```cpp
// Speed vs reliability tradeoff
#define SERIAL_BAUD 921600      // Use 115200 if you see corruption

// Resolution vs speed tradeoff  
#define FRAME_SIZE FRAMESIZE_QVGA   // QVGA=fast, VGA=detailed

// Quality vs size tradeoff
#define JPEG_QUALITY 12         // 10=best quality, 63=smallest size

// Capture mode
#define CAPTURE_MODE_TRIGGERED true  // true=on-demand, false=continuous
```

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| "Connecting..." stuck | Press RESET button, ensure GPIO0 is grounded |
| Upload fails | Try lower baud rate (115200) in Tools menu |
| No serial output | Check GPIO0 is NOT connected to GND |
| Garbled output | Match baud rate in Serial Monitor (921600) |
| Camera init failed | Check power (needs 5V, not 3.3V) |
| Dark images | Ring light not on, or adjust exposure settings |

---

## Moving to Raspberry Pi 5

After flashing, disconnect from Mac and connect to Pi:

```bash
# On Pi 5, check connection
ls /dev/ttyUSB*   # Should show /dev/ttyUSB0

# Quick test
stty -F /dev/ttyUSB0 921600
echo "S" > /dev/ttyUSB0
cat /dev/ttyUSB0   # Should see STATUS:OK
```
