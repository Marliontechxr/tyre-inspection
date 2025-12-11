# 🛒 Complete Shopping List - Tyre Paint Dot Inspection System
## Richie Street, Chennai - December 2024

---

## Project Summary
**Goal:** Real-time vision-based defect detection for tyre factory  
**Function:** Detect paint dot quality, control PLC for accept/reject  
**Requirements:** <250ms latency, 60+ tyres/min capacity, fingerprint auth, Firebase logging, touchscreen dashboard

---

## 📦 COMPLETE PARTS LIST

### 1. MAIN PROCESSING UNIT

| Item | Specification | Qty | Est. Price (₹) | Where to Buy | Notes |
|------|---------------|-----|----------------|--------------|-------|
| **Orange Pi 5 (4GB)** | RK3588S, 4GB RAM | 1 | ₹4,500-5,500 | Kasturi Electronics, Modi Electronics, or Online (Robu.in) | **Recommended over RPi5** - Faster, cheaper, same GPIO |
| **32GB microSD Card** | Class 10, A1 rated | 1 | ₹350-500 | Any electronics shop | For Armbian OS |
| **5V 4A USB-C Power Supply** | 20W minimum | 1 | ₹400-600 | Same shop | Must be quality PSU |
| **Heatsink + Fan** | For Orange Pi 5 | 1 | ₹150-300 | Same shop | Essential for stability |

**Subtotal: ₹5,400-6,900**

---

### 2. CAMERA MODULE

| Item | Specification | Qty | Est. Price (₹) | Where to Buy | Notes |
|------|---------------|-----|----------------|--------------|-------|
| **ESP32-CAM (AI-Thinker)** | OV2640 sensor, with antenna | 2 | ₹450-600 each | Kasturi Electronics, Modi Electronics | Buy 2 (1 spare) |
| **ESP32-CAM MB Programmer** | USB programmer board | 1 | ₹150-250 | Same shop | **IMPORTANT** - Makes flashing easy, no separate TTL adapter needed |
| **OV5640 Camera Module** (Optional upgrade) | 5MP, autofocus | 1 | ₹1,500-2,500 | Online (Amazon/Robu) | Higher resolution if needed |

**Subtotal: ₹1,050-1,700 (basic) or ₹2,550-4,200 (with OV5640)**

---

### 3. SERIAL COMMUNICATION

| Item | Specification | Qty | Est. Price (₹) | Where to Buy | Notes |
|------|---------------|-----|----------------|--------------|-------|
| **USB to TTL Adapter** | CP2102 or CH340G, 3.3V/5V | 2 | ₹80-150 each | Any electronics shop | For ESP32-CAM to Orange Pi |
| **USB Hub (Powered)** | 4-port, USB 3.0 | 1 | ₹400-600 | Same shop | For multiple USB devices |

**Subtotal: ₹560-900**

---

### 4. SENSORS

| Item | Specification | Qty | Est. Price (₹) | Where to Buy | Notes |
|------|---------------|-----|----------------|--------------|-------|
| **HC-SR04 Ultrasonic Sensor** | 5V, 2cm-400cm range | 2 | ₹50-80 each | Any electronics shop | Tyre presence detection (1 spare) |
| **R307 Fingerprint Sensor** | TTL UART, 3.3V/5V | 1 | ₹800-1,200 | Kasturi, Modi, or Amazon | User authentication |
| **IR Obstacle Sensor** (Optional) | Digital output | 2 | ₹40-60 each | Any shop | Backup tyre detection |

**Subtotal: ₹940-1,420**

---

### 5. DISPLAY

| Item | Specification | Qty | Est. Price (₹) | Where to Buy | Notes |
|------|---------------|-----|----------------|--------------|-------|
| **7" IPS Touch Display** | 1024x600, HDMI + USB touch | 1 | ₹2,500-4,000 | Kasturi, Modi, Online | For dashboard |
| **Display Stand/Mount** | Adjustable | 1 | ₹200-400 | Same shop | For control panel |

**Subtotal: ₹2,700-4,400**

---

### 6. LIGHTING (CRITICAL!)

| Item | Specification | Qty | Est. Price (₹) | Where to Buy | Notes |
|------|---------------|-----|----------------|--------------|-------|
| **Option A: Budget LED Ring Light** | 60mm-80mm, 12V/24V, white | 1 | ₹800-1,500 | Richie Street, Amazon | Basic option |
| **Option B: Machine Vision Ring Light** | 60mm, industrial grade | 1 | ₹6,000-12,000 | IndiaMART, Robotronix | Professional option |
| **12V/24V Power Supply** | 2A for LED ring | 1 | ₹250-400 | Any shop | Match to ring light voltage |
| **Light Diffuser** | Acrylic, matte white | 1 | ₹100-200 | Acrylic shop | Softens light |

