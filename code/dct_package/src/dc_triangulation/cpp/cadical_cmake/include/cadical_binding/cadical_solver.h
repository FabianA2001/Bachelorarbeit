#ifndef CADICAL_BINDINGS_H_INCLUDED_
#define CADICAL_BINDINGS_H_INCLUDED_

#include <memory>
#include <algorithm>
#include <vector>
#include <optional>
#include <limits>
#include <cmath>
#include <type_traits>
#include <utility>
#include <stdexcept>

namespace CaDiCaL
{

    /**
     * Forward declaration of the actual solver type.
     */
    class Solver;

}

namespace cdc
{

    /**
     * Bindings to make CaDiCaL usable in our framework,
     * and to avoid symbols seeping into the rest of our
     * projects.
     */
    class CadicalSolver
    {
    private:
        /**
         * Forward declaration of the external propagator type.
         */
        class RawExternalPropagator;

    public:
        using Lit = int;

        /**
         * Add a new variable.
         * Reusable is ignored in this solver.
         */
        Lit new_var(bool reusable = true);

        /**
         * Add num_vars new variables;
         * returns the a literal corresponding
         * to the first new variable.
         */
        Lit new_vars(Lit num_vars);

        /**
         * Get the number of variables.
         */
        Lit num_vars() const noexcept;

        /**
         * Add a short clause.
         */
        template <typename... Lits>
        void add_short_clause(Lits... lits)
        {
            add_literals(lits...);
            finish_clause();
        }

        /**
         * Add a variadic number of literals to the current clause.
         */
        template <typename... Lits>
        void add_literals(Lits... lits)
        {
            (add_literal(lits), ...);
        }

        /**
         * Finish the current clause.
         */
        void finish_clause()
        {
            add_literal(0);
        }

        /**
         * Add a clause from a sequence of literals.
         */
        template <
            typename LitIterator,
            std::enable_if_t<!std::is_integral_v<LitIterator>, int> = 0>
        void add_clause(LitIterator begin, LitIterator end)
        {
            std::for_each(begin, end, [this](Lit l)
                          { add_literal(l); });
            finish_clause();
        }

        /**
         * Add a single literal to the current clause.
         */
        void add_literal(Lit l);

        /**
         * Create an empty solver.
         */
        CadicalSolver();

        /**
         * Destroy the solver.
         */
        ~CadicalSolver();

        /**
         * Reset the solver.
         */
        void reset();

        /**
         * Fix a variable to a given value.
         */
        void fix(Lit l)
        {
            add_short_clause(l);
        }

        /**
         * Asynchronously terminate the solver.
         */
        void terminate();

        /**
         * Reset the termination flag.
         */
        void reset_terminate();

        /**
         * Solve the current formula.
         */
        std::optional<bool> solve(const std::vector<Lit> &assumptions = {},
                                  double time_limit = std::numeric_limits<double>::infinity());

        /**
         * Store a model returned by the solver;
         * allows querying the truth values of literals.
         */
        class ModelMap
        {
        public:
            ModelMap() = default;

            std::vector<bool> &raw() noexcept
            {
                return model_map;
            }

            const std::vector<bool> &raw() const noexcept
            {
                return model_map;
            }

            bool operator[](Lit l) const noexcept
            {
                if (l < 0)
                {
                    return !model_map[-(l + 1)];
                }
                else
                {
                    return model_map[l - 1];
                }
            }

            std::vector<bool> model_map;
        };

        /**
         * A wrapper around CaDiCaL's external propagator.
         * Supports easier addition of external clauses;
         * all other callbacks are passed through as is.
         */
        class ExternalPropagator
        {
        public:
            using Lit = CadicalSolver::Lit;

            /**
             * Construct an external propagator.
             * @param reasons_forgettable If true, the external clauses added as
             *                            reasons can be deleted by the SAT solver.
             * @param only_check_full_assignments If true, the external propagator
             *                                    will only check full assignments.
             */
            explicit ExternalPropagator(
                CadicalSolver *solver,
                bool reasons_forgettable = false,
                bool only_check_full_assignments = false);

            /**
             * Destructor for the external propagator.
             */
            virtual ~ExternalPropagator();

