# 消息字段约定

V1 使用同一套字段语义承载串口和 BLE。传输层可以不同，业务层不应不同。

## 棋子快照

```json
{
  "protocol_version": 1,
  "device_id": "wx-001",
  "game_id": "game-20260909-001",
  "state_version": 12,
  "pieces": [
    {"uid": "p01", "side": "white", "role": "king", "square": "e1", "confidence": 0.99},
    {"uid": "p17", "side": "black", "role": "knight", "square": "g8", "confidence": 0.97}
  ],
  "observed_at": "2026-09-09T12:00:00Z"
}
```

首版无视觉固件也可以用按格事件表达同一语义：

```text
IDSCAN,STATE,12,CH,0,UID,0102030405060701
IDSCAN,STATE,12,CH,1,EMPTY
IDSCAN,STATE,12,CH,2,CRC_ERROR
```

`CH` 是硬件通道，Android 根据棋盘布线表映射成 `a1` 到 `h8`。`UID` 来自 DS2431 或 DS2401 的 64-bit ROM；`EMPTY` 表示该格没有建立可靠接触，`CRC_ERROR` 不得用于推进棋局。

## 约束

- `uid` 是物理棋子身份，不永久绑定 `role`。
- `square` 使用 `a1` 到 `h8`，与 FEN/UCI 兼容。
- `state_version` 递增；断线重连优先请求完整快照。
- `confidence` 低于阈值时进入 `UNSTABLE`，不提交走法。
- 身份触点短暂断开、源格和目标格同时变化或 CRC 错误时进入 `UNSTABLE`，等待稳定快照。
- 设备完成运动或识别后必须回传 `cmd_id` 和结果。
