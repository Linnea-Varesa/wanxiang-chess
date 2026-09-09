#ifndef BLE_SERVICE_H
#define BLE_SERVICE_H

#include <NimBLEDevice.h>
#include <string>
#include "config.h"

// 回调函数类型
typedef void (*CommandCallback)(const std::string& command);

class BLEService {
public:
    BLEService();
    void begin(CommandCallback callback);
    
    // 发送状态给客户端
    void notify(const std::string& message);
    
    // 是否有客户端连接
    bool isConnected();
    
private:
    NimBLEServer* _server;
    NimBLECharacteristic* _characteristic;
    bool _connected;
    CommandCallback _callback;
    
    friend class ServerCallbacks;
    friend class CharacteristicCallbacks;
};

#endif // BLE_SERVICE_H
