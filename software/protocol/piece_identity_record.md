# 棋子身份芯片 EEPROM 记录

此文件定义 DS2431 EEPROM 的初始写入格式。它只描述出厂/装配信息，不取代 Android 的运行时棋局状态。文件路径相对于仓库根目录；与字段模型的关系见 [`../controller/models.py`](../controller/models.py)，器件依据见 [`../../docs/16_触点对自动移子影响与身份器件决策.md`](../../docs/16_触点对自动移子影响与身份器件决策.md)。

## 第一页前 16 字节

| 偏移 | 长度 | 字段 | 说明 |
|---:|---:|---|---|
| 0 | 2 | magic | ASCII `WX` |
| 2 | 1 | schema_version | 当前为 `1` |
| 3 | 1 | side | `0` 未绑定，`1` 白，`2` 黑 |
| 4 | 1 | initial_role | `1` 王、`2` 后、`3` 车、`4` 象、`5` 马、`6` 兵 |
| 5 | 1 | piece_number | 同色棋子编号，备用棋子也必须唯一 |
| 6 | 2 | board_revision | 棋子写入时的机械/协议版本 |
| 8 | 4 | batch_id | 本批棋子或实验批次编号 |
| 12 | 2 | payload_crc16 | 对偏移 0–11 计算的 CRC16 |
| 14 | 2 | reserved | 写 `0xFF`，供后续使用 |

DS2431 的 ROM UID 不写入 EEPROM，读取后作为记录主键。EEPROM 写入完成后必须整页读回，校验 `magic`、范围和 CRC；写失败的芯片不得装入棋子。

## 运行时规则

- `initial_role` 只是装配时角色；兵升变后，Android 状态机更新当前角色，不回写芯片。
- `side=0` 的备用棋子必须在 APP 登记时明确绑定，不能根据所在格猜颜色。
- 运行时快照仍传 UID、格位和置信度，字段见 [`message_schema.md`](message_schema.md)。
- 写入工具必须使用独立接触座和强上拉，禁止在 64 格扫描期间写 EEPROM。
