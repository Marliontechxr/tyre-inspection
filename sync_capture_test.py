#!/usr/bin/env python3
"""
Synchronized Capture Test
Plays the conveyor video and captures frames at optimal timestamps
to test motion blur and detection accuracy
"""

import cv2
import serial
import struct
import time
import numpy as np
import subprocess
import threading
import os

# Configuration
SERIAL_PORT = "/dev/cu.usbserial-0001"
BAUD_RATE = 921600
VIDEO_PATH = "/Users/marlionmac/Projects/tyre-inspection/test_conveyor.mp4"
OUTPUT_DIR = "/Users/marlionmac/Projects/tyre-inspection/capture_test"
TIMESTAMPS_FILE = "/Users/marlionmac/Projects/tyre-inspection/trigger_timestamps.txt"

# Frame markers
FRAME_START = bytes([0xFF, 0xAA, 0x55, 0xBB])
FRAME_END = bytes([0xFF, 0xBB, 0x55, 0xAA])

class CameraCapture:
    def __init__(self, port, baud):
        self.ser = serial.Serial(port, baud, timeout=2)
        time.sleep(1)
        self.ser.reset_input_buffer()
        
    def capture(self):
        """Capture a single frame"""
        self.ser.reset_input_buffer()
        self.ser.write(b'C')
        
        buffer = b''
        timeout = time.time() + 3
        
        # Wait for start marker
        while time.time() < timeout:
            if self.ser.in_waiting:
                buffer += self.ser.read(self.ser.in_waiting)
                start_idx = buffer.find(FRAME_START)
                if start_idx != -1:
                    buffer = buffer[start_idx:]
                    break
            time.sleep(0.001)
        
        if not buffer.startswith(FRAME_START):
            return None
        
        # Read header
        while len(buffer) < 8 and time.time() < timeout:
            if self.ser.in_waiting:
                buffer += self.ser.read(self.ser.in_waiting)
            time.sleep(0.001)
        
        frame_len = struct.unpack('<I', buffer[4:8])[0]
        total_needed = 8 + frame_len + 4
        
        # Read full frame
        while len(buffer) < total_needed and time.time() < timeout:
            if self.ser.in_waiting:
                buffer += self.ser.read(self.ser.in_waiting)
            time.sleep(0.001)
        
        if len(buffer) >= total_needed:
            return buffer[8:8+frame_len]
        return None
    
    def close(self):
        self.ser.close()

