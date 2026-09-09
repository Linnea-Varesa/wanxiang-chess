/**
 * 万象实体互动桌 - 网页控制端
 * 使用 Web Bluetooth API 直接连接 ESP32
 */

// BLE UUID（与固件一致）
const SERVICE_UUID = '0000ffe0-0000-1000-8000-00805f9b34fb';
const CHARACTERISTIC_UUID = '0000ffe1-0000-1000-8000-00805f9b34fb';

let bluetoothDevice = null;
let characteristic = null;
let isConnected = false;

// DOM元素
const connectBtn = document.getElementById('connect-btn');
const disconnectBtn = document.getElementById('disconnect-btn');
const statusEl = document.getElementById('connection-status');
const positionEl = document.getElementById('position-info');
const logEl = document.getElementById('log');
const cmdInput = document.getElementById('cmd-input');
const sendCmdBtn = document.getElementById('send-cmd');
const speedSlider = document.getElementById('speed');
const speedValue = document.getElementById('speed-value');

// 日志函数
function log(message, type = 'info') {
    const line = document.createElement('div');
    line.className = `log-line ${type}`;
    const time = new Date().toLocaleTimeString();
    line.textContent = `[${time}] ${message}`;
    logEl.appendChild(line);
    logEl.scrollTop = logEl.scrollHeight;
}

// 连接设备
async function connect() {
    try {
        log('正在搜索设备...');
        
        bluetoothDevice = await navigator.bluetooth.requestDevice({
            filters: [{ namePrefix: 'Wanxiang' }],
            optionalServices: [SERVICE_UUID]
        });
        
        log(`找到设备: ${bluetoothDevice.name}`);
        
        bluetoothDevice.addEventListener('gattserverdisconnected', onDisconnected);
        
        const server = await bluetoothDevice.gatt.connect();
        const service = await server.getPrimaryService(SERVICE_UUID);
        characteristic = await service.getCharacteristic(CHARACTERISTIC_UUID);
        
        // 监听通知
        characteristic.addEventListener('characteristicvaluechanged', onDataReceived);
        await characteristic.startNotifications();
        
        isConnected = true;
        updateConnectionUI();
        log('连接成功！', 'received');
        
        // 查询状态
        sendCommand('STATUS?');
        
    } catch (error) {
        log(`连接失败: ${error.message}`, 'error');
    }
}

// 断开连接
async function disconnect() {
    if (bluetoothDevice && bluetoothDevice.gatt.connected) {
        await bluetoothDevice.gatt.disconnect();
    }
}

function onDisconnected() {
    isConnected = false;
    characteristic = null;
    updateConnectionUI();
    log('设备已断开', 'error');
}

// 接收数据
function onDataReceived(event) {
    const value = event.target.value;
    const decoder = new TextDecoder('utf-8');
    const message = decoder.decode(value);
    log(`← ${message}`, 'received');
    
    // 解析状态
    if (message.startsWith('STATUS')) {
        const match = message.match(/X:(-?\d+),Y:(-?\d+)/);
        if (match) {
            positionEl.textContent = `X: ${match[1]}, Y: ${match[2]}`;
        }
    }
}

// 发送指令
async function sendCommand(cmd) {
    if (!isConnected || !characteristic) {
        log('未连接设备', 'error');
        return;
    }
    
    try {
        const encoder = new TextEncoder();
        await characteristic.writeValue(encoder.encode(cmd + '\n'));
        log(`→ ${cmd}`, 'sent');
    } catch (error) {
        log(`发送失败: ${error.message}`, 'error');
    }
}

// 更新连接状态UI
function updateConnectionUI() {
    if (isConnected) {
        statusEl.textContent = '已连接';
        statusEl.className = 'status connected';
        connectBtn.disabled = true;
        disconnectBtn.disabled = false;
    } else {
        statusEl.textContent = '未连接';
        statusEl.className = 'status disconnected';
        connectBtn.disabled = false;
        disconnectBtn.disabled = true;
        positionEl.textContent = 'X: 0, Y: 0';
    }
}

// 方向键控制
document.querySelectorAll('.dpad-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        const dir = btn.dataset.dir;
        const step = parseInt(document.getElementById('step-size').value);
        
        switch(dir) {
            case 'up':    sendCommand(`MOVE,Y,${step}`); break;
            case 'down':  sendCommand(`MOVE,Y,-${step}`); break;
            case 'left':  sendCommand(`MOVE,X,-${step}`); break;
            case 'right': sendCommand(`MOVE,X,${step}`); break;
            case 'home':  sendCommand('HOME'); break;
        }
    });
});

// 电磁铁控制
document.getElementById('mag-on').addEventListener('click', () => sendCommand('MAG,ON'));
document.getElementById('mag-off').addEventListener('click', () => sendCommand('MAG,OFF'));
document.getElementById('mag-pulse').addEventListener('click', () => sendCommand('MAG,PULSE,300'));

// 棋盘移动
document.getElementById('grid-go').addEventListener('click', () => {
    const row = document.getElementById('grid-row').value;
    const col = document.getElementById('grid-col').value;
    sendCommand(`GRID,ROW,${row},COL,${col}`);
});

// 互动片移动
document.getElementById('piece-move').addEventListener('click', () => {
    const fr = document.getElementById('from-row').value;
    const fc = document.getElementById('from-col').value;
    const tr = document.getElementById('to-row').value;
    const tc = document.getElementById('to-col').value;
    sendCommand(`PIECE,FROM,${fr},${fc},TO,${tr},${tc}`);
});

// 速度调节
speedSlider.addEventListener('input', () => {
    speedValue.textContent = speedSlider.value;
});
speedSlider.addEventListener('change', () => {
    sendCommand(`SPEED,${speedSlider.value}`);
});

// 调试终端
sendCmdBtn.addEventListener('click', () => {
    const cmd = cmdInput.value.trim();
    if (cmd) {
        sendCommand(cmd);
        cmdInput.value = '';
    }
});
cmdInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') sendCmdBtn.click();
});

// 连接/断开按钮
connectBtn.addEventListener('click', connect);
disconnectBtn.addEventListener('click', disconnect);

// 检查浏览器支持
if (!navigator.bluetooth) {
    log('警告: 当前浏览器不支持 Web Bluetooth', 'error');
    log('请使用 Chrome 或 Edge 浏览器，并确保已开启蓝牙', 'error');
    connectBtn.disabled = true;
}

log('控制端已就绪，请点击"连接设备"');
