import requests
from typing import List
from app.config import settings
from app.exceptions import DistanceMatrixAPIError
import time
import os
import json

import os
import json
from typing import List


def load_or_build_distance_matrix(locations: List[str], branch_name: str) -> List[List[int]]:
    cache_path = f"/Users/reyyansarikaya/Desktop/Projects/master_vrp/app/cache/{branch_name.lower()}_distance_matrix.json"

    # 1. Eğer dosya varsa, yüklemeyi dene
    if os.path.exists(cache_path):
        try:
            with open(cache_path, "r") as f:
                matrix = json.load(f)
            # 2. Matrix'in geçerli 2D liste olduğunu kontrol et
            if not matrix or not isinstance(matrix, list) or not all(isinstance(row, list) for row in matrix):
                raise ValueError(f"Invalid matrix format in cache file: {cache_path}")
            print(f"[INFO] Loaded cached distance matrix for {branch_name}")
            print(f"[DEBUG] Matrix shape: {len(matrix)}x{len(matrix[0])}")
            return matrix
        except Exception as e:
            print(f"[WARNING] Failed to load cache: {e}. Rebuilding matrix...")

    # 3. Dosya yoksa ya da okuma başarısızsa yeniden oluştur
    print(f"[INFO] Building new distance matrix for {branch_name}")
    matrix = build_distance_matrix(locations, locations)
    print("[DEBUG] Matrix built")
    print(f"[DEBUG] Matrix shape: {len(matrix)}x{len(matrix[0])}")

    os.makedirs(os.path.dirname(cache_path), exist_ok=True)
    with open(cache_path, "w") as f:
        json.dump(matrix, f)
    print(f"[INFO] Written to: {cache_path}")

    return matrix

# Yardımcı: listeyi parçalayarak chunk'lara ayır
def chunk_list(lst: List[str], chunk_size: int) -> List[List[str]]:
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]

def build_distance_matrix(origins: List[str], destinations: List[str]) -> List[List[int]]:
    """
    Builds a full distance matrix by batching both origins and destinations
    to stay under the Google Distance Matrix API 100 element limit.
    Uses current traffic data.

    Args:
        origins (List[str]): List of origin coordinates.
        destinations (List[str]): List of destination coordinates.

    Returns:
        List[List[int]]: Full distance matrix (origins x destinations).

    Raises:
        DistanceMatrixAPIError: If any batch request fails.
    """
    MAX_ELEMENTS = 100
    chunk_size = max(1, int(MAX_ELEMENTS ** 0.5))

    origin_chunks = chunk_list(origins, chunk_size)
    destination_chunks = chunk_list(destinations, chunk_size)

    full_matrix = [[0 for _ in range(len(destinations))] for _ in range(len(origins))]

    for i, origin_chunk in enumerate(origin_chunks):
        for j, destination_chunk in enumerate(destination_chunks):
            departure_time = int(time.time())  # Şu anki zaman, her istek için güncel

            params = {
                "origins": "|".join(origin_chunk),
                "destinations": "|".join(destination_chunk),
                "key": settings.GOOGLE_API_KEY,
                "departure_time": departure_time,
                "traffic_model": "best_guess",
                "units": "metric",
                "mode": "driving"
            }

            print(f"\n--- API Request [{i},{j}] ---")
            print(params)

            response = requests.get(settings.GOOGLE_DISTANCE_MATRIX_URL, params=params)

            if response.status_code != 200:
                raise DistanceMatrixAPIError(f"HTTP {response.status_code}: {response.text}")

            data = response.json()
            if data.get("status") != "OK":
                raise DistanceMatrixAPIError(data.get("status", "Unknown error"))

            for oi, row in enumerate(data["rows"]):
                for di, element in enumerate(row["elements"]):
                    if element.get("status") != "OK":
                        raise DistanceMatrixAPIError(f"Element error: {element.get('status')}")
                    orig_idx = i * chunk_size + oi
                    dest_idx = j * chunk_size + di
                    if orig_idx < len(origins) and dest_idx < len(destinations):
                        full_matrix[orig_idx][dest_idx] = element["duration"]["value"]

            time.sleep(1)  # throttling önlemek için bekleme

    return full_matrix
