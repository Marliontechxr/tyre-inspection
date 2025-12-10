/*
 * ESP32-CAM Firmware for Tyre Paint Dot Inspection
 * 
 * Purpose: Capture JPEG frames and send over USB Serial to Raspberry Pi 5
 * Optimized for: Low latency, high reliability, factory environment
 * 
 * Hardware: AI-Thinker ESP32-CAM
 * Connection: USB Serial via TTL adapter @ 921600 baud
 */

#include "esp_camera.h"
#include "Arduino.h"

// =============================================================================
// CONFIGURATION - Adjust these for your setup
// =============================================================================

// Serial baud rate (921600 for speed, 115200 for reliability)
#define SERIAL_BAUD 921600

// Frame resolution - VGA (640x480) for better detail
// Higher resolution = better solidity measurement accuracy
#define FRAME_SIZE FRAMESIZE_VGA  // Options: FRAMESIZE_QVGA, FRAMESIZE_VGA, FRAMESIZE_SVGA

// JPEG quality (10-63, lower = better quality, larger file, slower)
// Using 15 for VGA to balance quality vs transfer speed
#define JPEG_QUALITY 15

// Capture mode: 
// - CONTINUOUS: Stream frames as fast as possible
// - TRIGGERED: Wait for 'C' command from Pi to capture
#define CAPTURE_MODE_TRIGGERED true

// Frame start/end markers for reliable parsing
#define FRAME_START_MARKER 0xFF, 0xAA, 0x55, 0xBB
#define FRAME_END_MARKER   0xFF, 0xBB, 0x55, 0xAA

// =============================================================================
// AI-THINKER ESP32-CAM PIN DEFINITIONS (DO NOT CHANGE)
// =============================================================================
#define PWDN_GPIO_NUM     32
#define RESET_GPIO_NUM    -1
#define XCLK_GPIO_NUM      0
#define SIOD_GPIO_NUM     26
#define SIOC_GPIO_NUM     27
#define Y9_GPIO_NUM       35
#define Y8_GPIO_NUM       34
#define Y7_GPIO_NUM       39
#define Y6_GPIO_NUM       36
#define Y5_GPIO_NUM       21
#define Y4_GPIO_NUM       19
#define Y3_GPIO_NUM       18
#define Y2_GPIO_NUM        5
#define VSYNC_GPIO_NUM    25
#define HREF_GPIO_NUM     23
#define PCLK_GPIO_NUM     22

// Built-in LED for status indication
#define LED_GPIO_NUM       4

// =============================================================================
// GLOBALS
// =============================================================================
const uint8_t frameStartMarker[] = {FRAME_START_MARKER};
const uint8_t frameEndMarker[] = {FRAME_END_MARKER};
uint32_t frameCount = 0;
uint32_t lastFrameTime = 0;

