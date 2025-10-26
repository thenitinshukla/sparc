#include <cstdlib>
#include <iostream>
#include <vector>
#include <string>
#include <algorithm>
#include <cctype>
#include <cstring>

void printArray(const std::vector<double>& array) {
    for (size_t i = 0; i < array.size(); i++) {
        std::cout << array[i] << " ";
    }
    std::cout << std::endl;
}

void trim(std::string& str) {
    // Remove leading whitespace
    str.erase(str.begin(), std::find_if(str.begin(), str.end(), [](unsigned char ch) {
        return !std::isspace(ch);
    }));
    
    // Remove trailing whitespace
    str.erase(std::find_if(str.rbegin(), str.rend(), [](unsigned char ch) {
        return !std::isspace(ch);
    }).base(), str.end());
}

bool parseLine(const std::string& line, const std::string& param, double* value) {
    if (line.find(param) != std::string::npos) {
        size_t pos = line.find("=");
        if (pos != std::string::npos) {
            *value = std::stod(line.substr(pos + 1));
            return true;
        }
    }
    return false;
}

double randDouble() {
    return (double)rand() / RAND_MAX;
}