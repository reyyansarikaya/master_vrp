from app.scripts.multi_vrp_solver import run_all_branches
from app.utils import setup_logger
import pandas as pd
import os

OUTPUT_DIR = "app/outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

logger = setup_logger("main")

def save_branch_routes_to_csv(branch: str, routes: list):
    rows = []
    for vehicle_id, route in enumerate(routes):
        for step_order, step in enumerate(route):
            rows.append({
                "branch": branch,
                "vehicle_id": vehicle_id,
                "step_order": step_order,
                "location_index": step["location_index"],
                "arrival_time (sec)": step["arrival_time"]
            })
    df = pd.DataFrame(rows)
    df.to_csv(os.path.join(OUTPUT_DIR, f"{branch.lower()}_routes.csv"), index=False)
    logger.info(f"Saved routes to {branch.lower()}_routes.csv")


def main():
    logger.info("Starting VRP analysis for all branches...")
    results = run_all_branches()
    logger.info("VRP analysis completed.")

    for branch, result in results.items():
        if result["status"] != "OK":
            logger.warning(f"Branch: {branch}, No solution found.")
            continue

        logger.info(f"Branch: {branch}, Vehicles used: {len(result['routes'])}")
        save_branch_routes_to_csv(branch, result["routes"])

if __name__ == "__main__":
    main()