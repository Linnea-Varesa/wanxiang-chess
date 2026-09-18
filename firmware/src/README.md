# 固件源码

包含 BLE、命令解析、身份扫描、运动和电磁铁模块。三个月主线使用 [`identity_grid.cpp`](identity_grid.cpp) 读取 DS2431/DS2401 的 ROM UID；DS2431 EEPROM 写入工具单独开发，运动源码保留作后续台架，不代表自动移子已完成。
