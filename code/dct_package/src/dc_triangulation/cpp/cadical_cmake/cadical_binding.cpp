#include <cadical_binding/cadical_solver.h>
#include <cadical.hpp>
#include <future>
#include <thread>
#include <mutex>
#include <iostream>

namespace cdc {

static constexpr int IS_FORGETTABLE_TAG = std::numeric_limits<int>::min();
static constexpr int IS_UNFORGETTABLE_TAG = std::numeric_limits<int>::max();

/**
 * Implementation of the actual external propagator.
 */
class CadicalSolver::RawExternalPropagator : public CaDiCaL::ExternalPropagator {
  public:
    RawExternalPropagator(CadicalSolver::ExternalPropagator* external_prop,
                          bool reasons_forgettable,
                          bool only_check_full_assignments) :
        m_external_prop(external_prop)
    {
        this->is_lazy = only_check_full_assignments;
        this->are_reasons_forgettable = reasons_forgettable;
    }

    void notify_new_decision_level() override final {
        m_external_prop->notify_new_decision_level();
    }

    void notify_backtrack(size_t new_level) override final {
        m_external_prop->notify_backtrack(new_level);
    }

    void notify_assignment(const std::vector<int> &lits) override final {
        m_external_prop->notify_assignment(lits);
    }

    bool cb_check_found_model(const std::vector<int> &model) override final {
        return m_external_prop->check_full_assignment(model);
    }

    int cb_decide() override final {
        return m_external_prop->next_decision();
    }

    int cb_propagate() override final {
        return m_external_prop->propagate();
    }

    int cb_add_reason_clause_lit(int propagated_lit) override final {
        if(propagated_lit == m_last_reason_prop_lit) {
            if(m_reason_buffer.empty()) {
                m_last_reason_prop_lit = 0;
                return 0;  // done adding reason clause
            }
            Lit next_lit = m_reason_buffer.back();
            m_reason_buffer.pop_back();
            return next_lit; // return the next literal in the reason clause
        }
        if(!m_reason_buffer.empty()) {
            throw std::logic_error(
                "cb_add_reason_clause_lit called unexpectedly with a new propagated literal."
            );
        }
        m_last_reason_prop_lit = propagated_lit;
        m_external_prop->get_reason_clause(propagated_lit, m_reason_buffer);
        return cb_add_reason_clause_lit(m_last_reason_prop_lit);
    }

    void add_external_clause_lit(Lit l) {
        m_external_clause_buffer.push_back(l);
    }

    /**
     * Callback that queries whether we have an external clause to add.
     */
    bool cb_has_external_clause(bool &is_forgettable) override {
        if(m_external_clause_buffer.empty()) {
            return false; // no external clause to add
        }
        is_forgettable = (m_external_clause_buffer.front() == IS_FORGETTABLE_TAG);
        return true;
    }

    /**
     * Callback that actually adds a single literal to an external clause.
     */
    int cb_add_external_clause_lit() override {
        Lit next_lit = m_external_clause_buffer[m_external_clause_consume_pos];
        if(next_lit == IS_FORGETTABLE_TAG || next_lit == IS_UNFORGETTABLE_TAG) {
            ++m_external_clause_consume_pos;
            next_lit = m_external_clause_buffer[m_external_clause_consume_pos];
        }
        if(++m_external_clause_consume_pos == m_external_clause_buffer.size()) {
            m_external_clause_buffer.clear();
            m_external_clause_consume_pos = 0;
        }
        return next_lit;
    }

    void reset_buffers() {
        m_external_clause_buffer.clear();
        m_external_clause_consume_pos = 0;
        m_last_reason_prop_lit = 0;
        m_reason_buffer.clear();
    }

  private:
    CadicalSolver::ExternalPropagator* m_external_prop;
    std::vector<Lit> m_external_clause_buffer;
    std::size_t m_external_clause_consume_pos = 0;
    Lit m_last_reason_prop_lit = 0;
    std::vector<Lit> m_reason_buffer;
};

struct CadicalSolver::Terminator : CaDiCaL::Terminator {
    std::atomic<bool> interrupt_flag;

    Terminator() noexcept : interrupt_flag(false) {}

    bool terminate() override {
        return interrupt_flag.load(std::memory_order_relaxed);
    }

    void set_terminate() noexcept {
        interrupt_flag.store(true, std::memory_order_relaxed);
    }

