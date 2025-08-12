#include "cadical_wrapper.h"
#include <fstream>
#include <sstream>
#include <iomanip>
#include <limits>
#include <filesystem>

#define PRINT 1 // Enable debug printing

// Constants for SVG visualization
const double SCALE_FACTOR = 100.0;
const double NODE_RADIUS = 5.0;

// Helper function to save arrangement as SVG file
void save_arrangement_as_svg(const Arrangement_2 &arr, const std::vector<Segment_2> &original_edges, const std::string &filename)
{
    // Create svg_figures directory if it doesn't exist
    std::filesystem::create_directories("svg_figures");

    // Construct full path with directory
    std::string full_path = "svg_figures/" + filename;

    std::ofstream svg_file(full_path);
    if (!svg_file.is_open())
    {
#if PRINT
        std::cerr << "Error: Could not open file " << full_path << " for writing." << std::endl;
#endif
        return;
    }

    // Calculate bounding box - use original edges if arrangement is empty
    double min_x = std::numeric_limits<double>::max();
    double max_x = std::numeric_limits<double>::lowest();
    double min_y = std::numeric_limits<double>::max();
    double max_y = std::numeric_limits<double>::lowest();

    bool has_arrangement_data = (arr.number_of_vertices() > 0);

    if (has_arrangement_data)
    {
        // Find bounds from arrangement vertices
        for (auto vit = arr.vertices_begin(); vit != arr.vertices_end(); ++vit)
        {
            double x = CGAL::to_double(vit->point().x()) * SCALE_FACTOR;
            double y = CGAL::to_double(vit->point().y()) * SCALE_FACTOR;
            min_x = std::min(min_x, x);
            max_x = std::max(max_x, x);
            min_y = std::min(min_y, y);
            max_y = std::max(max_y, y);
        }
    }
    else
    {
        // Find bounds from original edges
        for (const auto &edge : original_edges)
        {
            double x1 = CGAL::to_double(edge.source().x()) * SCALE_FACTOR;
            double y1 = CGAL::to_double(edge.source().y()) * SCALE_FACTOR;
            double x2 = CGAL::to_double(edge.target().x()) * SCALE_FACTOR;
            double y2 = CGAL::to_double(edge.target().y()) * SCALE_FACTOR;

            min_x = std::min({min_x, x1, x2});
            max_x = std::max({max_x, x1, x2});
            min_y = std::min({min_y, y1, y2});
            max_y = std::max({max_y, y1, y2});
        }
    }

    // Add some padding
    double padding = 50;
    double width = max_x - min_x + 2 * padding;
    double height = max_y - min_y + 2 * padding;

    // Ensure minimum size
    if (width < 200)
        width = 200;
    if (height < 200)
        height = 200;

    // Write SVG header
    svg_file << "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n";
    svg_file << "<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"" << width << "\" height=\"" << height << "\">\n";
    svg_file << "<rect width=\"100%\" height=\"100%\" fill=\"white\"/>\n";

    if (has_arrangement_data)
    {
        // Draw arrangement edges
        svg_file << "<g stroke=\"black\" stroke-width=\"1\" fill=\"none\">\n";
        for (auto eit = arr.edges_begin(); eit != arr.edges_end(); ++eit)
        {
            auto curve = eit->curve();
            double x1 = CGAL::to_double(curve.source().x()) * SCALE_FACTOR - min_x + padding;
            double y1 = CGAL::to_double(curve.source().y()) * SCALE_FACTOR - min_y + padding;
            double x2 = CGAL::to_double(curve.target().x()) * SCALE_FACTOR - min_x + padding;
            double y2 = CGAL::to_double(curve.target().y()) * SCALE_FACTOR - min_y + padding;

            // Flip y-coordinate for SVG (SVG has origin at top-left)
            y1 = height - y1;
            y2 = height - y2;

            svg_file << "<line x1=\"" << x1 << "\" y1=\"" << y1
                     << "\" x2=\"" << x2 << "\" y2=\"" << y2 << "\"/>\n";
        }
        svg_file << "</g>\n";

        // Draw vertices
        svg_file << "<g fill=\"red\">\n";
        for (auto vit = arr.vertices_begin(); vit != arr.vertices_end(); ++vit)
        {
            double x = CGAL::to_double(vit->point().x()) * SCALE_FACTOR - min_x + padding;
            double y = CGAL::to_double(vit->point().y()) * SCALE_FACTOR - min_y + padding;
            y = height - y; // Flip y-coordinate
            svg_file << "<circle cx=\"" << x << "\" cy=\"" << y << "\" r=\"" << NODE_RADIUS << "\"/>\n";
        }
        svg_file << "</g>\n";
    }
    else
    {
        // Draw original edges if arrangement is empty
        svg_file << "<g stroke=\"blue\" stroke-width=\"1\" fill=\"none\">\n";
        for (const auto &edge : original_edges)
        {
            double x1 = CGAL::to_double(edge.source().x()) * SCALE_FACTOR - min_x + padding;
            double y1 = CGAL::to_double(edge.source().y()) * SCALE_FACTOR - min_y + padding;
            double x2 = CGAL::to_double(edge.target().x()) * SCALE_FACTOR - min_x + padding;
            double y2 = CGAL::to_double(edge.target().y()) * SCALE_FACTOR - min_y + padding;

            // Flip y-coordinate for SVG
            y1 = height - y1;
            y2 = height - y2;

            svg_file << "<line x1=\"" << x1 << "\" y1=\"" << y1
                     << "\" x2=\"" << x2 << "\" y2=\"" << y2 << "\"/>\n";
        }
        svg_file << "</g>\n";

        // Draw endpoints
        svg_file << "<g fill=\"blue\">\n";
        for (const auto &edge : original_edges)
        {
            double x1 = CGAL::to_double(edge.source().x()) * SCALE_FACTOR - min_x + padding;
            double y1 = CGAL::to_double(edge.source().y()) * SCALE_FACTOR - min_y + padding;
            double x2 = CGAL::to_double(edge.target().x()) * SCALE_FACTOR - min_x + padding;
            double y2 = CGAL::to_double(edge.target().y()) * SCALE_FACTOR - min_y + padding;

            y1 = height - y1;
            y2 = height - y2;

            svg_file << "<circle cx=\"" << x1 << "\" cy=\"" << y1 << "\" r=\"" << NODE_RADIUS << "\"/>\n";
            svg_file << "<circle cx=\"" << x2 << "\" cy=\"" << y2 << "\" r=\"" << NODE_RADIUS << "\"/>\n";
        }
        svg_file << "</g>\n";
    }

    svg_file << "</svg>\n";
    svg_file.close();

#if PRINT
    std::cerr << "Arrangement saved as SVG to: " << full_path << std::endl;
    // std::cerr << "Vertices: " << arr.number_of_vertices()
    //           << ", Edges: " << arr.number_of_edges()
    //           << ", Faces: " << arr.number_of_faces() << std::endl;
    // std::cerr << "Original edges count: " << original_edges.size() << std::endl;
#endif
}

