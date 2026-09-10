# 协议测试样例

## 识别事件

```text
EVENT,LIFT,UID,p01,SQUARE,e2,SEQ,91
EVENT,PLACE,UID,p01,SQUARE,e4,SEQ,92
```

预期：主机在连续帧稳定前保持 `UNSTABLE`；确认后才生成一次棋局变更。

## 无视觉逐格身份扫描

```text
IDSCAN,CH,0,UID,0102030405060701
IDSCAN,CH,1,EMPTY
IDSCAN,CH,2,CRC_ERROR
OK,ID_SCAN_DONE
```

预期：Android 使用通道映射表换算格位；`CRC_ERROR` 不覆盖已有快照，`EMPTY → UID → EMPTY` 的变化只有在去抖后才形成落子事件。

## 重同步

```text
SNAPSHOT?,CMD,42
SNAPSHOT,STATE,12,P01:e4,P17:g8
```

预期：主机丢弃过期增量，使用状态版本 12 的完整快照重建局面。

## 错误

```text
ERR,CMD,44,CODE,NOT_STABLE
ERR,CMD,45,CODE,RANGE
ERR,CMD,46,CODE,TIMEOUT
```

预期：界面显示可恢复错误，不能自动把命令标记为完成。
