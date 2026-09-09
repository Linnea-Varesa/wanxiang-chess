# 协议测试样例

## 识别事件

```text
EVENT,LIFT,UID,p01,SQUARE,e2,SEQ,91
EVENT,PLACE,UID,p01,SQUARE,e4,SEQ,92
```

预期：主机在连续帧稳定前保持 `UNSTABLE`；确认后才生成一次棋局变更。

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

