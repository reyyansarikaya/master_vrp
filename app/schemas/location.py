from pydantic import BaseModel
from typing import Optional

class Depot(BaseModel):
    """
    Schema for a depot (starting location for delivery vehicles).

    Attributes:
        name (str): Name of the depot.
        lat (float): Latitude coordinate.
        lon (float): Longitude coordinate.
    """
    name: str
    lat: float
    lon: float

class WarehouseOrder(BaseModel):
    """
    Schema for a warehouse order pickup location.

    Attributes:
        latitude (float): Latitude of the order location.
        longitude (float): Longitude of the order location.
        order_count (int): Number of orders at the location.
        total_desi (float): Total desi volume for the location.
        total_hj_desi (Optional[float]): Additional desi (optional).
        total_used_desi (Optional[float]): Used desi value (optional).
        address_line_1 (Optional[str]): Address text.
        status (Optional[str]): Pickup status (e.g., success).
    """
    latitude: float
    longitude: float
    order_count: int
    total_desi: float
    total_hj_desi: Optional[float] = None
    total_used_desi: Optional[float] = None
    address_line_1: Optional[str] = None
    status: Optional[str] = None