/**
 * Data structure to track the state of our observed literals.
 * May be generally useful to have, e.g., to be able to
 * both iterate over the fixed observe literals and query
 * their state in O(1) time with O(1) overhead per propagated literal.
 */
struct ObservedLiteralStateTracker
{
public:
    using Lit = cdc::CadicalSolver::Lit;

    ObservedLiteralStateTracker(bool save_states_lokal = false, std::vector<Point_raw> nodes = {}, std::vector<Edge_raw> edges = {}, std::unordered_map<std::string, int> nodes_to_sdegree = {}) : save_states(save_states_lokal), node_to_sdegree(nodes_to_sdegree)
    {
        for (const auto &edge : edges)
        {
            auto seg = Segment_2(Point_2(edge.first.first, edge.first.second), Point_2(edge.second.first, edge.second.second));
            this->edges.emplace_back(seg);
        }
        for (int i = 0; i < this->edges.size(); ++i)
        {
            std::string key = std::to_string(this->edges[i].source().x()) + "," +
                              std::to_string(this->edges[i].source().y()) + "," +
                              std::to_string(this->edges[i].target().x()) + "," +
                              std::to_string(this->edges[i].target().y());
            edge_to_index[key] = i + 1; // +1 to make it 1-based index
        }

        for (const auto &node : nodes)
        {
            this->nodes.push_back(Point_2(node.first, node.second));
        }
    }

