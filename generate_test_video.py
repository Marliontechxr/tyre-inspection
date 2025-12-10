#!/usr/bin/env python3
"""
Synthetic Tyre Conveyor Video Generator
Simulates tyres with paint dots moving on a conveyor belt
For testing motion blur and capture timing
"""

import cv2
import numpy as np
import os

# Video settings
OUTPUT_PATH = "/Users/marlionmac/Projects/tyre-inspection/test_conveyor.mp4"
WIDTH, HEIGHT = 640, 480
FPS = 30
DURATION_SEC = 10

# Conveyor settings (matching real-world hypothesis)
BELT_SPEED_PX_PER_FRAME = 6  # ~15cm/sec at 30fps, scaled to pixels
TYRE_SPACING_PX = 150  # Gap between tyres
TYRE_WIDTH_PX = 280  # Tyre visible width (realistic - tyre is large)

# Paint dot settings (realistic - dot is small relative to tyre)
DOT_RADIUS = 12  # pixels (small dot ~1.5cm on large tyre)
DOT_COLOR_YELLOW = (0, 230, 255)  # BGR - yellow
DOT_COLOR_RED = (0, 0, 230)  # BGR - red

# Dot position variation (not always centered)
import random
random.seed(42)  # Reproducible randomness

# Tyre definitions: (x_start, dot_type, dot_color, is_defective)
# dot_type: 'circle', 'pacman', 'donut', 'double', 'none'
TYRES = [
    {'dot_type': 'circle', 'color': 'yellow', 'defective': False},
    {'dot_type': 'pacman', 'color': 'yellow', 'defective': True},
    {'dot_type': 'circle', 'color': 'red', 'defective': False},
    {'dot_type': 'irregular', 'color': 'yellow', 'defective': True},
    {'dot_type': 'circle', 'color': 'yellow', 'defective': False},
    {'dot_type': 'donut', 'color': 'red', 'defective': False},
    {'dot_type': 'double', 'color': 'yellow', 'defective': True},
    {'dot_type': 'none', 'color': None, 'defective': True},
    {'dot_type': 'circle', 'color': 'yellow', 'defective': False},
    {'dot_type': 'smear', 'color': 'yellow', 'defective': True},
]