    void reset_terminate() noexcept {
        interrupt_flag.store(false, std::memory_order_relaxed);
    }
};

CadicalSolver::CadicalSolver() {
    m_solver = std::make_unique<CaDiCaL::Solver>();
    m_terminator = std::make_unique<Terminator>();
    m_num_vars = 0;
    m_solver->connect_terminator(m_terminator.get());
}

CadicalSolver::~CadicalSolver() {
    m_solver->disconnect_terminator();
}

void CadicalSolver::reset() {
    m_solver->disconnect_terminator();
    m_solver = std::make_unique<CaDiCaL::Solver>();
    m_solver->connect_terminator(m_terminator.get());
    m_num_vars = 0;
}

auto CadicalSolver::new_var(bool /*reusable*/) -> Lit {
    if(m_num_vars == 0) {
        m_num_vars = m_solver->vars();
    }
    m_num_vars += 1;
    return m_num_vars;
}

auto CadicalSolver::ExternalPropagator::new_observed_var() -> Lit {
    Lit new_var = solver->new_var();
    this->observe(new_var);
    return new_var;
}

auto CadicalSolver::new_vars(Lit num_vars) -> Lit {
    if(m_num_vars == 0) {
        m_num_vars = m_solver->vars();
    }
    Lit result = m_num_vars + 1;
    m_num_vars += num_vars;
    m_solver->reserve(m_num_vars);
    return result;
}

auto CadicalSolver::num_vars() const noexcept -> Lit {
    return m_solver->vars();
}

auto CadicalSolver::get_model() const -> ModelMap {
    ModelMap map;
    map.model_map = std::vector<bool>(m_solver->vars(), false);
    for(Lit l = 1, nvars = num_vars(); l <= nvars; ++l) {
        if(m_solver->val(l) > 0) {
            map.model_map[l-1] = true;
        }
    }
    return map;
}

void CadicalSolver::terminate() {
    m_terminator->set_terminate();
}
    
void CadicalSolver::reset_terminate() {
    m_terminator->reset_terminate();
    if(m_external_propagator) {
        m_external_propagator->m_raw->reset_buffers();
    }
}

static void cdc_add_assumptions(CaDiCaL::Solver& solver, 
                                const std::vector<int>& assumptions) 
{
    for(int l : assumptions) {
        solver.assume(l);
    }
}

std::optional<bool> 
CadicalSolver::solve(const std::vector<Lit>& assumptions, double time_limit)
{
    if(time_limit <= 0) return std::nullopt;
    cdc_add_assumptions(*m_solver, assumptions);
    reset_terminate();
    if(!std::isfinite(time_limit)) {
        int solve_result = m_solver->solve();
        if(solve_result == 10) {
            return true;
        } else if(solve_result == 20) {
            return false;
        } else {
            return std::nullopt;
        }
    }
    std::promise<std::optional<bool>> res_promise;
    std::future<std::optional<bool>> result = res_promise.get_future();
    auto smain = [&] () { res_promise.set_value(solve()); };
    std::thread t{smain};
    auto status = result.wait_for(std::chrono::duration<double>(time_limit));
    if(status == std::future_status::timeout) {
        this->terminate(); // abort solution process on timeout
    }
    std::optional<bool> r = result.get();
    t.join();
    return r;
}

void CadicalSolver::add_literal(Lit l) {
    m_solver->add(l);
}

CadicalSolver::ExternalPropagator::~ExternalPropagator() = default;

CadicalSolver::ExternalPropagator::ExternalPropagator(
    CadicalSolver* solver, bool reasons_forgettable, bool only_check_full_assignments
) : 
    solver(solver),
    m_raw(std::make_unique<RawExternalPropagator>(
        this, reasons_forgettable, only_check_full_assignments
    ))
{}

void CadicalSolver::ExternalPropagator::begin_external_clause(bool forgettable) {
    m_raw->add_external_clause_lit(
        forgettable ? IS_FORGETTABLE_TAG : IS_UNFORGETTABLE_TAG
    );
}

void CadicalSolver::ExternalPropagator::finish_external_clause() {
    m_raw->add_external_clause_lit(0); // end the external clause
}

void CadicalSolver::ExternalPropagator::observe(Lit var) {
    solver->m_solver->add_observed_var(var);
}

void CadicalSolver::ExternalPropagator::unobserve(Lit var) {
    solver->m_solver->remove_observed_var(var);
}

void CadicalSolver::p_connect_external_propagator() {
    m_solver->connect_external_propagator(
        m_external_propagator->m_raw.get()
    );
}

void CadicalSolver::ExternalPropagator::add_external_clause_literal(Lit l) {
    m_raw->add_external_clause_lit(l);
}

} // namespace cdc