    Segment_2 get_edge_from_lit(Lit lit) const
    {
        if (lit > edges.size())
        {
            throw std::logic_error("Edge index out of bounds for observed literal: " + std::to_string(lit));
        }
        return edges.at(lit - 1);
    }

    Lit get_lit_from_edge(const Segment_2 &edge) const
    {
        std::string key = std::to_string(edge.source().x()) + "," +
                          std::to_string(edge.source().y()) + "," +
                          std::to_string(edge.target().x()) + "," +
                          std::to_string(edge.target().y());
        auto it = edge_to_index.find(key);
        if (it != edge_to_index.end())
        {
            return Lit(0);
        }
        return it->second;
    }

    int get_sdegree_from_node(const Point_2 &node) const
    {
        std::string key = std::to_string(node.x()) + "," +
                          std::to_string(node.y());
        return node_to_sdegree.at(key);
    }
    void notify_backtrack(std::size_t new_level)
    {
        assert(new_level < level_indices.size() &&
               "Cannot backtrack to a non-existing decision level.");
        current_decision_level = new_level;
        std::size_t new_size = level_indices[new_level];
        for (auto it = observed_trail.begin() + new_size; it != observed_trail.end(); ++it)
        {
            std::size_t index = p_var_index(*it);
            observed_values[index] = false; // make open
        }
        observed_trail.resize(new_size);
        level_indices.resize(new_level);
        arr = arrangements[new_level];  // Restore the arrangement for the new level
        arrangements.resize(new_level); // Remove later levels
    }

    void notify_new_decision_level()
    {
        ++current_decision_level;
        level_indices.push_back(observed_trail.size());
        arrangements.push_back(arr); // Store the current arrangement
    }

    void notify_new_observed_var(Lit observed_var)
    {
        std::size_t index = p_var_index(observed_var);
        if (index + 1 >= observed_values.size())
        {
            std::size_t new_size = (std::max)(2 * observed_values.size() + 64, index + 2);
            observed_values.resize(new_size, false);
        }
    }

    void notify_new_observed_vars(const std::vector<Lit> &observed_vars)
    {
        set_observed_vars(observed_vars);
        Lit max_abs = *std::max_element(observed_vars.begin(), observed_vars.end(),
                                        [](Lit a, Lit b)
                                        {
                                            return std::abs(a) < std::abs(b);
                                        });
        notify_new_observed_var(max_abs);
    }

    /*

    Die Beiden Funktionieren funktionieren nicht.
    Sie werden drin gelassen falls ich das doch noch implementieren möchte.
    */
    // std::pair<Vertex_handle, Vertex_handle> get_vertex_handel_from_face(Arrangement_2::Face_handle face, const Point_2 &point1, const Point_2 &point2)
    // {
    //     std::pair<Vertex_handle, Vertex_handle> vertices;
    //     if (face->is_unbounded())
    //     {
    //         // Für unbounded faces gibt es keinen äußeren Rand im klassischen Sinne
    //         return vertices;
    //     }

    //     // Einen Halfedge des äußeren Rands bekommen
    //     Arrangement_2::Ccb_halfedge_circulator circ = face->outer_ccb();
    //     Arrangement_2::Ccb_halfedge_circulator start = circ;

    //     // Über alle Halfedges des äußeren Rands iterieren
    //     do
    //     {
    //         if (circ->source()->point() == point1)
    //         {
    //             vertices.first = circ->source();
    //         }
    //         else if (circ->source()->point() == point2)
    //         {
    //             vertices.second = circ->source();
    //         }
    //         ++circ;
    //     } while (circ != start);

