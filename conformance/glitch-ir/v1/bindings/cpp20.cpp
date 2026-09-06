#include <fstream>
#include <iostream>
#include <stdexcept>
#include <string>
#include <unordered_map>

std::unordered_map<std::string, std::string> load(const std::string& path) {
    std::ifstream input(path);
    if (!input) {
        throw std::runtime_error("cannot open vector");
    }
    std::unordered_map<std::string, std::string> values;
    std::string line;
    while (std::getline(input, line)) {
        if (line.empty()) continue;
        const auto pos = line.find('=');
        if (pos == std::string::npos || pos == 0) {
            throw std::runtime_error("invalid vector line");
        }
        values.emplace(line.substr(0, pos), line.substr(pos + 1));
    }
    return values;
}

int main(int argc, char** argv) {
    if (argc != 2) {
        std::cerr << "usage: cpp20 VECTOR\n";
        return 2;
    }

    const auto v = load(argv[1]);
    const bool backtrace =
        (v.at("verification_label") == "PRESENT" && v.at("evidence") != "PRESENT") ||
        v.at("source") == "UNKNOWN";

    const std::string verdict = backtrace ? "BACKTRACE" : "ACCEPT";
    const std::string op = backtrace ? "GLT-0036" : "NONE";
    const std::string state = backtrace ? "CONTESTED" : "ACCEPTED";

    std::cout << v.at("vector_id") << '|'
              << v.at("protocol_version") << '|'
              << verdict << '|'
              << op << '|'
              << state << '\n';
}
