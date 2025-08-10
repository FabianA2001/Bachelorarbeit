
#include "cadical_wrapper.h"
#include <fstream>
#include <sstream>
#include <iomanip>
#include <limits>
#include <filesystem>

using Kernel = CGAL::Exact_predicates_inexact_constructions_kernel;
using Point_2 = Kernel::Point_2;
using Segment_2 = Kernel::Segment_2;
using Polygon_2 = CGAL::Polygon_2<Kernel>;
using Traits_2 = CGAL::Arr_segment_traits_2<Kernel>;
using Arrangement_2 = CGAL::Arrangement_2<Traits_2>;

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
        std::cerr << "Error: Could not open file " << full_path << " for writing." << std::endl;
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

    std::cerr << "Arrangement saved as SVG to: " << full_path << std::endl;
    // std::cerr << "Vertices: " << arr.number_of_vertices()
    //           << ", Edges: " << arr.number_of_edges()
    //           << ", Faces: " << arr.number_of_faces() << std::endl;
    // std::cerr << "Original edges count: " << original_edges.size() << std::endl;
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

    ObservedLiteralStateTracker(bool save_states = false) : save_states(save_states)
    {
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
            throw std::logic_error("No reason stored for the propagated literal: " +
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

private:
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

    ExamplePropagator(cdc::CadicalSolver *solver, bool save_states = false, std::vector<Edge_raw> edges = {}, std::unordered_map<std::string, int> nodes_to_sdegree = {}) : cdc::CadicalSolver::ExternalPropagator(solver, true, false), state_tracker(save_states), node_to_sdegree(node_to_sdegree)
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
        assert(it != edge_to_index.end() &&
               "Edge not found in the edge to index map.");
        return it->second;
    }

    int get_sdegree_from_node(const Point_2 &node) const
    {
        std::string key = std::to_string(node.x()) + "," +
                          std::to_string(node.y());
        return node_to_sdegree.at(key);
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

        // Check if any observed variables are found before printing
        bool found_observed = false;
        std::vector<Lit> observed_lits;

        for (Lit l : lits)
        {
            if (std::find(state_tracker.observed_vars.begin(), state_tracker.observed_vars.end(), l) != state_tracker.observed_vars.end())
            {
                found_observed = true;
                observed_lits.push_back(l);
                CGAL::insert(state_tracker.arr, get_edge_from_lit(l));
            }
        }

        // Only print if observed variables were found
        if (found_observed)
        {
            std::cerr << "Observed literals assigned: ";
            for (Lit l : observed_lits)
            {
                std::cerr << l << " ";
            }
            std::cerr << "\n";
        }
        // std::cerr << "Current observed trail: ";
        // for (Lit l : state_tracker.get_observed_trail())
        // {
        //     std::cerr << l << " ";
        // }
        // std::cerr << "\n";
    }

    void notify_new_decision_level() override
    {
        std::cerr << "New decision level started.\n";
        state_tracker.notify_new_decision_level();
    }

    void notify_backtrack(std::size_t new_level) override
    {
        std::cerr << "Backtracking to level " << new_level << "\n";
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
        save_arrangement_as_svg(state_tracker.arr, edges, filename.str());

        return 0;
    }

    void get_reason_clause(Lit propagated_lit, std::vector<Lit> &reason_buffer) override
    {
        std::cerr << "Getting reason clause for propagated literal: " << propagated_lit << "\n";
        state_tracker.get_reason(propagated_lit, reason_buffer);
    }

    std::vector<std::vector<int>> get_vars_saved()
    {
        return state_tracker.get_vars_saved();
    }

private:
    ObservedLiteralStateTracker state_tracker;
    std::vector<std::vector<Lit>> hidden_clauses;
    std::vector<Segment_2> edges;
    std::unordered_map<std::string, Lit> edge_to_index;
    std::unordered_map<std::string, int> node_to_sdegree;
    static int arrangement_counter;
};

// Initialize static counter
int ExamplePropagator::arrangement_counter = 0;

std::pair<Vars_List, std::vector<Vars_List>> cadical_wrapper(int number_vars,
                                                             int number_edges_vars,
                                                             std::vector<Vars_List> clauses,
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
    auto &propagator = solver.emplace_external_propagator<ExamplePropagator>(&solver, save_state, edges, node_to_sdegree);
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
        std::cerr << "No solution found\n";
        return std::make_pair(Vars_List{}, std::vector<Vars_List>{});
    }
    else
    {
        std::cout << "Solution found\n";
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