    //     return vertices;
    // }

    // void insert_edge(const Segment_2 &edge)
    // {
    //     if (tracked_face == Face_handle())
    //     {
    //         CGAL::insert(arr, edge);
    //         auto count = std::distance(arr.faces_begin(), arr.faces_end());
    //         if (count == 2)
    //         {
    //             auto face = arr.faces_begin();
    //             if (face->is_unbounded())
    //             {
    //                 face = ++face; // Skip the unbounded face
    //             }
    //             tracked_face = face;
    //         }
    //     }
    //     else
    //     {
    //         auto vertices = get_vertex_handel_from_face(tracked_face, edge.source(), edge.target());
    //         if (vertices.first == Vertex_handle() || vertices.second == Vertex_handle())
    //         {
    //             // If the edge does not connect two vertices in the tracked face, insert it normally
    //             CGAL::insert(arr, edge);
    //         }
    //         else
    //         {
    //             // Otherwise, create a new halfedge and insert it into the arrangement
    //             auto new_halfedge = arr.insert_at_vertices(edge, vertices.first, vertices.second);
    //             if (new_halfedge != Halfedge_handle())
    //             {
    //                 Face_handle face = new_halfedge->face();
    //             }
    //             else
    //             {
    //                 std::cerr << "Failed to insert edge: " << edge.source() << " -> " << edge.target() << "\n";
    //                 throw std::runtime_error("Failed to insert edge into arrangement.");
    //             }
    //         }
    //     }
    // }

    void notify_assignments(const std::vector<Lit> &assignments)
    {
        for (Lit l : assignments)
        {
            if (is_open(l))
            {
                observed_trail.push_back(l);
                std::size_t index = p_var_index(l);
                assert(index + 1 < observed_values.size() && "Observed values vector is too small.");
                observed_values[index] = true;        // mark the variable as assigned
                observed_values[index + 1] = (l > 0); // store the value
                if (std::find(observed_vars.begin(), observed_vars.end(), l) != observed_vars.end())
                {
                    has_changes = true; // mark that we have changes
                }
            }
            else
            {
                assert(is_true(l) && "Trying to assign an already assigned observed literal.");
            }
        }

        // Check if any observed variables are found before printing
        bool found_observed = false;
        std::vector<Lit> observed_lits;

        for (Lit l : assignments)
        {
            if (std::find(observed_vars.begin(), observed_vars.end(), l) != observed_vars.end())
            {
                found_observed = true;
                observed_lits.push_back(l);

                // Insert the edge into the arrangement
                auto edge = get_edge_from_lit(l);
                // insert_edge(edge);
                CGAL::insert(arr, edge);
            }

            // Only print if observed variables were found
            if (found_observed)
            {
#if PRINT
                std::cerr << "Observed literals assigned: ";
                for (Lit l : observed_lits)
                {
                    std::cerr << l << " ";
                }
                std::cerr << "\n";
#endif
            }
        }
    }

    /**
     * Check if the observed literal is true under the current assignment.
     */
    bool is_true(Lit observed_lit) const
    {
        std::size_t index = p_var_index(observed_lit);
        return observed_values[index] & ((observed_lit > 0) == observed_values[index + 1]);
    }

    /**
     * Check if the observed literal is false under the current assignment.
     */
    bool is_false(Lit observed_lit) const
    {
        std::size_t index = p_var_index(observed_lit);
        return observed_values[index] & ((observed_lit > 0) == !observed_values[index + 1]);
    }

    /**
     * Check if the observed literal is open, i.e., not currently assigned.
     */
    bool is_open(Lit observed_lit) const
    {
        return !observed_values[p_var_index(observed_lit)];
    }

    /**
     * Get a list of currently fixed observed literals.
     */
    const std::vector<Lit> &get_observed_trail() const
    {
        return observed_trail;
    }

