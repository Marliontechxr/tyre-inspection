#!/usr/bin/env python3
"""
ESP32-CAM Test Script - Capture and display image
Run this on your Mac to test the camera before moving to Pi
"""

import serial
import struct
import time
import os

# Configuration
SERIAL_PORT = "/dev/cu.usbserial-0001"  # Mac port
BAUD_RATE = 921600
OUTPUT_FILE = "/Users/marlionmac/Projects/tyre-inspection/test_capture.jpg"

# Frame markers (must match firmware)
FRAME_START = bytes([0xFF, 0xAA, 0x55, 0xBB])
FRAME_END = bytes([0xFF, 0xBB, 0x55, 0xAA])

def capture_frame(ser):
    """Send capture command and receive JPEG frame"""
    
    # Clear any pending data
    ser.reset_input_buffer()
    
    # Send capture command
    ser.write(b'C')
    print("Sent capture command...")
    
    # Wait for start marker
    buffer = b''
    timeout = time.time() + 5  # 5 second timeout
    
    while time.time() < timeout:
        if ser.in_waiting:
            buffer += ser.read(ser.in_waiting)
            
            # Look for start marker
            start_idx = buffer.find(FRAME_START)
            if start_idx != -1:
                buffer = buffer[start_idx:]
                break
        time.sleep(0.01)
    
    if not buffer.startswith(FRAME_START):
        print("ERROR: Start marker not found")
        return None
    
    print("Found start marker...")
    
    # Read until we have at least header (4 start + 4 length = 8 bytes)
    while len(buffer) < 8 and time.time() < timeout:
        if ser.in_waiting:
            buffer += ser.read(ser.in_waiting)
        time.sleep(0.01)
    
    # Extract frame length
    frame_len = struct.unpack('<I', buffer[4:8])[0]
    print(f"Frame size: {frame_len} bytes")
    
    # Read the full frame + end marker
    total_needed = 8 + frame_len + 4  # start + length + data + end
    
    while len(buffer) < total_needed and time.time() < timeout:
        if ser.in_waiting:
            buffer += ser.read(ser.in_waiting)
        time.sleep(0.01)
    
    if len(buffer) < total_needed:
        print(f"ERROR: Incomplete frame. Got {len(buffer)}, expected {total_needed}")
        return None
    
    # Extract JPEG data
    jpeg_data = buffer[8:8+frame_len]
    
    # Verify end marker
    end_marker = buffer[8+frame_len:8+frame_len+4]
    if end_marker != FRAME_END:
        print("WARNING: End marker mismatch, but continuing...")
    
    print("Frame captured successfully!")
    return jpeg_data

def main():
    print(f"Connecting to {SERIAL_PORT} at {BAUD_RATE} baud...")
    
    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        time.sleep(2)  # Wait for ESP32 to initialize
        
        # Check status
        ser.reset_input_buffer()
        ser.write(b'S')
        time.sleep(0.5)
        response = ser.read(ser.in_waiting).decode('utf-8', errors='ignore')
        print(f"Status: {response.strip()}")
        
        # Capture frame
        jpeg_data = capture_frame(ser)
        
        if jpeg_data:
            # Save to file
            with open(OUTPUT_FILE, 'wb') as f:
                f.write(jpeg_data)
            print(f"\n✓ Image saved to: {OUTPUT_FILE}")
            print(f"  Size: {len(jpeg_data)} bytes")
            
            # Open the image
            os.system(f'open "{OUTPUT_FILE}"')
        else:
            print("\n✗ Failed to capture image")
        
        ser.close()
        
    except serial.SerialException as e:
        print(f"Serial error: {e}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
