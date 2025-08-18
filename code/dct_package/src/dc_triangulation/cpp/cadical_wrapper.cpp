#include "cadical_wrapper.h"
#include <fstream>
#include <sstream>
#include <iomanip>
#include <limits>
#include <filesystem>

#define PRINT 0 // Enable debug printing

// Constants for SVG visualization
// const double SCALE_FACTOR = 100.0;
// const double SCALE_FACTOR = 1;
const double SCALE_FACTOR = 0.1;
const double NODE_RADIUS = 5.0;
static int counter = 0;
static int gesamt_counter = 0;

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
            double x = static_cast<int>(CGAL::to_double(vit->point().x())) * SCALE_FACTOR;
            double y = static_cast<int>(CGAL::to_double(vit->point().y())) * SCALE_FACTOR;
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
            double x1 = static_cast<int>(CGAL::to_double(edge.source().x())) * SCALE_FACTOR;
            double y1 = static_cast<int>(CGAL::to_double(edge.source().y())) * SCALE_FACTOR;
            double x2 = static_cast<int>(CGAL::to_double(edge.target().x())) * SCALE_FACTOR;
            double y2 = static_cast<int>(CGAL::to_double(edge.target().y())) * SCALE_FACTOR;

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
            double x1 = static_cast<int>(CGAL::to_double(curve.source().x())) * SCALE_FACTOR - min_x + padding;
            double y1 = static_cast<int>(CGAL::to_double(curve.source().y())) * SCALE_FACTOR - min_y + padding;
            double x2 = static_cast<int>(CGAL::to_double(curve.target().x())) * SCALE_FACTOR - min_x + padding;
            double y2 = static_cast<int>(CGAL::to_double(curve.target().y())) * SCALE_FACTOR - min_y + padding;

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
            double x = static_cast<int>(CGAL::to_double(vit->point().x())) * SCALE_FACTOR - min_x + padding;
            double y = static_cast<int>(CGAL::to_double(vit->point().y())) * SCALE_FACTOR - min_y + padding;
            y = height - y; // Flip y-coordinate
            svg_file << "<circle cx=\"" << x << "\" cy=\"" << y << "\" r=\"" << NODE_RADIUS << "\"/>\n";

            // Add coordinate labels
            double coord_x = static_cast<int>(CGAL::to_double(vit->point().x()));
            double coord_y = static_cast<int>(CGAL::to_double(vit->point().y()));
            svg_file << "<text x=\"" << (x + NODE_RADIUS + 2) << "\" y=\"" << (y - NODE_RADIUS - 2)
                     << "\" font-family=\"Arial\" font-size=\"10\" fill=\"black\">("
                     << coord_x << "," << coord_y << ")</text>\n";
        }
        svg_file << "</g>\n";
    }
    else
    {
        // Draw original edges if arrangement is empty
        svg_file << "<g stroke=\"blue\" stroke-width=\"1\" fill=\"none\">\n";
        for (const auto &edge : original_edges)
        {
            double x1 = static_cast<int>(CGAL::to_double(edge.source().x())) * SCALE_FACTOR - min_x + padding;
            double y1 = static_cast<int>(CGAL::to_double(edge.source().y())) * SCALE_FACTOR - min_y + padding;
            double x2 = static_cast<int>(CGAL::to_double(edge.target().x())) * SCALE_FACTOR - min_x + padding;
            double y2 = static_cast<int>(CGAL::to_double(edge.target().y())) * SCALE_FACTOR - min_y + padding;

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
            double x1 = static_cast<int>(CGAL::to_double(edge.source().x())) * SCALE_FACTOR - min_x + padding;
            double y1 = static_cast<int>(CGAL::to_double(edge.source().y())) * SCALE_FACTOR - min_y + padding;
            double x2 = static_cast<int>(CGAL::to_double(edge.target().x())) * SCALE_FACTOR - min_x + padding;
            double y2 = static_cast<int>(CGAL::to_double(edge.target().y())) * SCALE_FACTOR - min_y + padding;

            y1 = height - y1;
            y2 = height - y2;

            svg_file << "<circle cx=\"" << x1 << "\" cy=\"" << y1 << "\" r=\"" << NODE_RADIUS << "\"/>\n";
            svg_file << "<circle cx=\"" << x2 << "\" cy=\"" << y2 << "\" r=\"" << NODE_RADIUS << "\"/>\n";

            // Add coordinate labels for endpoints
            double coord_x1 = static_cast<int>(CGAL::to_double(edge.source().x()));
            double coord_y1 = static_cast<int>(CGAL::to_double(edge.source().y()));
            double coord_x2 = static_cast<int>(CGAL::to_double(edge.target().x()));
            double coord_y2 = static_cast<int>(CGAL::to_double(edge.target().y()));

            svg_file << "<text x=\"" << (x1 + NODE_RADIUS + 2) << "\" y=\"" << (y1 - NODE_RADIUS - 2)
                     << "\" font-family=\"Arial\" font-size=\"10\" fill=\"black\">("
                     << coord_x1 << "," << coord_y1 << ")</text>\n";
            svg_file << "<text x=\"" << (x2 + NODE_RADIUS + 2) << "\" y=\"" << (y2 - NODE_RADIUS - 2)
                     << "\" font-family=\"Arial\" font-size=\"10\" fill=\"black\">("
                     << coord_x2 << "," << coord_y2 << ")</text>\n";
        }
        svg_file << "</g>\n";
    }

    svg_file << "</svg>\n";
    svg_file.close();