// =============================================================================
// CAMERA INITIALIZATION
// =============================================================================
bool initCamera() {
  camera_config_t config;
  config.ledc_channel = LEDC_CHANNEL_0;
  config.ledc_timer = LEDC_TIMER_0;
  config.pin_d0 = Y2_GPIO_NUM;
  config.pin_d1 = Y3_GPIO_NUM;
  config.pin_d2 = Y4_GPIO_NUM;
  config.pin_d3 = Y5_GPIO_NUM;
  config.pin_d4 = Y6_GPIO_NUM;
  config.pin_d5 = Y7_GPIO_NUM;
  config.pin_d6 = Y8_GPIO_NUM;
  config.pin_d7 = Y9_GPIO_NUM;
  config.pin_xclk = XCLK_GPIO_NUM;
  config.pin_pclk = PCLK_GPIO_NUM;
  config.pin_vsync = VSYNC_GPIO_NUM;
  config.pin_href = HREF_GPIO_NUM;
  config.pin_sccb_sda = SIOD_GPIO_NUM;
  config.pin_sccb_scl = SIOC_GPIO_NUM;
  config.pin_pwdn = PWDN_GPIO_NUM;
  config.pin_reset = RESET_GPIO_NUM;
  config.xclk_freq_hz = 20000000;
  config.pixel_format = PIXFORMAT_JPEG;
  config.frame_size = FRAME_SIZE;
  config.jpeg_quality = JPEG_QUALITY;
  config.fb_count = 1;  // Single buffer for triggered capture (prevents overflow)
  config.fb_location = CAMERA_FB_IN_PSRAM;
  config.grab_mode = CAMERA_GRAB_WHEN_EMPTY;  // Only capture when buffer is free

  // Initialize camera
  esp_err_t err = esp_camera_init(&config);
  if (err != ESP_OK) {
    return false;
  }

  // Optimize sensor settings for factory lighting + ring light
  sensor_t *s = esp_camera_sensor_get();
  if (s != NULL) {
    s->set_brightness(s, 0);      // -2 to 2
    s->set_contrast(s, 1);        // -2 to 2 (slight boost for paint dots)
    s->set_saturation(s, 2);      // -2 to 2 (max boost for yellow/red detection)
    s->set_whitebal(s, 1);        // Auto white balance ON
    s->set_awb_gain(s, 1);        // AWB gain ON
    s->set_wb_mode(s, 0);         // Auto WB mode
    
    // DEFAULT: Fast exposure for motion blur reduction
    // Requires bright ring light! Use 'A' command to switch to auto if too dark
    s->set_exposure_ctrl(s, 0);   // Manual exposure
    s->set_aec2(s, 0);            // AEC DSP OFF
    s->set_ae_level(s, 0);        // AE level
    s->set_aec_value(s, 80);      // Short exposure (~8ms) - anti motion blur
    s->set_gain_ctrl(s, 0);       // Manual gain
    s->set_agc_gain(s, 12);       // High gain to compensate for short exposure
    s->set_gainceiling(s, (gainceiling_t)6); // Gain ceiling
    
    s->set_bpc(s, 1);             // Black pixel correction
    s->set_wpc(s, 1);             // White pixel correction
    s->set_raw_gma(s, 1);         // Gamma correction
    s->set_lenc(s, 1);            // Lens correction
    s->set_hmirror(s, 0);         // No horizontal mirror
    s->set_vflip(s, 0);           // No vertical flip
    s->set_dcw(s, 1);             // Downsize EN
  }

  return true;
}

// =============================================================================
// CAPTURE AND SEND FRAME
// =============================================================================
void captureAndSendFrame() {
  // Capture frame
  camera_fb_t *fb = esp_camera_fb_get();
  if (!fb) {
    Serial.println("ERROR:CAPTURE_FAILED");
    return;
  }

  // Blink LED to indicate capture
  digitalWrite(LED_GPIO_NUM, HIGH);

  // Send frame with markers for reliable parsing
  // Format: [START_MARKER][4-byte length][JPEG data][END_MARKER]
  
  // Start marker
  Serial.write(frameStartMarker, sizeof(frameStartMarker));
  
  // Frame length (4 bytes, little-endian)
  uint32_t len = fb->len;
  Serial.write((uint8_t)(len & 0xFF));
  Serial.write((uint8_t)((len >> 8) & 0xFF));
  Serial.write((uint8_t)((len >> 16) & 0xFF));
  Serial.write((uint8_t)((len >> 24) & 0xFF));
  
  // JPEG data
  Serial.write(fb->buf, fb->len);
  
  // End marker
  Serial.write(frameEndMarker, sizeof(frameEndMarker));
  
  // Flush serial buffer
  Serial.flush();

  // LED off
  digitalWrite(LED_GPIO_NUM, LOW);

  // Stats
  frameCount++;
  uint32_t now = millis();
  if (now - lastFrameTime >= 5000) {
    // Every 5 seconds, print stats (visible in Pi logs)
    float fps = (float)frameCount / ((now - lastFrameTime) / 1000.0);
    // Send as comment line (Pi will ignore)
    // Serial.printf("# FPS: %.1f, Frames: %d\n", fps, frameCount);
    frameCount = 0;
    lastFrameTime = now;
  }

  // Return frame buffer
  esp_camera_fb_return(fb);
}