            /**
             * Called to notify the external propagator
             * about assignments to observed variables.
             * The notification is not necessarily eager,
             * the external propagator is usually notified
             * before the call of propagator callbacks.
             *
             * NEEDS TO BE IMPLEMENTED BY THE USER.
             * @param lits The observed literals that have been assigned.
             */
            virtual void notify_assignment(const std::vector<Lit> &lits) = 0;

            /**
             * Notify the external propagator about beginning a new decision level.
             * CAN BE OVERRIDDEN BY THE USER.
             */
            virtual void notify_new_decision_level() {}

            /**
             * Notify the external propagator about backtracking/backjumping to
             * a previous decision level.
             * CAN BE OVERRIDDEN BY THE USER.
             * @param new_level The new decision level to backtrack to.
             */
            virtual void notify_backtrack(size_t new_level)
            {
                static_cast<void>(new_level);
            }

            /**
             * Check the found model (full satisfying assignment).
             * Returning false rejects the model,
             * and the external propagator should provide
             * an external clause or new observed variables
             * if it returns false.
             * CAN BE OVERRIDDEN BY THE USER.
             * @param model The full assignment to check.
             * @return true if the model is valid, false otherwise.
             */
            virtual bool check_full_assignment(const std::vector<Lit> &model)
            {
                static_cast<void>(model);
                return true; // by default, assume the model is valid
            }

            /**
             * Get the next decision literal, if the propagator
             * wants to influence the decision making.
             * If it returns 0, the SAT solver will make its own choice.
             * CAN BE OVERRIDDEN BY THE USER.
             * @return The next decision literal, or 0 if the solver should decide.
             */
            virtual int next_decision() { return 0; }

            /**
             * Get the next external propagation literal.
             * If it returns 0, there is no external propagation to make.
             * CAN BE OVERRIDDEN BY THE USER.
             * @return The next literal to propagate, or 0 if there is none.
             */
            virtual int propagate()
            {
                return 0; // by default, no external propagation
            }

            /**
             * Get the reason clause for a propagated literal.
             * This function is called when the propagate method returns a non-zero literal.
             * MUST BE OVERRIDDEN BY THE USER IF `propagate` ever returns a non-zero literal.
             * @param propagated_lit The literal that was propagated, as returned from `propagate`.
             * @param reason_buffer A buffer to fill with the reason clause.
             */
            virtual void get_reason_clause(Lit propagated_lit, std::vector<Lit> &reason_buffer)
            {
                throw std::logic_error("get_reason_clause not implemented but propagate returned a non-zero literal!");
            }

            /**
             * Observe a new variable;
             * only observed variables can be used
             * in external clauses and propagation,
             * and only they are in notified assignments.
             * CAN be called with 'fresh' variables,
             * during the solving process,
             * or between/before calls to `solve()`.
             */
            void observe(Lit var);

            /**
             * Add a new variable and observe it.
             * CAN be called during, between, or before calls to `solve()`.
             */
            Lit new_observed_var();

            /**
             * Observe a range of variables.
             */
            template <typename ObserveRangeBegin,
                      typename ObserveRangeEnd>
            void observe(ObserveRangeBegin begin, ObserveRangeEnd end)
            {
                std::for_each(begin, end, [this](Lit l)
                              { observe(l); });
            }

            /**
             * Stop observing a variable.
             * Note: This must NOT be called
             * during a call to `solve()`,
             * e.g., from any callback method,
             * but ONLY between calls to `solve()`.
             */
            void unobserve(Lit var);

            /**
             * Stop observing a range of variables.
             * The same conditions apply as for `unobserve(Lit)`.
             */
            template <typename ObserveRangeBegin,
                      typename ObserveRangeEnd>
            void unobserve(ObserveRangeBegin begin, ObserveRangeEnd end)
            {
                std::for_each(begin, end, [this](Lit l)
                              { unobserve(l); });
            }

            /**
             * Mechanisms to add external clauses,
             * which can be either unforgettable (default) or forgettable.
             */
            struct Forgettable
            {
            };
            struct Unforgettable
            {
            };
            static constexpr Forgettable forgettable{};
            static constexpr Unforgettable unforgettable{};