#if PRINT
    // std::cerr << "Arrangement saved as SVG to: " << full_path << std::endl;
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

    ObservedLiteralStateTracker(bool save_states_lokal = false, std::vector<Point_raw> nodes = {}, std::vector<Edge_raw> edges = {}, std::unordered_map<std::string, int> nodes_to_sdegree = {}, std::unordered_map<int, std::vector<int>> intersections = {}) : save_states(save_states_lokal), node_to_sdegree(nodes_to_sdegree), intersections(intersections)
    {
        for (const auto &edge : edges)
        {
            auto seg = Segment_2(Point_2(edge.first.first, edge.first.second), Point_2(edge.second.first, edge.second.second));
            this->edges.emplace_back(seg);
        }
        for (int i = 0; i < this->edges.size(); ++i)
        {
            std::string key = std::to_string(static_cast<int>(CGAL::to_double(this->edges[i].source().x()))) + "," +
                              std::to_string(static_cast<int>(CGAL::to_double(this->edges[i].source().y()))) + "," +
                              std::to_string(static_cast<int>(CGAL::to_double(this->edges[i].target().x()))) + "," +
                              std::to_string(static_cast<int>(CGAL::to_double(this->edges[i].target().y())));
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
        std::string key = std::to_string(static_cast<int>(CGAL::to_double(edge.source().x()))) + "," +
                          std::to_string(static_cast<int>(CGAL::to_double(edge.source().y()))) + "," +
                          std::to_string(static_cast<int>(CGAL::to_double(edge.target().x()))) + "," +
                          std::to_string(static_cast<int>(CGAL::to_double(edge.target().y())));

        auto it = edge_to_index.find(key);
        if (it != edge_to_index.end())
        {
            return it->second;
        }
        key = std::to_string(static_cast<int>(CGAL::to_double(edge.target().x()))) + "," +
              std::to_string(static_cast<int>(CGAL::to_double(edge.target().y()))) + "," +
              std::to_string(static_cast<int>(CGAL::to_double(edge.source().x()))) + "," +
              std::to_string(static_cast<int>(CGAL::to_double(edge.source().y())));

        it = edge_to_index.find(key);
        if (it != edge_to_index.end())
        {
            return it->second;
        }
        return Lit(0);
    }

    int get_sdegree_from_node(const Point_2 &node) const
    {
        std::string key = std::to_string(static_cast<int>(CGAL::to_double(node.x()))) + "," +
                          std::to_string(static_cast<int>(CGAL::to_double(node.y())));
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
        // std::cerr << "Notify assignments" << counter++ << "    last literal: " << assignments.at(assignments.size() - 1) << "\n";
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
                CGAL::insert(arr, edge);
#if PRINT
                // std::cerr << "Inserting edge: " << edge << "for lit: " << l << "for counter: " << counter << "\n";
#endif
            }

            // Only print if observed variables were found
            if (found_observed)
            {
#if PRINT
                // std::cerr << "Observed literals assigned: ";
                // for (Lit l : observed_lits)
                // {
                //     std::cerr << l << " ";
                // }
                // std::cerr << "\n";
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
    std::unordered_map<int, std::vector<int>> intersections;
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

    ExamplePropagator(cdc::CadicalSolver *solver, bool save_states = false, std::vector<Point_raw> nodes = {}, std::vector<Edge_raw> edges = {}, std::unordered_map<std::string, int> nodes_to_sdegree = {}, std::unordered_map<int, std::vector<int>> intersections = {}) : cdc::CadicalSolver::ExternalPropagator(solver, true, false), state_tracker(save_states, nodes, edges, nodes_to_sdegree, intersections)
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
        // std::cerr << "New decision level started." << std::endl;
#endif
        state_tracker.notify_new_decision_level();
    }

    void notify_backtrack(std::size_t new_level) override
    {
#if PRINT
        // std::cerr << "Backtracking to level " << new_level << std::endl;
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
        gesamt_counter++;
#if PRINT
        // std::cerr << "Propergate" << std::endl;
#endif
        if (!state_tracker.has_changes)
        {
            return 0; // Keine Änderungen - früher Ausstieg
        }

        state_tracker.has_changes = false; // Flag zurücksetzen

        state_tracker.update_vars_saved();
        // std::cerr << "PROPAGATE called with observed trail "
        // for (Lit l : state_tracker.get_observed_trail())
        // {
        //     std::cerr << l << " ";
        // }
        // std::cerr << "\n";

        // Arrangement-Informationen ausgeben

        std::vector<Query_result> point_lokations;
        locate(state_tracker.arr, state_tracker.nodes.begin(), state_tracker.nodes.end(), std::back_inserter(point_lokations));

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
                hull_vertices.push_back(circ->source()->point()); // Add hull vertex
                ++circ;
            } while (circ != start);

            if (outer_halfedges_count <= 3)
                continue; // Skip faces with 3 or fewer edges

            std::vector<Point_2> inner_vertices;
            // Populate vertices with points that lie in the current face using point_lokations
            for (auto &result : point_lokations)
            {
                if (std::holds_alternative<Face_const_handle>(result.second))
                {
                    if (std::get<Face_const_handle>(result.second) == face)
                    {
                        inner_vertices.push_back(result.first);
                    }
                }
                if (std::holds_alternative<Halfedge_const_handle>(result.second))
                {
                    std::cerr << "Point " << result.first << " is on a halfedge, not a face." << std::endl;
                    assert(false && "Point is on a halfedge, not a face.");
                }
                if (std::holds_alternative<Vertex_const_handle>(result.second))
                {
                    auto vertex = std::get<Vertex_const_handle>(result.second);
                    // Check if any incident face matches the target face
                    bool vertex_in_face = false;
                    if (!vertex->is_isolated())
                    {
                        auto circ = vertex->incident_halfedges();
                        auto start = circ;
                        do
                        {
                            if (circ->face() == face || circ->twin()->face() == face)
                            {
                                vertex_in_face = true;
                                break;
                            }
                            ++circ;
                        } while (circ != start);
                    }
                    if (find(hull_vertices.begin(), hull_vertices.end(), result.first) != hull_vertices.end())
                    {
                        continue; // Skip if the vertex is already in the hull vertices
                    }
                    if (vertex_in_face)
                    {
                        inner_vertices.push_back(result.first);
                    }
                }
            }

            // Generate all possible edges between vertices
            auto handel_half = [&](const std::vector<Point_2> &i_points, const std::vector<Point_2> &h_points, std::stringstream &info) -> bool
            {
                int k = h_points.size();
                int n = i_points.size() + k; // Total number of vertices
                int degree_count = 0;
                for (const auto &v : i_points)
                {
                    int degree = state_tracker.get_sdegree_from_node(v);
                    degree_count += degree;
                    if (degree > n - 1)
                    {
#if PRINT
                        info << "Vertex " << v << " has degree " << degree << ", which is greater than n-1 (" << n - 1 << ")." << "\n";
#endif
                        return true; // If any vertex has a degree greater than n-1, return true
                    }
                }
                for (const auto &v : h_points)
                {
                    int degree = state_tracker.get_sdegree_from_node(v);
                    degree_count += degree;
                }
                if ((3 * n - 3 - k) * 2 > degree_count)
                {
#if PRINT
                    info << "Degree count " << degree_count << " is less than 2 * edge count " << (2 * (n - 1)) << "." << "\n";
#endif
                    return true; // If the degree count is less than 2 * edge_count, return true
                }
                return false;
            };
            for (size_t x = 0; x < hull_vertices.size(); ++x)
            {
                for (size_t y = x + 1; y < hull_vertices.size(); ++y)
                {
                    // i: inside, h: hull
                    auto edge = Segment_2(hull_vertices[x], hull_vertices[y]);
                    auto lit = state_tracker.get_lit_from_edge(edge);
                    if (lit == Lit(0))
                    {
                        continue; // Edge not found, skip
                    }
                    if (!state_tracker.is_open(lit))
                    {
                        continue; // Skip if the edge is already assigned
                    }

                    auto intersections = state_tracker.intersections[lit];
                    bool find_intersection = false;
                    for (auto const &aktive_lit : state_tracker.get_observed_trail())
                    {
                        if (aktive_lit < 1)
                        {
                            continue; // Skip if the active literal is less than 1
                        }
                        if (std::find(intersections.begin(), intersections.end(), aktive_lit) != intersections.end())
                        {
                            find_intersection = true;
                            break; // Found an intersection, break
                        }
                    }
                    if (find_intersection)
                    {
                        continue; // Skip if an intersection is found
                    }

                    std::stringstream info;

#if PRINT
                    info << "------------------------------------------------------" << "\n";
                    info << "Checking edge: " << hull_vertices[x] << " - " << hull_vertices[y] << "\n";
                    info << "------------------------------------------------------" << "\n";
#endif
                    std::vector<Point_2> i_half_one, h_half_one, i_half_two, h_half_two;

                    // Split hull vertices from x to y (clockwise)
                    for (size_t i = x; i != y; i = (i + 1) % hull_vertices.size())
                    {
                        h_half_one.push_back(hull_vertices[i]);
                    }
                    h_half_one.push_back(hull_vertices[y]); // Include y

                    // Split hull vertices from y to x (clockwise)
                    for (size_t i = y; i != x; i = (i + 1) % hull_vertices.size())
                    {
                        h_half_two.push_back(hull_vertices[i]);
                    }
                    h_half_two.push_back(hull_vertices[x]); // Include x

                    // Populate inside vertices for both halves using convex hull containment test
                    // Helper function for cross product calculation
                    auto cross = [](const Point_2 &p1, const Point_2 &p2, const Point_2 &p) -> double
                    {
                        return CGAL::to_double((p2.x() - p1.x()) * (p.y() - p1.y()) - (p2.y() - p1.y()) * (p.x() - p1.x()));
                    };

                    // Helper function to test if point is in convex hull
                    auto pointInConvexHull = [&cross](const std::vector<Point_2> &hull, const Point_2 &p) -> bool
                    {
                        int n = hull.size();
                        if (n < 3)
                            return false; // no valid hull

                        // Check if all cross products have the same sign
                        int sign = 0;
                        for (int i = 0; i < n; i++)
                        {
                            Point_2 a = hull[i];
                            Point_2 b = hull[(i + 1) % n];
                            double cp = cross(a, b, p);

                            if (std::abs(cp) < 1e-9)
                                continue; // on the edge

                            if (sign == 0)
                            {
                                sign = (cp > 0 ? 1 : -1);
                            }
                            else
                            {
                                if ((cp > 0 ? 1 : -1) != sign)
                                    return false;
                            }
                        }
                        return true;
                    };

                    for (const auto &inner_vertex : inner_vertices)
                    {
                        // Test which half of the convex hull contains the inner vertex
                        bool in_half_one = pointInConvexHull(h_half_one, inner_vertex);
                        bool in_half_two = pointInConvexHull(h_half_two, inner_vertex);

                        if (in_half_one && !in_half_two)
                        {
                            i_half_one.push_back(inner_vertex);
                        }
                        else if (!in_half_one && in_half_two)
                        {
                            i_half_two.push_back(inner_vertex);
                        }
                        else if (in_half_one && in_half_two)
                        {
                            // // Point is in both halves - this should not happen for a proper division
                            // std::cerr << "Error: Inner vertex " << inner_vertex
                            //           << " is contained in both halves of the convex hull!" << std::endl;
                            // assert(false && "Inner vertex found in both halves of convex hull");
                            i_half_one.push_back(inner_vertex);
                            i_half_two.push_back(inner_vertex);
                        }
                        // else
                        // {
                        //     // Point is in neither half - this is an error for inner vertices
                        //     std::cerr << "Error: Inner vertex " << inner_vertex
                        //               << " is not contained in either half of the convex hull!" << std::endl;
                        //     std::cerr << "Hull half one size: " << h_half_one.size()
                        //               << ", Hull half two size: " << h_half_two.size() << std::endl;
                        //     assert(false && "Inner vertex not found in any half of convex hull");
                        // }
                    }

                    if (i_half_one.empty() || i_half_two.empty())
                    {
                        continue; // Skip if one of the halves is empty
                    }
                    if (handel_half(i_half_one, h_half_one, info) || handel_half(i_half_two, h_half_two, info))
                    {

#if PRINT
                        info << "can exclude(" << arrangement_counter << ") edge: " << hull_vertices[x] << " - " << hull_vertices[y] << "\n";
                        std::stringstream filename;
                        filename << "arrangement_" << std::setfill('0') << std::setw(4) << arrangement_counter++ << ".svg";
                        save_arrangement_as_svg(state_tracker.arr, state_tracker.edges, filename.str());
#endif
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

#if PRINT
                        info << "größe der inneren Punkte: " << inner_vertices.size() << "\n";
                        info << "lit can be excluded: " << lit << "\n";
                        info << "Reason for exclusion: ";
                        for (Lit l : reason)
                        {
                            info << l << " ";
                        }
                        info << "\n";
                        std::cerr << info.str() << std::endl;
#endif
                        counter++;
                        return -lit; // Return the literal for the edge that can be excluded
                    }
                }
            }
        }

        return 0;
    }

    void get_reason_clause(Lit propagated_lit, std::vector<Lit> &reason_buffer) override
    {
#if PRINT
        std::cerr << "Getting reason clause for propagated literal: " << propagated_lit << std::endl;
#endif
        state_tracker.get_reason(propagated_lit, reason_buffer);
    }

    std::vector<std::vector<int>> get_vars_saved()
    {
        return state_tracker.get_vars_saved();
    }

    ObservedLiteralStateTracker state_tracker;
    std::vector<std::vector<Lit>> hidden_clauses;
    static int arrangement_counter;
    int edgges_set_to_false_counter = 0;
};

