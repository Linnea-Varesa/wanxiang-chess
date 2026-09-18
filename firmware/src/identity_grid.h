#ifndef IDENTITY_GRID_H
#define IDENTITY_GRID_H

#include <Arduino.h>
#include <OneWire.h>
#include <stdint.h>

struct IdentityReading {
    bool present;
    bool crc_ok;
    bool supported_family;
    uint8_t family_code;
    uint8_t uid[8];
};

class IdentityGrid {
public:
    IdentityGrid();
    void begin();
    IdentityReading readChannel(uint8_t channel);
    String formatUid(const uint8_t uid[8]) const;
    uint8_t channelCount() const;

private:
    OneWire _bus;
    void selectChannel(uint8_t channel);
    IdentityReading readOnce(uint8_t channel);
};

#endif
