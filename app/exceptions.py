class MasterVRPException(Exception):
    """Base exception for the Master VRP project."""
    pass


class DepotFileNotFoundError(MasterVRPException):
    """Raised when depot data file is missing or unreadable."""
    def __init__(self, filepath: str):
        self.filepath = filepath
        super().__init__(f"Depot file not found: {filepath}")


class WarehouseOrdersLoadError(MasterVRPException):
    """Raised when warehouse order locations could not be loaded."""
    def __init__(self, message="Failed to load warehouse orders from file."):
        super().__init__(message)


class DistanceMatrixAPIError(MasterVRPException):
    """Raised when Google Maps Distance Matrix API fails."""
    def __init__(self, status: str):
        self.status = status
        super().__init__(f"Distance Matrix API returned error: {status}")


class NoRoutesFoundError(MasterVRPException):
    """Raised when OR-Tools does not find any route."""
    def __init__(self):
        super().__init__("No routes found by VRP solver.")