
#include <iostream>
#include "intersection.h"

using namespace std;
std::vector<std::pair<int, int>> two_combinations(int max_index)
{
    std::vector<std::pair<int, int>> result;

    // Generate all combinations of 2 elements
    for (int i = 0; i < max_index + 1; ++i)
    {
        for (int j = i + 1; j < max_index + 1; ++j)
        {
            result.push_back(std::make_pair(i, j));
        }
    }
    return result;
}

int sign(int x)
{
    return (x > 0) - (x < 0); // Returns 1 for positive, -1 for negative, and 0 for zero
}

int orientation(std::pair<int, int> p1, std::pair<int, int> p2, std::pair<int, int> p3)
{
    return sign((p2.first - p1.first) * (p3.second - p1.second) -
                (p2.second - p1.second) * (p3.first - p1.first));
}

// Updated function to return a map of pairs to sets of pairs
// (equivalent to Python dict[tuple[int, int], set[tuple[int, int]]])
std::map<Edge, std::vector<Edge>>
intersection(const std::vector<int> &indices, const std::vector<Poss> &point_pairs, const std::vector<Edge> &impossible_edges)
{
    // Placeholder for intersection logic
    // Create a result map to return
    std::map<Edge, std::vector<Edge>> result;

    auto combinations = two_combinations(point_pairs.size() - 1);
    for (auto [node1, node2] : combinations)
    {
        // Check if the two points are distinct
        auto edge1 = std::make_pair(min(indices.at(node1), indices.at(node2)),
                                    max(indices.at(node1), indices.at(node2)));

        if (std::find(impossible_edges.begin(), impossible_edges.end(), edge1) != impossible_edges.end())
        {
            continue;
        }

        for (int current_node = 0; current_node < point_pairs.size(); ++current_node)
        {
            if (current_node == node1 || current_node == node2)
            {
                continue; // Skip the nodes that form the edge
            }
            auto orientation_node1_node2_current = orientation(
                point_pairs[node1],
                point_pairs[node2],
                point_pairs[current_node]);
            for (int remaining_node = current_node + 1; remaining_node < point_pairs.size(); ++remaining_node)
            {
                // alle edges benötigt die größere Menge, intersection würde die kleinere Reichen.
                // TODO testen ob intersection durch größere Menge schneller wird
                // if (
                //     remaining_node == node1 || remaining_node == node2 || std::tie(node1, node2) < std::tie(current_node, remaining_node))
                // {
                //     continue; // Skip the nodes that form the edge or already processed
                // }
                if (
                    remaining_node == node1 || remaining_node == node2)
                {
                    continue; // Skip the nodes that form the edge or already processed
                }

                auto orientation_node1_node2_remaining = orientation(
                    point_pairs[node1],
                    point_pairs[node2],
                    point_pairs[remaining_node]);
                if (orientation_node1_node2_current == orientation_node1_node2_remaining)
                {
                    continue; // Skip if the orientations are the same
                }
                auto orientation_current_remaining_node1 = orientation(
                    point_pairs[current_node],
                    point_pairs[remaining_node],
                    point_pairs[node1]);
                auto orientation_current_remaining_node2 = orientation(
                    point_pairs[current_node],
                    point_pairs[remaining_node],
                    point_pairs[node2]);
                if (
                    orientation_current_remaining_node1 == orientation_current_remaining_node2)
                {
                    continue;
                }
                auto edge2 = std::make_pair(min(indices.at(current_node), indices.at(remaining_node)),
                                            max(indices.at(current_node), indices.at(remaining_node)));
                if (std::find(impossible_edges.begin(), impossible_edges.end(), edge2) != impossible_edges.end())
                {
                    continue;
                }
                result[edge1].push_back(edge2);
            }
        }
    }
    return result;
}
