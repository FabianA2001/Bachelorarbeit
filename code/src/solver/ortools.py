from solver.solver import Solver


class Ortools(Solver):
    def actual_solver(self):
        for edge in self.graph.get_all_edges():
            self.graph.active_edge(edge[1], edge[0])