    void store_reason(Lit prop_lit, const std::vector<Lit> &reason)
    {
        reasons[prop_lit] = reason;
    }

    void get_reason(Lit prop_lit, std::vector<Lit> &reason)
    {
        auto it = reasons.find(prop_lit);
        if (it == reasons.end())
        {
            throw std::logic_error("No reason stored fo the propagated literal: " +
                                   std::to_string(prop_lit));
        }
        reason = it->second;
        reasons.erase(it);
    }

    void set_observed_vars(const std::vector<Lit> &observed_vars)
    {
        this->observed_vars = observed_vars;
    }
    std::vector<std::vector<int>> get_vars_saved()
    {
        return this->vars_saved;
    }
    void update_vars_saved()
    {
        if (!save_states)
        {
            return;
        }
        std::vector<int> result = {};
        for (auto l : observed_vars)
        {
            if (is_true(l))
            {
                result.push_back(1);
            }
            else if (is_false(l))
            {
                result.push_back(0);
            }
            else
            {
                result.push_back(-1); // -1 for open variables
            }
        }
        vars_saved.push_back(result);
    }

public:
    bool has_changes = false;
    std::vector<Lit> observed_vars;
    Arrangement_2 arr;
    Face_handle tracked_face; // Track the face with most edges

    static std::size_t p_var_index(Lit observed_lit)
    {
        std::size_t var_index = 2 * (std::abs(observed_lit) - 1);
        return var_index;
    }

    std::unordered_map<Lit, std::vector<Lit>> reasons;
    std::vector<std::size_t> level_indices;
    std::vector<Lit> observed_trail;
    std::vector<bool> observed_values;
    std::size_t current_decision_level{0};
    std::vector<std::vector<int>> vars_saved;
    bool save_states;
    std::vector<Arrangement_2> arrangements; // Store arrangements for each decision level
    std::vector<Segment_2> edges;
    std::unordered_map<std::string, Lit> edge_to_index;
    std::unordered_map<std::string, int> node_to_sdegree;
    std::vector<Point_2> nodes; // Store nodes for arrangement
};
/**
 * Trivial example propagator that enforces a simple list of additional clauses
 * on its observed variables.
 * Note that it uses a quite inefficient way of checking the clauses for unitness.
 */
class ExamplePropagator : public cdc::CadicalSolver::ExternalPropagator
{
public:
    using Lit = cdc::CadicalSolver::Lit;

    ExamplePropagator(cdc::CadicalSolver *solver, bool save_states = false, std::vector<Point_raw> nodes = {}, std::vector<Edge_raw> edges = {}, std::unordered_map<std::string, int> nodes_to_sdegree = {}) : cdc::CadicalSolver::ExternalPropagator(solver, true, false), state_tracker(save_states, nodes, edges, nodes_to_sdegree)
    {
    }

    void observe_variables(const std::vector<Lit> &observed_vars)
    {
        state_tracker.notify_new_observed_vars(observed_vars);
        for (Lit l : observed_vars)
        {
            observe(l);
        }
    }

    void notify_assignment(const std::vector<Lit> &lits) override
    {
        if (lits.empty())
        {
            return; // No assignments to notify
        }
        state_tracker.notify_assignments(lits);
        // std::cerr << "Current observed trail: ";
        // for (Lit l : state_tracker.get_observed_trail())
        // {
        //     std::cerr << l << " ";
        // }
        // std::cerr << "\n";
    }

    void notify_new_decision_level() override
    {
#if PRINT
        std::cerr << "New decision level started.\n";
#endif
        state_tracker.notify_new_decision_level();
    }

    void notify_backtrack(std::size_t new_level) override
    {
#if PRINT
        std::cerr << "Backtracking to level " << new_level << "\n";
#endif
        state_tracker.notify_backtrack(new_level);
    }

    /**
     * Add a hidden clause to the propagator, which it will
     * give to the SAT solver during propagation.
     */
    void add_hidden_clause(const std::vector<Lit> &clause)
    {
        hidden_clauses.push_back(clause);
    }