**Subtotal: ₹1,150-2,100 (budget) or ₹6,350-12,600 (professional)**

---

### 7. PLC / OUTPUT CONTROL

| Item | Specification | Qty | Est. Price (₹) | Where to Buy | Notes |
|------|---------------|-----|----------------|--------------|-------|
| **2-Channel Relay Module** | 5V, optocoupler isolated | 1 | ₹80-150 | Any electronics shop | Accept/Reject signals |
| **4-Channel Relay Module** | 5V, optocoupler isolated | 1 | ₹150-250 | Same shop | If more outputs needed |
| **Terminal Block Connectors** | Screw type | 1 pack | ₹50-100 | Same shop | For PLC wiring |
| **24V Signal Cable** | 2-core shielded | 5m | ₹100-200 | Same shop | To PLC |

**Subtotal: ₹380-700**

---

### 8. WIRING & CONNECTORS

| Item | Specification | Qty | Est. Price (₹) | Where to Buy | Notes |
|------|---------------|-----|----------------|--------------|-------|
| **Jumper Wires (M-M)** | 20cm, 40-piece | 1 pack | ₹80-120 | Any shop | Prototyping |
| **Jumper Wires (M-F)** | 20cm, 40-piece | 1 pack | ₹80-120 | Any shop | Sensor connections |
| **Jumper Wires (F-F)** | 20cm, 40-piece | 1 pack | ₹80-120 | Any shop | GPIO connections |
| **Breadboard** | 830 tie-points | 1 | ₹80-150 | Any shop | Prototyping |
| **PCB Prototype Board** | 5x7cm, double-sided | 3 | ₹30-50 each | Any shop | Final wiring |
| **Resistor Kit** | 1/4W, assorted (1K, 2K needed) | 1 | ₹100-200 | Any shop | Voltage divider for ultrasonic |
| **Capacitor Kit** | Assorted (10µF, 100µF) | 1 | ₹100-150 | Any shop | Power stabilization |
| **Heat Shrink Tubing** | Assorted sizes | 1 pack | ₹80-120 | Any shop | Wire insulation |

**Subtotal: ₹710-1,130**

---

### 9. ENCLOSURE & MOUNTING

| Item | Specification | Qty | Est. Price (₹) | Where to Buy | Notes |
|------|---------------|-----|----------------|--------------|-------|
| **Project Enclosure** | ABS, ~200x150x70mm | 1 | ₹300-500 | Electronics shop | For main unit |
| **Camera Enclosure** | Small, IP65 if possible | 1 | ₹200-400 | Same shop | Protect ESP32-CAM |
| **Mounting Bracket** | Adjustable arm | 1 | ₹300-500 | Hardware shop | Camera positioning |
| **Cable Glands** | PG7, PG9 | 5 | ₹20-30 each | Electronics shop | Waterproof cable entry |
| **Standoffs & Screws** | M3, assorted | 1 kit | ₹100-150 | Any shop | Board mounting |

**Subtotal: ₹1,000-1,700**

---

### 10. POWER & PROTECTION

| Item | Specification | Qty | Est. Price (₹) | Where to Buy | Notes |
|------|---------------|-----|----------------|--------------|-------|
| **DC-DC Buck Converter** | 24V→5V, 3A | 1 | ₹80-150 | Any shop | If using single 24V supply |
| **Fuse Holder + Fuses** | 5A, blade type | 1 | ₹50-80 | Any shop | Protection |
| **Surge Protector** | 5V/12V TVS diode | 2 | ₹20-40 each | Electronics shop | GPIO protection |
| **Power Strip** | 6-outlet, surge protected | 1 | ₹400-600 | Any shop | Workstation power |

**Subtotal: ₹570-910**

---

### 11. TOOLS (If not already owned)

| Item | Specification | Qty | Est. Price (₹) | Where to Buy | Notes |
|------|---------------|-----|----------------|--------------|-------|
| **Soldering Iron** | 40W, temperature controlled | 1 | ₹400-800 | Any shop | For permanent connections |
| **Solder Wire** | 60/40, 0.8mm | 1 roll | ₹80-120 | Any shop | |
| **Wire Stripper** | Multi-gauge | 1 | ₹150-300 | Any shop | |
| **Multimeter** | Digital, basic | 1 | ₹300-600 | Any shop | Essential for debugging |
| **Precision Screwdriver Set** | Phillips + Flathead | 1 set | ₹150-300 | Any shop | |
| **Hot Glue Gun** | 40W | 1 | ₹200-350 | Any shop | Mounting |

