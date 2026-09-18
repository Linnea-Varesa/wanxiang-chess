#include "identity_grid.h"
#include "config.h"

IdentityGrid::IdentityGrid() : _bus(ID_ONEWIRE_PIN) {}

void IdentityGrid::begin() {
    pinMode(ID_MUX_S0_PIN, OUTPUT);
    pinMode(ID_MUX_S1_PIN, OUTPUT);
    pinMode(ID_MUX_S2_PIN, OUTPUT);
    pinMode(ID_MUX_S3_PIN, OUTPUT);
    pinMode(ID_MUX_EN_PIN, OUTPUT);
    digitalWrite(ID_MUX_EN_PIN, HIGH); // 禁用多路器，避免上电误读
    pinMode(ID_ONEWIRE_PIN, INPUT_PULLUP);
}

void IdentityGrid::selectChannel(uint8_t channel) {
    digitalWrite(ID_MUX_EN_PIN, HIGH);
    digitalWrite(ID_MUX_S0_PIN, channel & 0x01);
    digitalWrite(ID_MUX_S1_PIN, (channel >> 1) & 0x01);
    digitalWrite(ID_MUX_S2_PIN, (channel >> 2) & 0x01);
    digitalWrite(ID_MUX_S3_PIN, (channel >> 3) & 0x01);
    delay(ID_SETTLE_MS);
    digitalWrite(ID_MUX_EN_PIN, LOW);
}

IdentityReading IdentityGrid::readOnce(uint8_t channel) {
    IdentityReading result{};
    selectChannel(channel);
    _bus.reset_search();
    if (!_bus.search(result.uid)) {
        digitalWrite(ID_MUX_EN_PIN, HIGH);
        return result;
    }

    result.present = true;
    result.family_code = result.uid[0];
    result.crc_ok = OneWire::crc8(result.uid, 7) == result.uid[7];
    // 0x2D = DS2431; 0x01 = DS2401/DS2411 family used by the electrical backup.
    result.supported_family = result.family_code == 0x2D || result.family_code == 0x01;
    digitalWrite(ID_MUX_EN_PIN, HIGH);
    return result;
}

IdentityReading IdentityGrid::readChannel(uint8_t channel) {
    IdentityReading last{};
    if (channel >= ID_GRID_CHANNELS) return last;

    for (uint8_t attempt = 0; attempt < ID_SCAN_RETRIES; ++attempt) {
        last = readOnce(channel);
        if (!last.present || (last.crc_ok && last.supported_family)) return last;
    }
    return last;
}

String IdentityGrid::formatUid(const uint8_t uid[8]) const {
    char buf[17];
    for (uint8_t i = 0; i < 8; ++i) {
        snprintf(&buf[i * 2], 3, "%02X", uid[i]);
    }
    buf[16] = '\0';
    return String(buf);
}

uint8_t IdentityGrid::channelCount() const { return ID_GRID_CHANNELS; }