def analyze_frame(jpeg_data, expected):
    """Analyze captured frame for paint dot"""
    # Decode JPEG
    nparr = np.frombuffer(jpeg_data, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    if img is None:
        return {'error': 'decode_failed'}
    
    h, w = img.shape[:2]
    
    # Detect yellow/red paint dot
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    
    # Yellow mask
    yellow_mask = cv2.inRange(hsv, (15, 60, 60), (45, 255, 255))
    # Red mask
    red_mask1 = cv2.inRange(hsv, (0, 100, 100), (10, 255, 255))
    red_mask2 = cv2.inRange(hsv, (160, 100, 100), (180, 255, 255))
    red_mask = red_mask1 | red_mask2
    
    mask = yellow_mask | red_mask
    
    # Cleanup
    kernel = np.ones((5,5), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    result = {
        'image_size': f'{w}x{h}',
        'expected': expected,
        'dot_found': False,
        'verdict': 'NO_DOT',
        'correct': False
    }
    
    if contours:
        largest = max(contours, key=cv2.contourArea)
        area = cv2.contourArea(largest)
        
        if area > 50:  # Minimum area threshold
            perimeter = cv2.arcLength(largest, True)
            x, y, cw, ch = cv2.boundingRect(largest)
            
            circularity = 4 * np.pi * area / (perimeter ** 2) if perimeter > 0 else 0
            hull = cv2.convexHull(largest)
            hull_area = cv2.contourArea(hull)
            solidity = area / hull_area if hull_area > 0 else 0
            
            verdict = 'ACCEPT' if solidity >= 0.92 else 'REJECT'
            
            result.update({
                'dot_found': True,
                'dot_size': f'{cw}x{ch}',
                'area': int(area),
                'circularity': round(circularity, 3),
                'solidity': round(solidity, 3),
                'verdict': verdict,
                'correct': verdict == expected
            })
    
    # Handle 'none' dot type - should be REJECT
    if not result['dot_found'] and expected == 'REJECT':
        result['correct'] = True
        result['verdict'] = 'REJECT (no dot)'
    
    return result

def main():
    # Create output directory
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Load trigger timestamps
    triggers = []
    with open(TIMESTAMPS_FILE, 'r') as f:
        next(f)  # Skip header
        for line in f:
            parts = line.strip().split(',')
            triggers.append({
                'frame': int(parts[0]),
                'time_sec': float(parts[1]),
                'tyre_index': int(parts[2]),
                'dot_type': parts[3],
                'expected': parts[4]
            })
    
    # Deduplicate (keep first occurrence per tyre)
    seen_tyres = set()
    unique_triggers = []
    for t in triggers:
        if t['tyre_index'] not in seen_tyres:
            seen_tyres.add(t['tyre_index'])
            unique_triggers.append(t)
    triggers = unique_triggers
    
    print(f"Loaded {len(triggers)} capture triggers")
    print("=" * 70)
    
    # Connect to camera
    print("Connecting to ESP32-CAM...")
    try:
        camera = CameraCapture(SERIAL_PORT, BAUD_RATE)
        camera.ser.write(b'S')
        time.sleep(0.3)
        status = camera.ser.read(camera.ser.in_waiting).decode('utf-8', errors='ignore')
        print(f"Camera status: {status.strip()}")
    except Exception as e:
        print(f"ERROR: Could not connect to camera: {e}")
        print("\nManual test mode - will analyze pre-captured frames")
        camera = None
    
    print("\n" + "=" * 70)
    print("INSTRUCTIONS:")
    print("1. Open the video in a player: open test_conveyor.mp4")
    print("2. Position ESP32-CAM pointing at your screen")
    print("3. Press ENTER to start synchronized capture test")
    print("=" * 70)
    
    input("\nPress ENTER when ready...")
    
    # Start video playback
    print("\nStarting video playback...")
    video_process = subprocess.Popen(
        ['open', VIDEO_PATH],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    
    # Wait for video to start
    time.sleep(1.5)
    
    start_time = time.time()
    results = []
    
    print("\nCapturing at trigger points...")
    print("-" * 70)
    
    for trigger in triggers:
        # Wait until trigger time
        target_time = trigger['time_sec']
        while time.time() - start_time < target_time:
            time.sleep(0.001)
        
        capture_time = time.time() - start_time
        print(f"\n⏱ Trigger at {target_time:.2f}s (actual: {capture_time:.2f}s)")
        print(f"  Tyre {trigger['tyre_index']}: {trigger['dot_type']} - Expected: {trigger['expected']}")
        
        if camera:
            # Capture frame
            jpeg_data = camera.capture()
            
            if jpeg_data:
                # Save frame
                filename = f"{OUTPUT_DIR}/tyre_{trigger['tyre_index']}_{trigger['dot_type']}.jpg"
                with open(filename, 'wb') as f:
                    f.write(jpeg_data)
                
                # Analyze
                result = analyze_frame(jpeg_data, trigger['expected'])
                result['trigger'] = trigger
                results.append(result)
                
                status = "✅" if result['correct'] else "❌"
                print(f"  {status} Captured: {result.get('dot_size', 'N/A')} | "
                      f"Solidity: {result.get('solidity', 'N/A')} | "
                      f"Verdict: {result['verdict']}")
            else:
                print("  ⚠️ Capture failed")
                results.append({'trigger': trigger, 'error': 'capture_failed', 'correct': False})
        else:
            print("  (Camera not connected - skipping capture)")
    
    # Summary
    print("\n" + "=" * 70)
    print("RESULTS SUMMARY")
    print("=" * 70)
    
    if results:
        correct = sum(1 for r in results if r.get('correct', False))
        total = len(results)
        accuracy = correct / total * 100 if total > 0 else 0
        
        print(f"Accuracy: {correct}/{total} = {accuracy:.1f}%")
        print("\nDetailed results:")
        for r in results:
            t = r.get('trigger', {})
            status = "✅" if r.get('correct') else "❌"
            print(f"  {status} Tyre {t.get('tyre_index', '?')}: "
                  f"{t.get('dot_type', '?'):10s} | "
                  f"Expected: {t.get('expected', '?'):6s} | "
                  f"Got: {r.get('verdict', 'ERROR'):6s} | "
                  f"Solidity: {r.get('solidity', 'N/A')}")
    
    if camera:
        camera.close()
    
    print(f"\nCaptured frames saved to: {OUTPUT_DIR}/")

if __name__ == "__main__":
    main()
