# Master VRP - Vehicle Routing Problem Solver

A Python-based Vehicle Routing Problem (VRP) solver that optimizes delivery routes for multiple branches using Google's OR-Tools. This project solves complex routing problems with time windows, vehicle capacity constraints, and lunch breaks.

## 🚀 Features

- **Multi-branch VRP solving**: Handles routing for multiple branches (Esenyurt, Haramidere)
- **Time window constraints**: Respects working hours (8:00-17:00) and lunch breaks
- **Vehicle capacity management**: Optimizes routes based on vehicle capacity (15,000 units)
- **Distance matrix caching**: Uses Google Distance Matrix API with local caching
- **CSV output**: Generates detailed route reports in CSV format
- **JSON solution storage**: Saves complete solution data for analysis

## 📋 Prerequisites

- Python 3.9+
- Google Maps API key (for distance calculations)
- Virtual environment (recommended)

## 🛠️ Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd master_vrp
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   Create a `.env` file in the root directory:
   ```env
   GOOGLE_API_KEY=your_google_maps_api_key_here
   DATABASE_URL=sqlite:///./master_vrp.db
   ```

## 📁 Project Structure

```
master_vrp/
├── main.py                 # Main entry point
├── requirements.txt        # Python dependencies
├── README.md              # This file
├── app/
│   ├── config.py          # Configuration settings
│   ├── utils.py           # Utility functions
│   ├── exceptions.py      # Custom exceptions
│   ├── data/              # Input data files
│   │   ├── Esenyurt_Orders.csv
│   │   ├── Haramidere_Orders.csv
│   │   └── depots.json
│   ├── scripts/
│   │   └── multi_vrp_solver.py  # Main VRP solver
│   ├── services/
│   │   ├── distance_matrix.py    # Distance calculation service
│   │   └── vrp_solver.py         # OR-Tools VRP solver
│   ├── schemas/           # Data schemas
│   ├── outputs/           # Generated output files
│   └── cache/             # Distance matrix cache
```

## 🚀 Usage

### Running the VRP Solver

1. **Ensure your data is ready**
   - Place order CSV files in `app/data/`
   - Update `depots.json` with your depot coordinates
   - Verify your Google API key is set

2. **Run the solver**
   ```bash
   python main.py
   ```

3. **Check outputs**
   - CSV route files: `app/outputs/{branch}_routes.csv`
   - JSON solution files: `app/outputs/{branch}_solution.json`

### Configuration

Key parameters in `app/scripts/multi_vrp_solver.py`:

- `WORK_START`: 8:00 (28800 seconds)
- `WORK_END`: 17:00 (61200 seconds)
- `LUNCH_BREAK`: 12:00-13:00
- `SERVICE_TIME_PER_DESI`: 5 seconds per unit
- `VEHICLE_CAPACITY`: 15,000 units
- `BRANCH_VEHICLES`: Number of vehicles per branch

## 📊 Output Format

### CSV Route Files
Each branch generates a CSV file with columns:
- `branch`: Branch name
- `vehicle_id`: Vehicle identifier
- `step_order`: Order of stops in route
- `location_index`: Location index in distance matrix
- `arrival_time (sec)`: Arrival time in seconds

### JSON Solution Files
Complete solution data including:
- Route assignments
- Vehicle utilization
- Total distance and time
- Constraint violations (if any)

## 🔧 Dependencies

- **OR-Tools**: Google's optimization library for VRP solving
- **Pandas**: Data manipulation and CSV handling
- **NumPy**: Numerical computations
- **Requests**: HTTP requests for Google Distance Matrix API
- **SQLAlchemy**: Database operations
- **Pydantic**: Data validation

## 📝 Data Requirements

### Order CSV Format
Each order CSV should contain:
- `latitude`, `longtitude`: Location coordinates
- `total_used_desi`: Demand quantity
- Additional order metadata

### Depot JSON Format
```json
[
  {
    "name": "Branch Name",
    "lat": 41.040641,
    "lon": 28.660911
  }
]
```

## 🔍 Troubleshooting

### Common Issues

1. **Google API Key Error**
   - Ensure your API key is valid and has Distance Matrix API enabled
   - Check the `.env` file is in the correct location

2. **No Solution Found**
   - Verify vehicle capacity is sufficient for total demand
   - Check time windows are reasonable
   - Ensure depot coordinates are correct

3. **Distance Matrix Errors**
   - Clear the cache directory: `rm -rf app/cache/`
   - Verify internet connection for API calls

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Google OR-Tools for the optimization engine
- Google Maps API for distance calculations
- The VRP research community for algorithms and insights
