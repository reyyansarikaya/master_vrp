import json
import csv
import logging
from typing import List, Dict
from app.schemas.location import Depot, WarehouseOrder
from app.exceptions import DepotFileNotFoundError, WarehouseOrdersLoadError

def setup_logger(name: str = "master_vrp") -> logging.Logger:
    """
    Sets up and returns a logger with standard formatting.

    Args:
        name (str): Name of the logger instance.

    Returns:
        logging.Logger: Configured logger.
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    if not logger.hasHandlers():
        handler = logging.StreamHandler()
        formatter = logging.Formatter("[%(asctime)s] [%(levelname)s] %(message)s", "%H:%M:%S")
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger

def load_depots(filepath: str) -> List[Depot]:
    """
    Loads and validates a list of depots from a JSON file.

    Args:
        filepath (str): Path to the JSON file.

    Returns:
        List[Depot]: List of validated Depot objects.

    Raises:
        DepotFileNotFoundError: If the JSON file does not exist.
    """
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            raw = json.load(f)
            return [Depot(**item) for item in raw]
    except FileNotFoundError:
        raise DepotFileNotFoundError(filepath)

def load_warehouse_orders_from_csv(filepath: str) -> List[WarehouseOrder]:
    """
    Loads and validates a list of warehouse orders from a CSV file.

    Args:
        filepath (str): Path to the CSV file.

    Returns:
        List[WarehouseOrder]: List of validated WarehouseOrder objects.

    Raises:
        WarehouseOrdersLoadError: If the CSV file is missing or invalid.
    """
    orders = []
    try:
        with open(filepath, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                try:
                    order = WarehouseOrder(
                        latitude=float(row["latitude"]),
                        longitude=float(row["longtitude"]),
                        order_count=int(row["order_count"]),
                        total_desi=float(row["total_desi"]),
                        total_hj_desi=float(row.get("total_hj_desi", 0) or 0),
                        total_used_desi=float(row.get("total_used_desi", 0) or 0),
                        address_line_1=row.get("address_line_1"),
                        status=row.get("status")
                    )
                    orders.append(order)
                except Exception:
                    continue  # Skip rows with invalid data
    except Exception:
        raise WarehouseOrdersLoadError("CSV file could not be loaded.")
    return orders