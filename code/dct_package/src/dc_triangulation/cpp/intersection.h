#pragma once
#include <vector>
#include <map>

std::map<std::pair<int, int>, std::vector<std::pair<int, int>>>
intersection(const std::vector<int> &indices, const std::vector<std::pair<int, int>> &point_pairs);