def draw_tyre(frame, x_center, y_center, tyre_info, tyre_index):
    """Draw a tyre section with paint dot at realistic position"""
    
    # Draw tyre rubber (dark black - realistic rubber)
    cv2.ellipse(frame, (x_center, y_center), (TYRE_WIDTH_PX//2, 120), 
                0, 0, 360, (25, 25, 25), -1)
    
    # Tyre tread pattern (subtle lines)
    for i in range(-3, 4):
        offset = i * 25
        cv2.ellipse(frame, (x_center, y_center), (TYRE_WIDTH_PX//2 - 10 + abs(i)*3, 110), 
                    0, 0, 360, (35, 35, 35), 1)
    
    # Inner tyre wall (slightly lighter)
    cv2.ellipse(frame, (x_center, y_center), (TYRE_WIDTH_PX//2 - 40, 80), 
                0, 0, 360, (40, 40, 40), -1)
    
    # Rim area (dark center)
    cv2.ellipse(frame, (x_center, y_center), (TYRE_WIDTH_PX//2 - 80, 40), 
                0, 0, 360, (20, 20, 20), -1)
    
    # Draw paint dot based on type
    dot_type = tyre_info['dot_type']
    color = DOT_COLOR_YELLOW if tyre_info['color'] == 'yellow' else DOT_COLOR_RED
    
    # Randomize dot position (not centered) - on the sidewall
    # Position varies per tyre but is consistent for that tyre
    random.seed(42 + tyre_index)  # Consistent position per tyre
    dot_offset_x = random.randint(-60, 60)
    dot_offset_y = random.randint(-40, 40)
    
    dot_x = x_center + dot_offset_x
    dot_y = y_center + dot_offset_y
    
    if dot_type == 'circle':
        # Perfect circle - ACCEPT
        cv2.circle(frame, (dot_x, dot_y), DOT_RADIUS, color, -1)
        
    elif dot_type == 'pacman':
        # Circle with bite mark - REJECT
        cv2.circle(frame, (dot_x, dot_y), DOT_RADIUS, color, -1)
        # Cut out a triangle (pac-man mouth) - scaled to small dot
        bite_size = DOT_RADIUS // 2
        pts = np.array([[dot_x, dot_y], 
                        [dot_x + DOT_RADIUS + 2, dot_y - bite_size],
                        [dot_x + DOT_RADIUS + 2, dot_y + bite_size]], np.int32)
        cv2.fillPoly(frame, [pts], (25, 25, 25))
        
    elif dot_type == 'irregular':
        # Irregular blob - REJECT (scaled down)
        scale = DOT_RADIUS / 25  # Scale factor
        pts = np.array([
            [dot_x + int(-15*scale), dot_y + int(-8*scale)],
            [dot_x + int(-3*scale), dot_y + int(-18*scale)],
            [dot_x + int(12*scale), dot_y + int(-10*scale)],
            [dot_x + int(18*scale), dot_y + int(4*scale)],
            [dot_x + int(8*scale), dot_y + int(15*scale)],
            [dot_x + int(-12*scale), dot_y + int(10*scale)],
        ], np.int32)
        cv2.fillPoly(frame, [pts], color)
        
    elif dot_type == 'donut':
        # Donut shape - ACCEPT (if clean)
        cv2.circle(frame, (dot_x, dot_y), DOT_RADIUS, color, -1)
        cv2.circle(frame, (dot_x, dot_y), DOT_RADIUS // 3, (25, 25, 25), -1)
        
    elif dot_type == 'double':
        # Two dots - REJECT (scaled spacing)
        spacing = DOT_RADIUS + 5
        cv2.circle(frame, (dot_x - spacing//2, dot_y), DOT_RADIUS - 3, color, -1)
        cv2.circle(frame, (dot_x + spacing//2, dot_y), DOT_RADIUS - 3, color, -1)
        
    elif dot_type == 'smear':
        # Smeared/elongated - REJECT
        cv2.ellipse(frame, (dot_x, dot_y), (DOT_RADIUS + 8, DOT_RADIUS - 4),
                    25, 0, 360, color, -1)
        
    elif dot_type == 'none':
        # No dot - REJECT
        pass
    
    return frame

def generate_video():
    """Generate the test conveyor video"""
    
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(OUTPUT_PATH, fourcc, FPS, (WIDTH, HEIGHT))
    
    total_frames = FPS * DURATION_SEC
    
    # Calculate initial positions for all tyres (start off-screen right)
    tyre_positions = []
    for i, tyre in enumerate(TYRES):
        x_start = WIDTH + 100 + i * (TYRE_WIDTH_PX + TYRE_SPACING_PX)
        tyre_positions.append(x_start)
    
    # Capture trigger timestamps (for later sync testing)
    trigger_frames = []
    
    print(f"Generating {total_frames} frames...")
    
    for frame_num in range(total_frames):
        # Create belt background (gray conveyor)
        frame = np.ones((HEIGHT, WIDTH, 3), dtype=np.uint8) * 80
        
        # Add belt texture lines
        for y in range(0, HEIGHT, 20):
            cv2.line(frame, (0, y), (WIDTH, y), (70, 70, 70), 1)
        
        # Draw each tyre
        y_center = HEIGHT // 2
        
        for i, tyre in enumerate(TYRES):
            x_pos = tyre_positions[i] - (frame_num * BELT_SPEED_PX_PER_FRAME)
            
            # Only draw if visible
            if -TYRE_WIDTH_PX < x_pos < WIDTH + TYRE_WIDTH_PX:
                draw_tyre(frame, int(x_pos), y_center, tyre, i)
                
                # Log when tyre center crosses the capture zone (center of frame)
                if abs(x_pos - WIDTH//2) < BELT_SPEED_PX_PER_FRAME:
                    trigger_frames.append({
                        'frame': frame_num,
                        'time_sec': frame_num / FPS,
                        'tyre_index': i,
                        'expected': 'ACCEPT' if not tyre['defective'] else 'REJECT',
                        'dot_type': tyre['dot_type']
                    })
        
        # Add frame counter and timestamp
        cv2.putText(frame, f"Frame: {frame_num} | Time: {frame_num/FPS:.2f}s", 
                    (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)
        
        # Add capture zone indicator (center line)
        cv2.line(frame, (WIDTH//2, 0), (WIDTH//2, HEIGHT), (0, 255, 0), 1)
        cv2.putText(frame, "CAPTURE ZONE", (WIDTH//2 - 60, HEIGHT - 20), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
        
        out.write(frame)
        
        if frame_num % 30 == 0:
            print(f"  Frame {frame_num}/{total_frames}")
    
    out.release()
    print(f"\n✓ Video saved to: {OUTPUT_PATH}")
    print(f"  Duration: {DURATION_SEC}s, {total_frames} frames at {FPS}fps")
    
    # Save trigger timestamps
    print("\n📍 Optimal capture timestamps:")
    print("-" * 60)
    for t in trigger_frames:
        print(f"  Frame {t['frame']:3d} | {t['time_sec']:.2f}s | Tyre {t['tyre_index']} | "
              f"{t['dot_type']:10s} | Expected: {t['expected']}")
    
    # Save to file for later use
    with open("/Users/marlionmac/Projects/tyre-inspection/trigger_timestamps.txt", "w") as f:
        f.write("frame,time_sec,tyre_index,dot_type,expected\n")
        for t in trigger_frames:
            f.write(f"{t['frame']},{t['time_sec']:.3f},{t['tyre_index']},{t['dot_type']},{t['expected']}\n")
    
    return trigger_frames

if __name__ == "__main__":
    triggers = generate_video()
    print(f"\n✓ Trigger timestamps saved to: trigger_timestamps.txt")
    print(f"\nNext: Play this video and point ESP32-CAM at screen to test capture timing!")