**Subtotal: ₹1,280-2,470**

---

## 💰 BUDGET SUMMARY

### Option A: BUDGET BUILD
| Category | Amount (₹) |
|----------|------------|
| Main Processing (Orange Pi 5) | 5,400-6,900 |
| Camera (ESP32-CAM x2 + MB) | 1,050-1,700 |
| Serial Communication | 560-900 |
| Sensors | 940-1,420 |
| Display | 2,700-4,400 |
| Lighting (Budget) | 1,150-2,100 |
| PLC/Output | 380-700 |
| Wiring | 710-1,130 |
| Enclosure | 1,000-1,700 |
| Power | 570-910 |
| Tools | 1,280-2,470 |
| **TOTAL** | **₹15,740-24,330** |

### Option B: PROFESSIONAL BUILD
| Category | Amount (₹) |
|----------|------------|
| Everything above EXCEPT lighting | ~₹14,590-22,230 |
| Professional Machine Vision Light | 6,350-12,600 |
| **TOTAL** | **₹20,940-34,830** |

---

## 🏪 RECOMMENDED SHOPS IN RICHIE STREET

1. **Kasturi Electronics**
   - Ground Floor, Majestic Plaza, Mount Road
   - Good for: Arduino, ESP32, Raspberry Pi, Sensors

2. **Modi Electronics**
   - Richie Street main road
   - Good for: Components, connectors, tools

3. **Ocean Student Projects Shop**
   - Good for: Project kits, sensors, displays

4. **Supreme Electronics**
   - Good for: Power supplies, enclosures

5. **Online Alternatives:**
   - Robu.in (good prices, reliable)
   - Amazon.in (fast delivery)
   - Robocraze.com
   - Electronicscomp.com

---

## ⚠️ CRITICAL NOTES

### Must-Have vs Nice-to-Have
| Must-Have | Nice-to-Have |
|-----------|--------------|
| Orange Pi 5 (4GB) | Orange Pi 5 (8GB) |
| ESP32-CAM + MB Programmer | OV5640 upgrade |
| HC-SR04 Ultrasonic | IR Backup sensors |
| R307 Fingerprint | Capacitive fingerprint |
| 7" Touch Display | 10" Display |
| Budget Ring Light | Machine Vision Light |
| 2-Ch Relay | 4-Ch Relay |

### Power Requirements Summary
| Device | Voltage | Current |
|--------|---------|---------|
| Orange Pi 5 | 5V | 3-4A |
| ESP32-CAM | 5V | 0.5A (peak) |
| Ring Light | 12V or 24V | 1-2A |
| Fingerprint | 5V (via Pi) | 0.1A |
| Relay Module | 5V (via Pi) | 0.1A |
| Display | 5V (via Pi USB) | 0.5A |

### Voltage Divider for Ultrasonic
```
HC-SR04 ECHO (5V) ──┬── 1kΩ ──► Orange Pi GPIO (3.3V)
                    │
                    └── 2kΩ ──► GND
```

---

## 📋 PRE-SHOPPING CHECKLIST

Before going to Richie Street:
- [ ] Print this list
- [ ] Carry cash (many shops don't take cards)
- [ ] Carry a bag for components
- [ ] Go early (shops open ~10am, less crowded before noon)
- [ ] Bring phone for reference images
- [ ] Have backup online ordering ready (some items may be out of stock)

---

## 🔧 ASSEMBLY ORDER (After Shopping)

1. **Day 1:** Set up Orange Pi with Armbian, test display
2. **Day 2:** Flash ESP32-CAM with firmware, test camera
3. **Day 3:** Wire ultrasonic sensor, test distance
4. **Day 4:** Wire fingerprint sensor, test enrollment
5. **Day 5:** Set up ring light, optimize camera exposure
6. **Day 6:** Wire relay module, test PLC signals
7. **Day 7:** Install software, Firebase setup, final testing

---

## 📞 CONTACTS (if needed)

- **Robotronix Automation (Machine Vision Lights):** IndiaMART listing
- **Robu.in Customer Care:** For online orders
- **Kasturi Electronics:** Check Google Maps for phone number

---

*Shopping list created: December 11, 2024*
*Project: Apollo Tyres Paint Dot Inspection System*
*GitHub: https://github.com/Marliontechxr/tyre-inspection*
