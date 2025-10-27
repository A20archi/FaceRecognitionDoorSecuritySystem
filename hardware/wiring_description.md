# Wiring and Hardware Connections

## ESP32-CAM to Raspberry Pi Zero 2 W
- The ESP32-CAM connects to Wi-Fi and streams images.
- The Raspberry Pi accesses the stream via IP to perform face recognition.

## Relay and Solenoid Lock
- Relay IN pin → Raspberry Pi GPIO17  
- Relay VCC → 5V output from LM2596  
- Relay GND → Raspberry Pi GND  
- Solenoid Lock → Relay NO (Normally Open) terminal  
- Solenoid Lock power → 5V/12V line (as per lock rating)

## Power
- Two 18650 batteries (3.7V each) in series = ~7.4V  
- LM2596 output regulated to 5V for Pi and relay.  
- ESP32-CAM powered separately via 5V pin (or regulated 3.3V).

## Optional
- Add an LED on GPIO27 for “Access Granted” signal.  
- Add push button on GPIO22 to reset recognition.
- Ensure all grounds are connected together for a common reference.