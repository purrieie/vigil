import pandas as pd

def compute_hotspots(csv_path: str = "data/sample_complaints.csv", grid_size: float = 0.05):
    df = pd.read_csv(csv_path)
    df["grid_lat"] = (df["lat"] / grid_size).round() * grid_size
    df["grid_lon"] = (df["lon"] / grid_size).round() * grid_size

    grouped = df.groupby(["grid_lat", "grid_lon"]).size().reset_index(name="count")
    grouped = grouped.sort_values("count", ascending=False)

    hotspots = grouped.to_dict(orient="records")
    return hotspots