#ifndef COMMAND_PARSER_H
#define COMMAND_PARSER_H

#include <string>
#include <vector>

class CommandParser {
public:
    // 解析逗号分隔的指令，返回参数列表
    // 例如 "MOVE,X,200,Y,-100" -> ["MOVE", "X", "200", "Y", "-100"]
    static std::vector<std::string> parse(const std::string& command);
    
    // 获取指令类型（第一个参数，大写）
    static std::string getType(const std::string& command);
    
    // 获取指定参数的值
    // 例如 getArg(args, "X") -> "200"
    static std::string getArg(const std::vector<std::string>& args, const std::string& key);
    
    // 获取整数参数
    static long getArgInt(const std::vector<std::string>& args, const std::string& key, long defaultValue = 0);
};

#endif // COMMAND_PARSER_H
