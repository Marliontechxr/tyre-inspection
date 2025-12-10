#!/usr/bin/env python3
"""
Manual Capture Test - You control the video, press ENTER to capture
"""

import serial
import struct
import time
import numpy as np
import cv2
import os

SERIAL_PORT = "/dev/cu.usbserial-0001"
BAUD_RATE = 921600
OUTPUT_DIR = "/Users/marlionmac/Projects/tyre-inspection/capture_test"
FRAME_START = bytes([0xFF, 0xAA, 0x55, 0xBB])
FRAME_END = bytes([0xFF, 0xBB, 0x55, 0xAA])

os.makedirs(OUTPUT_DIR, exist_ok=True)

def capture_frame(ser):
    ser.reset_input_buffer()
    ser.write(b'C')
    
    buffer = b''
    timeout = time.time() + 3
    
    while time.time() < timeout:
        if ser.in_waiting:
            buffer += ser.read(ser.in_waiting)
            start_idx = buffer.find(FRAME_START)
            if start_idx != -1:
                buffer = buffer[start_idx:]
                break
        time.sleep(0.001)
    
    if not buffer.startswith(FRAME_START):
        return None
    
    while len(buffer) < 8 and time.time() < timeout:
        if ser.in_waiting:
            buffer += ser.read(ser.in_waiting)
        time.sleep(0.001)
    
    frame_len = struct.unpack('<I', buffer[4:8])[0]
    total_needed = 8 + frame_len + 4
    
    while len(buffer) < total_needed and time.time() < timeout:
        if ser.in_waiting:
            buffer += ser.read(ser.in_waiting)
        time.sleep(0.001)
    
    if len(buffer) >= total_needed:
        return buffer[8:8+frame_len]
    return None

def analyze(jpeg_data):
    nparr = np.frombuffer(jpeg_data, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if img is None:
        return None
    
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    yellow_mask = cv2.inRange(hsv, (15, 60, 60), (45, 255, 255))
    red_mask1 = cv2.inRange(hsv, (0, 100, 100), (10, 255, 255))
    red_mask2 = cv2.inRange(hsv, (160, 100, 100), (180, 255, 255))
    mask = yellow_mask | red_mask1 | red_mask2
    
    kernel = np.ones((5,5), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    if not contours:
        return {'found': False, 'verdict': 'NO DOT'}
    
    largest = max(contours, key=cv2.contourArea)
    area = cv2.contourArea(largest)
    if area < 50:
        return {'found': False, 'verdict': 'NO DOT'}
    
    perimeter = cv2.arcLength(largest, True)
    hull = cv2.convexHull(largest)
    hull_area = cv2.contourArea(hull)
    solidity = area / hull_area if hull_area > 0 else 0
    x, y, w, h = cv2.boundingRect(largest)
    
    verdict = 'ACCEPT ✅' if solidity >= 0.92 else 'REJECT ❌'
    
    return {
        'found': True,
        'size': f'{w}x{h}',
        'area': int(area),
        'solidity': round(solidity, 3),
        'verdict': verdict
    }

def main():
    print("=" * 60)
    print("MANUAL CAPTURE TEST")
    print("=" * 60)
    print("\nInstructions:")
    print("1. Play the video: open test_conveyor.mp4")
    print("2. Point camera at screen")
    print("3. Press ENTER when a tyre is centered to capture")
    print("4. Type 'q' + ENTER to quit")
    print("=" * 60)
    
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=2)
    time.sleep(1)
    print(f"\n✅ Camera connected\n")
    
    capture_num = 0
    
    while True:
        user_input = input(f"\n[Capture #{capture_num + 1}] Press ENTER to capture (or 'q' to quit): ")
        
        if user_input.lower() == 'q':
            break
        
        print("  Capturing...")
        jpeg_data = capture_frame(ser)
        
        if jpeg_data:
            # Save
            filename = f"{OUTPUT_DIR}/manual_{capture_num:02d}.jpg"
            with open(filename, 'wb') as f:
                f.write(jpeg_data)
            
            # Analyze
            result = analyze(jpeg_data)
            
            if result['found']:
                print(f"  📷 Saved: {filename}")
                print(f"  📐 Size: {result['size']} | Area: {result['area']}px²")
                print(f"  📊 Solidity: {result['solidity']}")
                print(f"  🎯 {result['verdict']}")
            else:
                print(f"  ⚠️ No paint dot detected in frame")
            
            capture_num += 1
        else:
            print("  ❌ Capture failed")
    
    ser.close()
    print(f"\n✅ Done! {capture_num} frames saved to {OUTPUT_DIR}/")

if __name__ == "__main__":
    main()
