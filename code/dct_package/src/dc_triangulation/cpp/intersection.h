#pragma once
#include <vector>
#include <map>

typedef std::pair<int, int> Poss;
typedef std::pair<int, int> Edge;

std::map<Edge, std::vector<Edge>>
intersection(const std::vector<int> &indices, const std::vector<Poss> &point_pairs, const std::vector<Edge> &impossible_edges);

std::vector<std::set<Edge>> max_clique(std::map<Edge, std::vector<Edge>>);