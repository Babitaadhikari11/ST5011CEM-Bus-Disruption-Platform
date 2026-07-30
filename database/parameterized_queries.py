import json
import sqlite3
from pathlib import Path

project_root = Path(__file__).resolve().parents[1]
json_path = project_root / "dashboard" / "dashboard_data.json"
database_path = project_root / "database" / "bus_recovery.db"

with json_path.open("r", encoding="utf-8") as file:
    dashboard_data = json.load(file)

routes = dashboard_data.get("routes", [])

connection = sqlite3.connect(database_path)
cursor = connection.cursor()

cursor.execute("DROP TABLE IF EXISTS route_recovery")

cursor.execute(
    """
    CREATE TABLE route_recovery (
        route_name TEXT,
        direction TEXT,
        predicted_severity TEXT,
        predicted_risk REAL,
        recovery_priority_score REAL,
        recovery_priority_level TEXT,
        recommended_action TEXT
    )
    """
)

records = []

for route in routes:
    route_name = (
        route.get("published_line_name")
        or route.get("line_ref")
        or "unknown"
    )

    records.append(
        (
            str(route_name),
            str(route.get("direction_ref") or "unknown"),
            str(route.get("predicted_severity") or "unknown"),
            float(route.get("predicted_risk_probability") or 0),
            float(route.get("recovery_priority_score") or 0),
            str(route.get("recovery_priority_level") or "unknown"),
            str(route.get("recommended_recovery_action") or "operator review")
        )
    )

cursor.executemany(
    """
    INSERT INTO route_recovery (
        route_name,
        direction,
        predicted_severity,
        predicted_risk,
        recovery_priority_score,
        recovery_priority_level,
        recommended_action
    )
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """,
    records
)

connection.commit()

selected_priority = input(
    "enter priority level low, medium, high or critical: "
).strip().lower()

allowed_priorities = {
    "low",
    "medium",
    "high",
    "critical"
}

if selected_priority not in allowed_priorities:
    connection.close()
    raise ValueError("invalid priority level")

cursor.execute(
    """
    SELECT
        route_name,
        direction,
        predicted_severity,
        ROUND(recovery_priority_score, 2),
        recommended_action
    FROM route_recovery
    WHERE recovery_priority_level = ?
    ORDER BY recovery_priority_score DESC
    LIMIT ?
    """,
    (
        selected_priority,
        10
    )
)

results = cursor.fetchall()

print()
print("database rows:", len(records))
print("selected priority:", selected_priority)
print("top matching routes:")
print()

for row in results:
    print(row)

connection.close()