int ExamplePropagator::arrangement_counter = 0;

std::tuple<Vars_List, std::vector<Vars_List>, int, int> cadical_wrapper(int number_vars,
                                                                        int number_edges_vars,
                                                                        std::vector<Vars_List> clauses,
                                                                        std::vector<Point_raw> nodes,
                                                                        std::vector<Edge_raw> edges,
                                                                        std::unordered_map<std::string, int> node_to_sdegree,
                                                                        std::unordered_map<int, std::vector<int>> intersections,
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
    auto &propagator = solver.emplace_external_propagator<ExamplePropagator>(&solver, save_state, nodes, edges, node_to_sdegree, intersections);
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
        std::cerr << "No solution found" << std::endl;
        return std::make_tuple(Vars_List{}, propagator.get_vars_saved(), counter, gesamt_counter);
    }
    else
    {
        std::cout << "Solution found" << std::endl;
#if PRINT
        std::stringstream filename;
        filename << "arrangement_" << std::setfill('0') << std::setw(4) << propagator.arrangement_counter++ << ".svg";
        save_arrangement_as_svg(propagator.state_tracker.arr, propagator.state_tracker.edges, filename.str());
#endif

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
        std::cerr << "gefundene Propergationen: " << counter << std::endl;
        return std::make_tuple(result, propagator.get_vars_saved(), counter, gesamt_counter);
        // std::vector<Vars_List> leer;
        // return std::make_pair(result, leer);
    }
}