    int propagate() override
    {
        if (!state_tracker.has_changes)
        {
            return 0; // Keine Änderungen - früher Ausstieg
        }

        state_tracker.has_changes = false; // Flag zurücksetzen

        state_tracker.update_vars_saved();
        // std::cerr << "PROPAGATE called with observed trail ";
        // for (Lit l : state_tracker.get_observed_trail())
        // {
        //     std::cerr << l << " ";
        // }
        // std::cerr << "\n";

        // Arrangement-Informationen ausgeben
        std::stringstream filename;
        filename << "arrangement_" << std::setfill('0') << std::setw(4) << arrangement_counter++ << ".svg";
        save_arrangement_as_svg(state_tracker.arr, state_tracker.edges, filename.str());

        for (auto face = state_tracker.arr.faces_begin(); face != state_tracker.arr.faces_end(); ++face)
        {
            if (face->is_unbounded())
                continue; // Unbounded faces are not interesting

            // Count outer halfedges using circulator
            int outer_halfedges_count = 0;
            auto circ = face->outer_ccb();
            auto start = circ;
            std::vector<Point_2> hull_vertices;
            do
            {
                outer_halfedges_count++;
                ++circ;
            } while (circ != start);

            if (outer_halfedges_count <= 3)
                continue; // Skip faces with 3 or fewer edges
#if PRINT
            std::cerr << "Anzahl der Kanten: " << outer_halfedges_count << "\n";
#endif
            std::vector<Query_result> inside_points;
            locate(state_tracker.arr, state_tracker.nodes.begin(), state_tracker.nodes.end(), std::back_inserter(inside_points));
            std::vector<Point_2> vertices;
            for (const auto &result : inside_points)
            {
                vertices.push_back(result.first);
            }

            Point_2 p1(0, 0);
            Point_2 p2(5, 0);
            Segment_2 segment(p1, p2);

            Point_2 test_point(2, 3); // Punkt oberhalb des Segments

            int max_face_vertices = vertices.size();
            // Generate all possible edges between vertices
            auto handel_half = [&](const std::vector<Point_2> &points, int k)
            {
                int n = points.size();
                int degree_count = 0;
                for (const auto &v : points)
                {
                    int degree = state_tracker.get_sdegree_from_node(v);
                    degree_count += degree;
                    if (std::find(hull_vertices.begin(), hull_vertices.end(), v) != hull_vertices.end())
                    {
                        continue; // Skip hull vertices
                    }
                    if (degree > n - 1)
                    {
                        return true; // If any vertex has a degree greater than n-1, return true
                    }
                }
                if ((3 * n - 3 - k) * 2 > degree_count)
                {
                    return true; // If the degree count is less than 2 * edge_count, return true
                }
                return false;
            };
            for (size_t x = 0; x < hull_vertices.size(); ++x)
            {
                for (size_t y = x + 1; y < hull_vertices.size(); ++y)
                {
                    int k_one, k_two = 0;
                    std::vector<Point_2> half_one;
                    std::vector<Point_2> half_two;
                    for (const auto &v : vertices)
                    {
                        CGAL::Orientation orient = CGAL::orientation(hull_vertices[x], hull_vertices[y], v);
                        if (orient == CGAL::LEFT_TURN)
                        {
                            half_one.push_back(v);
                            if (std::find(hull_vertices.begin(), hull_vertices.end(), v) != hull_vertices.end())
                            {
                                k_one++;
                            }
                        }
                        else if (orient == CGAL::RIGHT_TURN)
                        {
                            half_two.push_back(v);
                            if (std::find(hull_vertices.begin(), hull_vertices.end(), v) != hull_vertices.end())
                            {
                                k_two++;
                            }
                        }
                        else
                        {
                            half_one.push_back(v);
                            half_two.push_back(v);
                        }
                        if (handel_half(half_one, k_one) || handel_half(half_two, k_two))
                        {
                            auto edge = Segment_2(hull_vertices[x], hull_vertices[y]);
                            // #if PRINT

                            std::cerr << "can exclude edge: " << hull_vertices[x] << " - " << hull_vertices[y] << "\n";
                            // #endif
                            auto lit = state_tracker.get_lit_from_edge(edge);
                            if (lit == Lit(0))
                            {
                                continue; // Edge not found, skip
                            }
                            std::vector<Lit> reason;
                            for (Lit l : state_tracker.get_observed_trail())
                            {
                                if (l > 0)
                                {
                                    reason.push_back(-l);
                                }
                            }
                            reason.push_back(-lit);
                            state_tracker.store_reason(-lit, reason);
                            return -lit; // Return the literal for the edge that can be excluded
                        }
                    }
                }
            }
        }

        return 0;
    }