// =============================================================================
// COMMAND PROCESSING
// =============================================================================
void processCommand(char cmd) {
  switch (cmd) {
    case 'C':  // Capture single frame
    case 'c':
      captureAndSendFrame();
      break;
      
    case 'S':  // Status check
    case 's':
      Serial.println("STATUS:OK");
      break;
      
    case 'R':  // Resolution change to QVGA
    case 'r':
      {
        sensor_t *s = esp_camera_sensor_get();
        if (s) {
          s->set_framesize(s, FRAMESIZE_QVGA);
          Serial.println("RESOLUTION:QVGA");
        }
      }
      break;
      
    case 'V':  // Resolution change to VGA
    case 'v':
      {
        sensor_t *sv = esp_camera_sensor_get();
        if (sv) {
          sv->set_framesize(sv, FRAMESIZE_VGA);
          Serial.println("RESOLUTION:VGA");
        }
      }
      break;
      
    case 'L':  // LED on (for alignment)
    case 'l':
      digitalWrite(LED_GPIO_NUM, HIGH);
      Serial.println("LED:ON");
      break;
      
    case 'O':  // LED off
    case 'o':
      digitalWrite(LED_GPIO_NUM, LOW);
      Serial.println("LED:OFF");
      break;
    
    case 'F':  // Fast exposure mode (anti-motion blur)
    case 'f':
      {
        sensor_t *sf = esp_camera_sensor_get();
        if (sf) {
          sf->set_exposure_ctrl(sf, 0);   // Disable auto exposure
          sf->set_aec_value(sf, 50);      // Very short exposure (~5ms)
          sf->set_gain_ctrl(sf, 0);       // Disable auto gain
          sf->set_agc_gain(sf, 15);       // High gain to compensate
          Serial.println("EXPOSURE:FAST (need bright light!)");
        }
      }
      break;
    
    case 'A':  // Auto exposure mode (normal)
    case 'a':
      {
        sensor_t *sa = esp_camera_sensor_get();
        if (sa) {
          sa->set_exposure_ctrl(sa, 1);   // Enable auto exposure
          sa->set_gain_ctrl(sa, 1);       // Enable auto gain
          Serial.println("EXPOSURE:AUTO");
        }
      }
      break;
    
    case 'M':  // Medium exposure (balanced)
    case 'm':
      {
        sensor_t *sm = esp_camera_sensor_get();
        if (sm) {
          sm->set_exposure_ctrl(sm, 0);   // Disable auto exposure
          sm->set_aec_value(sm, 150);     // Medium exposure (~15ms)
          sm->set_gain_ctrl(sm, 0);       // Disable auto gain
          sm->set_agc_gain(sm, 8);        // Medium gain
          Serial.println("EXPOSURE:MEDIUM");
        }
      }
      break;
      
    default:
      break;
  }
}

// =============================================================================
// SETUP
// =============================================================================
void setup() {
  // Initialize serial
  Serial.begin(SERIAL_BAUD);
  Serial.setTimeout(10);  // Fast timeout for commands
  
  // LED setup
  pinMode(LED_GPIO_NUM, OUTPUT);
  digitalWrite(LED_GPIO_NUM, LOW);
  
  // Wait for serial
  delay(500);
  
  // Initialize camera
  Serial.println("# Initializing camera...");
  if (!initCamera()) {
    Serial.println("ERROR:CAMERA_INIT_FAILED");
    // Blink LED rapidly to indicate error
    while (true) {
      digitalWrite(LED_GPIO_NUM, HIGH);
      delay(100);
      digitalWrite(LED_GPIO_NUM, LOW);
      delay(100);
    }
  }
  
  Serial.println("STATUS:READY");
  Serial.println("# Commands: C=capture, S=status, R=QVGA, V=VGA, L=LED on, O=LED off");
  
  lastFrameTime = millis();
}

// =============================================================================
// MAIN LOOP
// =============================================================================
void loop() {
  #if CAPTURE_MODE_TRIGGERED
    // Triggered mode: Wait for command from Pi
    if (Serial.available() > 0) {
      char cmd = Serial.read();
      processCommand(cmd);
    }
  #else
    // Continuous mode: Stream frames as fast as possible
    captureAndSendFrame();
    delay(33);  // ~30 FPS cap
  #endif
}
