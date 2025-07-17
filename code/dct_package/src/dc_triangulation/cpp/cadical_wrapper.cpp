
#include "cadical_wrapper.h"

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
    }

    void notify_new_decision_level()
    {
        ++current_decision_level;
        level_indices.push_back(observed_trail.size());
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
            assert(is_open(l) && "Should not assign a value to an already assigned literal.");
            observed_trail.push_back(l);
            std::size_t index = p_var_index(l);
            assert(index + 1 < observed_values.size() && "Observed values vector is too small.");
            observed_values[index] = true;        // mark the variable as assigned
            observed_values[index + 1] = (l > 0); // store the value
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

    ExamplePropagator(cdc::CadicalSolver *solver) : cdc::CadicalSolver::ExternalPropagator(solver, true, false),
                                                    state_tracker()
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
        state_tracker.notify_assignments(lits);
        std::cerr << "Observed literals assigned: ";
        for (Lit l : lits)
        {
            std::cerr << l << " ";
        }
        std::cerr << "\n";
        std::cerr << "Current observed trail: ";
        for (Lit l : state_tracker.get_observed_trail())
        {
            std::cerr << l << " ";
        }
        std::cerr << "\n";
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

    /**
     * Propagation routine; inefficient checking for unit clauses.
     */
    int propagate() override
    {
        std::cerr << "PROPAGATE called with observed trail ";
        for (Lit l : state_tracker.get_observed_trail())
        {
            std::cerr << l << " ";
        }
        std::cerr << "\n";

        for (const auto &clause : hidden_clauses)
        {
            bool has_true = false;
            std::size_t num_open = 0;
            Lit unit_lit = 0;
            for (Lit l : clause)
            {
                if (state_tracker.is_true(l))
                {
                    has_true = true;
                    break;
                }
                else if (state_tracker.is_open(l))
                {
                    unit_lit = l;
                    ++num_open;
                }
            }
            if (has_true)
            {
                continue; // clause is satisfied
            }
            if (num_open == 0)
            {
                std::cerr << "External clause violated: ";
                for (Lit l : clause)
                {
                    std::cerr << l << " ";
                }
                std::cerr << "\n";
                add_external_clause(clause.begin(), clause.end());
                return 0; // clause is violated, return 0 and external clause
            }
            if (num_open == 1)
            {
                std::cerr << "Unit clause: ";
                for (Lit l : clause)
                {
                    std::cerr << l << " ";
                }
                std::cerr << "\n";
                std::cerr << "Unit literal: " << unit_lit << "\n";
                state_tracker.store_reason(unit_lit, clause);
                return unit_lit;
            }
        }
        std::cerr << "No unit clauses found, returning 0.\n";
        return 0;
    }

    void get_reason_clause(Lit propagated_lit, std::vector<Lit> &reason_buffer) override
    {
        std::cerr << "Getting reason clause for propagated literal: " << propagated_lit << "\n";
        state_tracker.get_reason(propagated_lit, reason_buffer);
    }

private:
    ObservedLiteralStateTracker state_tracker;
    std::vector<std::vector<Lit>> hidden_clauses;
};

std::pair<Vars_List, std::vector<Vars_List>> cadical_wrapper(int nummber_vars, std::vector<Vars_List> clauses)
{
    cdc::CadicalSolver solver;
    std::vector<cdc::CadicalSolver::Lit> v;
    for (int i = 0; i < nummber_vars; ++i)
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
    auto &propagator = solver.emplace_external_propagator<ExamplePropagator>(&solver);
    // observe the variables (must be AFTER the constructor)
    propagator.observe_variables(v);
    for (const auto &clause : clauses)
    {
        // add the clauses to the propagator
        propagator.add_hidden_clause(clause);
    }

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
        return std::make_pair(result, std::vector<Vars_List>{});
        ;
    }
}