    void get_reason_clause(Lit propagated_lit, std::vector<Lit> &reason_buffer) override
    {
#if PRINT
        std::cerr << "Getting reason clause for propagated literal: " << propagated_lit << "\n";
#endif
        state_tracker.get_reason(propagated_lit, reason_buffer);
    }

    std::vector<std::vector<int>> get_vars_saved()
    {
        return state_tracker.get_vars_saved();
    }

private:
    ObservedLiteralStateTracker state_tracker;
    std::vector<std::vector<Lit>> hidden_clauses;
    static int arrangement_counter;
    int edgges_set_to_false_counter = 0;
};

int ExamplePropagator::arrangement_counter = 0;

std::pair<Vars_List, std::vector<Vars_List>> cadical_wrapper(int number_vars,
                                                             int number_edges_vars,
                                                             std::vector<Vars_List> clauses,
                                                             std::vector<Point_raw> nodes,
                                                             std::vector<Edge_raw> edges,
                                                             std::unordered_map<std::string, int> node_to_sdegree,
                                                             bool save_state,
                                                             bool optimize_propagation)
{
    // if (optimize_propagation)
    // {
    //     assert(!edges.empty() && "Edges must be provided when optimize_propagation is true.");
    // }
    assert(!edges.empty() && "Edges must be provided when optimize_propagation is true.");
    cdc::CadicalSolver solver;
    std::vector<cdc::CadicalSolver::Lit> v;
    for (int i = 0; i < number_vars; ++i)
    {
        v.push_back(solver.new_var());
    }
    // add the negated version of each clause directly to the solver
    for (const auto &clause : clauses)
    {
        for (auto l : clause)
        {
            if (l > 0)
            {
                // std::cout << "Adding literal: " << v.at(l - 1) << "\n";
                solver.add_literal(v.at(l - 1));
            }
            else
            {
                // std::cout << "Adding negated literal: " << -v.at((-1 * l) - 1) << "\n";
                solver.add_literal(-v.at((-1 * l) - 1));
            }
        }
        // std::cout << "Finishing clause with 0\n";
        solver.finish_clause();
    }

    // add the propagator
    auto &propagator = solver.emplace_external_propagator<ExamplePropagator>(&solver, save_state, nodes, edges, node_to_sdegree);
    // observe the variables (must be AFTER the constructor)
    propagator.observe_variables(std::vector<cdc::CadicalSolver::Lit>(v.begin(), v.begin() + number_edges_vars));
    // for (const auto &clause : clauses)
    // {
    //     // add the clauses to the propagator
    //     propagator.add_hidden_clause(clause);
    // }
    auto result = solver.solve();
    if (!result || !*result)
    {
        // #if PRINT
        std::cerr << "No solution found\n";
        // #endif
        return std::make_pair(Vars_List{}, std::vector<Vars_List>{});
    }
    else
    {
        // #if PRINT
        std::cout << "Solution found\n";
        // #endif
        auto model = solver.get_model();
        std::vector<int> result = {};
        for (auto l : v)
        {
            if (model[l])
            {
                result.push_back(1);
            }
            else
            {
                result.push_back(0);
            }
        }

        return std::make_pair(result, propagator.get_vars_saved());
    }
}
