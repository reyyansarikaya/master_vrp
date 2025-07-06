from ortools.constraint_solver import pywrapcp, routing_enums_pb2
from typing import List, Dict

def solve_simple_vrp(
    distance_matrix: List[List[int]],
    demands: List[float],
    vehicle_count: int,
    vehicle_capacity: float,
    depot_index: int = 0
) -> Dict:
    manager = pywrapcp.RoutingIndexManager(len(distance_matrix), vehicle_count, depot_index)
    routing = pywrapcp.RoutingModel(manager)

    # Distance callback
    def distance_callback(from_index, to_index):
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return distance_matrix[from_node][to_node]

    transit_callback_index = routing.RegisterTransitCallback(distance_callback)
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    # Demand callback
    def demand_callback(from_index):
        return int(demands[manager.IndexToNode(from_index)])

    demand_callback_index = routing.RegisterUnaryTransitCallback(demand_callback)

    routing.AddDimensionWithVehicleCapacity(
        demand_callback_index,
        0,  # no slack
        [int(vehicle_capacity)] * vehicle_count,
        True,  # start cumul at zero
        "Capacity"
    )

    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC

    solution = routing.SolveWithParameters(search_parameters)

    if not solution:
        return {"status": "No solution found"}

    routes = []
    for vehicle_id in range(vehicle_count):
        index = routing.Start(vehicle_id)
        route = []
        while not routing.IsEnd(index):
            node = manager.IndexToNode(index)
            route.append(node)
            index = solution.Value(routing.NextVar(index))
        route.append(manager.IndexToNode(index))  # return to depot
        routes.append(route)

    return {
        "status": "OK",
        "routes": routes
    }