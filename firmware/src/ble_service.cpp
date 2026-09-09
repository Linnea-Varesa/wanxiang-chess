#include "ble_service.h"
#include <Arduino.h>

// 服务端回调
class ServerCallbacks : public NimBLEServerCallbacks {
public:
    ServerCallbacks(BLEService* service) : _service(service) {}
    
    void onConnect(NimBLEServer* pServer) override {
        _service->_connected = true;
        Serial.println("[BLE] 客户端已连接");
    }
    
    void onDisconnect(NimBLEServer* pServer) override {
        _service->_connected = false;
        Serial.println("[BLE] 客户端断开，重新广播");
        NimBLEDevice::startAdvertising();
    }
    
private:
    BLEService* _service;
};

// 特征值回调（接收数据）
class CharacteristicCallbacks : public NimBLECharacteristicCallbacks {
public:
    CharacteristicCallbacks(BLEService* service) : _service(service) {}
    
    void onWrite(NimBLECharacteristic* pCharacteristic) override {
        std::string value = pCharacteristic->getValue();
        if (!value.empty() && _service->_callback) {
            Serial.print("[BLE] 收到指令: ");
            Serial.println(value.c_str());
            _service->_callback(value);
        }
    }
    
private:
    BLEService* _service;
};

BLEService::BLEService() : _server(nullptr), _characteristic(nullptr), _connected(false), _callback(nullptr) {}

void BLEService::begin(CommandCallback callback) {
    _callback = callback;
    
    NimBLEDevice::init(BLE_DEVICE_NAME);
    NimBLEDevice::setPower(ESP_PWR_LVL_P9);
    
    _server = NimBLEDevice::createServer();
    _server->setCallbacks(new ServerCallbacks(this));
    
    NimBLEService* service = _server->createService(BLE_SERVICE_UUID);
    
    _characteristic = service->createCharacteristic(
        BLE_CHARACTERISTIC_UUID,
        NIMBLE_PROPERTY::READ | NIMBLE_PROPERTY::WRITE | NIMBLE_PROPERTY::NOTIFY
    );
    _characteristic->setCallbacks(new CharacteristicCallbacks(this));
    
    service->start();
    
    // 开始广播
    NimBLEAdvertising* advertising = NimBLEDevice::getAdvertising();
    advertising->addServiceUUID(BLE_SERVICE_UUID);
    advertising->setScanResponse(true);
    advertising->start();
    
    Serial.println("[BLE] 服务已启动，设备名: " + String(BLE_DEVICE_NAME));
}

void BLEService::notify(const std::string& message) {
    if (_connected && _characteristic) {
        _characteristic->setValue(message);
        _characteristic->notify();
    }
}

bool BLEService::isConnected() { return _connected; }
