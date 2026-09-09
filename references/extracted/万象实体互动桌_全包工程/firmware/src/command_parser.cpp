#include "command_parser.h"
#include <algorithm>
#include <cctype>

std::vector<std::string> CommandParser::parse(const std::string& command) {
    std::vector<std::string> tokens;
    std::string current;
    
    for (char c : command) {
        if (c == ',' || c == '\n' || c == '\r') {
            if (!current.empty()) {
                tokens.push_back(current);
                current.clear();
            }
        } else if (c != ' ') {
            current += c;
        }
    }
    if (!current.empty()) {
        tokens.push_back(current);
    }
    
    return tokens;
}

std::string CommandParser::getType(const std::string& command) {
    auto args = parse(command);
    if (args.empty()) return "";
    std::string type = args[0];
    std::transform(type.begin(), type.end(), type.begin(), ::toupper);
    return type;
}

std::string CommandParser::getArg(const std::vector<std::string>& args, const std::string& key) {
    for (size_t i = 0; i + 1 < args.size(); i += 2) {
        if (args[i] == key) {
            return args[i + 1];
        }
    }
    return "";
}

long CommandParser::getArgInt(const std::vector<std::string>& args, const std::string& key, long defaultValue) {
    std::string val = getArg(args, key);
    if (val.empty()) return defaultValue;
    try {
        return std::stol(val);
    } catch (...) {
        return defaultValue;
    }
}
