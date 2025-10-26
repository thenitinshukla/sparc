#include <random>
#include <chrono>

// Simple random number generator
static std::mt19937 gen(std::chrono::high_resolution_clock::now().time_since_epoch().count());

double randDouble(double min, double max) {
    std::uniform_real_distribution<double> dis(min, max);
    return dis(gen);
}

int randInt(int min, int max) {
    std::uniform_int_distribution<int> dis(min, max);
    return dis(gen);
}