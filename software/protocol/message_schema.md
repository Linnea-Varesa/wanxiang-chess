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

## 约束

- `uid` 是物理棋子身份，不永久绑定 `role`。
- `square` 使用 `a1` 到 `h8`，与 FEN/UCI 兼容。
- `state_version` 递增；断线重连优先请求完整快照。
- `confidence` 低于阈值时进入 `UNSTABLE`，不提交走法。
- 设备完成运动或识别后必须回传 `cmd_id` 和结果。

