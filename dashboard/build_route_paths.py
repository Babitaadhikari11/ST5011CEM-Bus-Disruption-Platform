from __future__ import annotations

import json
import zipfile
from pathlib import Path

import pandas as pd


# project folders
PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_FILE = PROJECT_ROOT / "dashboard" / "route_paths.json"

# reduce very long route paths for faster dashboard loading
MAX_POINTS_PER_ROUTE = 300


def find_gtfs_zip() -> tuple[Path, dict[str, str]]:
    """find a zip containing the required gtfs files"""

    required_files = {
        "routes.txt",
        "trips.txt",
        "shapes.txt"
    }

    for zip_path in PROJECT_ROOT.rglob("*.zip"):
        try:
            with zipfile.ZipFile(zip_path) as gtfs_zip:
                file_map = {
                    Path(file_name).name: file_name
                    for file_name in gtfs_zip.namelist()
                }

                if required_files.issubset(file_map.keys()):
                    return zip_path, file_map

        except zipfile.BadZipFile:
            continue

    raise FileNotFoundError(
        "No GTFS zip containing routes.txt, trips.txt "
        "and shapes.txt was found inside the project."
    )


def reduce_path(
    shape_points: pd.DataFrame
) -> list[list[float]]:
    """order and reduce the number of shape coordinates"""

    shape_points = shape_points.sort_values(
        "shape_pt_sequence"
    )

    if len(shape_points) > MAX_POINTS_PER_ROUTE:
        step = max(
            1,
            len(shape_points) // MAX_POINTS_PER_ROUTE
        )

        shape_points = shape_points.iloc[::step].copy()

    return [
        [
            float(row["shape_pt_lon"]),
            float(row["shape_pt_lat"])
        ]
        for _, row in shape_points.iterrows()
    ]


def main() -> None:
    gtfs_zip_path, gtfs_files = find_gtfs_zip()

    print(f"GTFS file found: {gtfs_zip_path}")

    with zipfile.ZipFile(gtfs_zip_path) as gtfs_zip:
        routes_df = pd.read_csv(
            gtfs_zip.open(gtfs_files["routes.txt"]),
            dtype=str
        )

        trips_df = pd.read_csv(
            gtfs_zip.open(gtfs_files["trips.txt"]),
            dtype=str
        )

        shapes_df = pd.read_csv(
            gtfs_zip.open(gtfs_files["shapes.txt"]),
            dtype=str
        )

    required_route_columns = {
        "route_id"
    }

    required_trip_columns = {
        "route_id",
        "shape_id"
    }

    required_shape_columns = {
        "shape_id",
        "shape_pt_lat",
        "shape_pt_lon",
        "shape_pt_sequence"
    }

    if not required_route_columns.issubset(routes_df.columns):
        raise ValueError(
            "routes.txt is missing route_id"
        )

    if not required_trip_columns.issubset(trips_df.columns):
        raise ValueError(
            "trips.txt is missing route_id or shape_id"
        )

    if not required_shape_columns.issubset(shapes_df.columns):
        raise ValueError(
            "shapes.txt is missing required coordinate columns"
        )

    # use route short name when available
    if "route_short_name" not in routes_df.columns:
        routes_df["route_short_name"] = routes_df["route_id"]

    routes_df["route"] = (
        routes_df["route_short_name"]
        .fillna(routes_df["route_id"])
        .astype(str)
        .str.strip()
    )

    # add direction when it is missing
    if "direction_id" not in trips_df.columns:
        trips_df["direction_id"] = "unknown"

    trips_df["direction_id"] = (
        trips_df["direction_id"]
        .fillna("unknown")
        .astype(str)
    )

    trips_df = trips_df.dropna(
        subset=["route_id", "shape_id"]
    )

    # connect trips with route names
    route_trips_df = trips_df.merge(
        routes_df[
            [
                "route_id",
                "route"
            ]
        ],
        on="route_id",
        how="inner"
    )

    # count how often each shape is used
    shape_usage_df = (
        route_trips_df
        .groupby(
            [
                "route",
                "direction_id",
                "shape_id"
            ]
        )
        .size()
        .reset_index(name="trip_count")
    )

    # choose the most frequently used shape
    representative_shapes_df = (
        shape_usage_df
        .sort_values(
            [
                "route",
                "direction_id",
                "trip_count"
            ],
            ascending=[
                True,
                True,
                False
            ]
        )
        .drop_duplicates(
            subset=[
                "route",
                "direction_id"
            ]
        )
    )

    # convert shape values to numbers
    shapes_df["shape_pt_lat"] = pd.to_numeric(
        shapes_df["shape_pt_lat"],
        errors="coerce"
    )

    shapes_df["shape_pt_lon"] = pd.to_numeric(
        shapes_df["shape_pt_lon"],
        errors="coerce"
    )

    shapes_df["shape_pt_sequence"] = pd.to_numeric(
        shapes_df["shape_pt_sequence"],
        errors="coerce"
    )

    shapes_df = shapes_df.dropna(
        subset=[
            "shape_id",
            "shape_pt_lat",
            "shape_pt_lon",
            "shape_pt_sequence"
        ]
    )

    selected_shape_ids = set(
        representative_shapes_df["shape_id"].astype(str)
    )

    shapes_df = shapes_df[
        shapes_df["shape_id"]
        .astype(str)
        .isin(selected_shape_ids)
    ]

    paths_by_shape = {}

    for shape_id, shape_points in shapes_df.groupby("shape_id"):
        route_path = reduce_path(shape_points)

        if len(route_path) >= 2:
            paths_by_shape[str(shape_id)] = route_path

    output_rows = []

    for _, selected_shape in representative_shapes_df.iterrows():
        shape_id = str(selected_shape["shape_id"])

        route_path = paths_by_shape.get(shape_id)

        if route_path is None:
            continue

        output_rows.append(
            {
                "route": str(selected_shape["route"]),
                "direction_id": str(
                    selected_shape["direction_id"]
                ),
                "shape_id": shape_id,
                "path": route_path
            }
        )

    OUTPUT_FILE.write_text(
        json.dumps(
            output_rows,
            ensure_ascii=False
        ),
        encoding="utf-8"
    )

    print(f"Created: {OUTPUT_FILE}")
    print(f"Route paths created: {len(output_rows)}")


if __name__ == "__main__":
    main()