            /**
             * Add a short unforgettable external clause.
             */
            template <typename... Lits,
                      std::enable_if_t<(std::is_convertible_v<Lits, Lit> && ...), int> = 0>
            void add_short_external_clause(Unforgettable, Lits... lits)
            {
                begin_external_clause(false);
                (add_external_clause_literal(lits), ...);
                finish_external_clause();
            }

            /**
             * Add a short forgettable external clause.
             */
            template <typename... Lits,
                      std::enable_if_t<(std::is_convertible_v<Lits, Lit> && ...), int> = 0>
            void add_short_external_clause(Forgettable, Lits... lits)
            {
                begin_external_clause(true);
                (add_external_clause_literal(lits), ...);
                finish_external_clause();
            }

            /**
             * Add a short external clause (unforgettable by default).
             */
            template <typename... Lits,
                      std::enable_if_t<(std::is_convertible_v<Lits, Lit> && ...), int> = 0>
            void add_short_external_clause(Lits... lits)
            {
                add_short_external_clause(unforgettable, std::forward<Lits>(lits)...);
            }

            /**
             * Add an external clause from a sequence of literals.
             * The clause is unforgettable by default.
             */
            template <typename LitIterator,
                      std::enable_if_t<!std::is_integral_v<LitIterator>, int> = 0>
            void add_external_clause(LitIterator begin, LitIterator end)
            {
                begin_external_clause(false);
                std::for_each(begin, end, [this](Lit l)
                              { add_external_clause_literal(l); });
                finish_external_clause();
            }

            /**
             * Add an external clause from a sequence of literals.
             * The clause is forgettable.
             */
            template <typename LitIterator,
                      std::enable_if_t<!std::is_integral_v<LitIterator>, int> = 0>
            void add_external_clause(Forgettable, LitIterator begin, LitIterator end)
            {
                begin_external_clause(true);
                std::for_each(begin, end, [this](Lit l)
                              { add_external_clause_literal(l); });
                finish_external_clause();
            }

            /**
             * Add an external clause from a sequence of literals.
             * The clause is unforgettable.
             */
            template <typename LitIterator,
                      std::enable_if_t<!std::is_integral_v<LitIterator>, int> = 0>
            void add_external_clause(Unforgettable, LitIterator begin, LitIterator end)
            {
                begin_external_clause(false);
                std::for_each(begin, end, [this](Lit l)
                              { add_external_clause_literal(l); });
                finish_external_clause();
            }

            /**
             * Begin an external clause.
             * @param forgettable If true, the clause is forgettable, which means the
             *                    SAT solver can delete it later.
             */
            void begin_external_clause(bool forgettable);

            /**
             * Finish the current external clause, actually
             * adding the clause to the solver.
             */
            void finish_external_clause();

            /**
             * Add a single literal to the current external clause.
             */
            void add_external_clause_literal(Lit l);

        protected:
            CadicalSolver *solver;

        private:
            friend class CadicalSolver;
            std::unique_ptr<RawExternalPropagator> m_raw;
        };

        /**
         * After a successful solve, get the model.
         */
        ModelMap get_model() const;

        /**
         * Get the solver name.
         */
        static const char *name() noexcept
        {
            return "CaDiCaL";
        }

        /**
         * Construct an external propagator of the given type,
         * and connect it to the solver.
         * The propagator will be owned by the solver;
         * only one external propagator can be
         * connected to the solver at a time.
         *
         * @tparam ActualPropagatorType The type of the external propagator to create.
         * @param args Arguments to forward to the constructor of the external propagator.
         */
        template <typename ActualPropagatorType, typename... Args>
        ActualPropagatorType &emplace_external_propagator(Args &&...args)
        {
            m_external_propagator = std::make_unique<ActualPropagatorType>(
                std::forward<Args>(args)...);
            p_connect_external_propagator();
            return *static_cast<ActualPropagatorType *>(m_external_propagator.get());
        }

    private:
        struct Terminator;

        void p_connect_external_propagator();

        std::unique_ptr<CaDiCaL::Solver> m_solver;
        std::unique_ptr<Terminator> m_terminator;
        std::unique_ptr<ExternalPropagator> m_external_propagator;
        Lit m_num_vars = 0;
    };

}

#endif
