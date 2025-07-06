import pandas as pd
from app.services.distance_matrix import load_or_build_distance_matrix
from app.services.vrp_solver import solve_vrp_with_time_windows
from app.utils import load_depots, setup_logger
import os
import json

logger = setup_logger("multi_vrp")

# Yeni CSV yolları – sen kendi bilgisayarındaki path ile değiştirmelisin
ORDERS_CSVS = {
    "Esenyurt": "/Users/reyyansarikaya/Desktop/Projects/master_vrp/app/data/Esenyurt_Orders.csv",
    "Haramidere": "/Users/reyyansarikaya/Desktop/Projects/master_vrp/app/data/Haramidere_Orders.csv"
}

DEPOTS_JSON = "/Users/reyyansarikaya/Desktop/Projects/master_vrp/app/data/depots.json"

WORK_START = 8 * 3600  # 08:00 in seconds
WORK_END = 17 * 3600   # 17:00 in seconds
LUNCH_BREAK = (12 * 3600, 13 * 3600)
SERVICE_TIME_PER_DESI = 2
VEHICLE_CAPACITY = 15000

BRANCH_VEHICLES = {
    "Esenyurt": 100,
    "Haramidere": 100
}

def solve_branch_vrp(branch: str, orders_df: pd.DataFrame, depots: dict):
    logger.info(f"\n\n=== Solving for branch: {branch} ===")
    logger.info(f"{len(orders_df)} orders assigned to {branch}")

    depot = depots[branch]
    depot_coord = f"{depot.lat},{depot.lon}"

    order_coords = [f"{row['latitude']},{row['longtitude']}" for _, row in orders_df.iterrows()]
    locations = [depot_coord] + order_coords

    service_times = [0] + [int(row["total_used_desi"] * SERVICE_TIME_PER_DESI) for _, row in orders_df.iterrows()]
    demands = [0] + [row["total_used_desi"] for _, row in orders_df.iterrows()]

    logger.info(f"Total demand: {sum(demands)}")
    logger.info(f"Total capacity: {BRANCH_VEHICLES[branch] * VEHICLE_CAPACITY}")

    matrix = load_or_build_distance_matrix(locations, branch)

    result = solve_vrp_with_time_windows(
        distance_matrix=matrix,
        service_times=service_times,
        order_demands=demands,
        vehicle_count=BRANCH_VEHICLES[branch],
        vehicle_capacity=VEHICLE_CAPACITY,
        depot_index=0,
        time_windows=[[WORK_START, WORK_END]] * len(locations),
        lunch_breaks=[LUNCH_BREAK] * BRANCH_VEHICLES[branch]
    )

    output_dir = "app/outputs"
    os.makedirs(output_dir, exist_ok=True)
    with open(f"{output_dir}/{branch.lower()}_solution.json", "w") as f:
        json.dump(result, f, indent=2)

    return result

def run_all_branches():
    depots = {depot.name: depot for depot in load_depots(DEPOTS_JSON)}
    results = {}
    for branch, csv_path in ORDERS_CSVS.items():
        orders_df = pd.read_csv(csv_path)
        result = solve_branch_vrp(branch, orders_df, depots)
        results[branch] = result
    return results