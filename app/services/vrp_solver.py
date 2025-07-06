from ortools.constraint_solver import pywrapcp, routing_enums_pb2
from typing import List, Dict
from app.schemas.location import WarehouseOrder
from app.utils import load_depots, setup_logger

logger = setup_logger("multi_vrp")

def solve_vrp(distance_matrix: List[List[int]], vehicle_count: int, depot_index: int = 0) -> List[List[int]]:
    manager = pywrapcp.RoutingIndexManager(len(distance_matrix), vehicle_count, depot_index)
    routing = pywrapcp.RoutingModel(manager)

    def distance_callback(from_index, to_index):
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return distance_matrix[from_node][to_node]

    transit_callback_index = routing.RegisterTransitCallback(distance_callback)
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC

    logger.info("Solve VRP Vuhuuu and lunch breaks...")
    solution = routing.SolveWithParameters(search_parameters)
    logger.info("Solver finished.")

    routes = []
    if solution:
        for vehicle_id in range(vehicle_count):
            index = routing.Start(vehicle_id)
            route = []
            while not routing.IsEnd(index):
                route.append(manager.IndexToNode(index))
                index = solution.Value(routing.NextVar(index))
            route.append(manager.IndexToNode(index))  # End at depot
            routes.append(route)
    return routes


def solve_vrp_with_time_windows(
    distance_matrix: List[List[int]],
    service_times: List[int],
    vehicle_count: int,
    vehicle_capacity: int,
    order_demands: List[int],
    depot_index: int,
    time_windows: List[List[int]],
    lunch_breaks: List[List[int]]
) -> Dict:
    manager = pywrapcp.RoutingIndexManager(len(distance_matrix), vehicle_count, depot_index)
    routing = pywrapcp.RoutingModel(manager)

    print("🚨 Max demand:", max(order_demands))
    print("🚛 Vehicle capacity:", vehicle_capacity)
    print("🚛 Vehicle count:", vehicle_count)
    print("🚛 Depot index:", depot_index)
    print("🚛 Time windows:", time_windows)
    print("🚛 Lunch breaks:", lunch_breaks)

    # Zaman + servis süresi callback
    def time_callback(from_index, to_index):
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return distance_matrix[from_node][to_node] + service_times[from_node]

    transit_callback_index = routing.RegisterTransitCallback(time_callback)
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    # ZAMAN BOYUTU – toplam süre artırıldı
    routing.AddDimension(
        transit_callback_index,
        300,        # waiting slack
        72000,      # 20 saat maksimum rota süresi
        False,      # force start cumul to zero = False
        "Time"
    )
    time_dimension = routing.GetDimensionOrDie("Time")

    # ZAMAN PENCERELERİ
    for location_idx, (start, end) in enumerate(time_windows):
        index = manager.NodeToIndex(location_idx)
        time_dimension.CumulVar(index).SetRange(start, end)

    # LUNCH BREAKLER (geçici olarak devre dışı)
    # for v_id in range(vehicle_count):
    #     break_start, break_end = lunch_breaks[v_id]
    #     interval = routing.solver().FixedDurationIntervalVar(
    #         break_start, break_end,
    #         break_end - break_start,
    #         True,
    #         f"Break{v_id}"
    #     )
    #     time_dimension.SetBreakIntervalsOfVehicle(
    #         [interval],
    #         v_id,
    #         [break_end - break_start]
    #     )

    # KAPASİTE BOYUTU
    demand_callback_index = routing.RegisterUnaryTransitCallback(
        lambda from_index: order_demands[manager.IndexToNode(from_index)]
    )
    routing.AddDimensionWithVehicleCapacity(
        demand_callback_index,
        0,  # slack
        [vehicle_capacity] * vehicle_count,
        True,
        "Capacity"
    )

    # ARAMA PARAMETRELERİ
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
    search_parameters.time_limit.FromSeconds(60)  # timeout: 60 saniye

    print("🧠 Solving VRP with time windows...")
    solution = routing.SolveWithParameters(search_parameters)

    if not solution:
        print("❌ Çözüm bulunamadı.")
        return {"status": "No solution found"}

    # SONUÇLARI TOPARLA
    routes = []
    for v_id in range(vehicle_count):
        index = routing.Start(v_id)
        route = []
        while not routing.IsEnd(index):
            node = manager.IndexToNode(index)
            arrival = solution.Min(time_dimension.CumulVar(index))
            route.append({"location_index": node, "arrival_time": arrival})
            index = solution.Value(routing.NextVar(index))
        if len(route) > 1:
            routes.append(route)

    print("✅ Çözüm bulundu.")
    return {"status": "OK", "routes": routes}