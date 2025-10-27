#ifndef WIFI_CONFIG_H
#define WIFI_CONFIG_H

// Wi-Fi credentials
const char* ssid = "FTTH";
const char* password = "12345678";

// Optional static IP (set for stability)
IPAddress local_IP(192, 168, 1, 99);
IPAddress gateway(192, 168, 1, 1);
IPAddress subnet(255, 255, 255, 0);

#endif
