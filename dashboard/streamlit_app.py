from __future__ import annotations

import json
import os
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd
import plotly.express as px
import pydeck as pdk
import requests
import streamlit as st
from dotenv import load_dotenv


st.set_page_config(
    page_title="Bus Recovery Dashboard",
    page_icon="🚌",
    layout="wide",
    initial_sidebar_state="collapsed"
)


DASHBOARD_ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = DASHBOARD_ROOT.parent
DATA_FILE = DASHBOARD_ROOT / "dashboard_data.json"

load_dotenv(
    PROJECT_ROOT
    / ".env"
)


if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False


header_left, header_right = st.columns(
    [
        8,
        1.3
    ],
    vertical_alignment="center"
)


with header_right:
    dark_mode = st.toggle(
        "Dark mode",
        value=st.session_state.dark_mode,
        key="dark_mode"
    )


if dark_mode:
    page_background = "#08111f"
    surface_background = "#111c2e"
    soft_background = "#162338"
    text_colour = "#edf3fb"
    muted_colour = "#9fb0c6"
    border_colour = "#283a54"
    input_background = "#111c2e"
    map_style = "dark"
    card_shadow = "0 10px 30px rgba(0, 0, 0, 0.25)"
    status_background = "#102a4c"
    status_text = "#93c5fd"
    status_border = "#1d4ed8"

else:
    page_background = "#f5f7fb"
    surface_background = "#ffffff"
    soft_background = "#f8fafc"
    text_colour = "#13213a"
    muted_colour = "#64748b"
    border_colour = "#e2e8f0"
    input_background = "#ffffff"
    map_style = "light"
    card_shadow = "0 8px 25px rgba(15, 39, 71, 0.06)"
    status_background = "#eff6ff"
    status_text = "#1d4ed8"
    status_border = "#bfdbfe"


st.markdown(
    f"""
    <style>
    header[data-testid="stHeader"] {{
        background: transparent;
        height: 2.7rem;
    }}

    [data-testid="stToolbar"] {{
        top: 0.35rem;
    }}

    .stApp {{
        background: {page_background};
        color: {text_colour};
    }}

    .block-container {{
        max-width: 1450px;
        padding-top: 4.1rem;
        padding-bottom: 2rem;
    }}

    .dashboard-title {{
        font-size: 2rem;
        font-weight: 850;
        line-height: 1.2;
        letter-spacing: -0.03em;
        margin: 0 0 0.2rem;
        padding: 0;
        color: {text_colour};
    }}

    .dashboard-subtitle {{
        color: {muted_colour};
        margin: 0 0 1rem;
    }}

    .section-label {{
        color: #2563eb;
        font-size: 0.72rem;
        font-weight: 850;
        letter-spacing: 0.1em;
        margin-bottom: 0.25rem;
    }}

    .section-title {{
        color: {text_colour};
        font-size: 1.25rem;
        font-weight: 800;
        margin-bottom: 0.2rem;
    }}

    .section-note {{
        color: {muted_colour};
        font-size: 0.8rem;
        margin-bottom: 0.7rem;
    }}

    .kpi-card {{
        min-height: 7rem;
        padding: 1rem;
        border-radius: 1rem;
        background: {surface_background};
        border: 1px solid {border_colour};
        box-shadow: {card_shadow};
    }}

    .kpi-label {{
        color: {muted_colour};
        font-size: 0.76rem;
        margin-bottom: 0.7rem;
    }}

    .kpi-value {{
        color: {text_colour};
        font-size: 1.6rem;
        font-weight: 850;
        line-height: 1;
    }}

    .kpi-detail {{
        color: {muted_colour};
        font-size: 0.7rem;
        margin-top: 0.55rem;
    }}

    .simple-panel {{
        padding: 1rem;
        border-radius: 1rem;
        background: {surface_background};
        border: 1px solid {border_colour};
        box-shadow: {card_shadow};
        margin-bottom: 1rem;
    }}

    .live-status {{
        padding: 0.65rem 0.8rem;
        border-radius: 0.7rem;
        background: {status_background};
        color: {status_text};
        border: 1px solid {status_border};
        font-size: 0.82rem;
        margin-bottom: 0.6rem;
    }}

    .legend-row {{
        display: flex;
        gap: 0.9rem;
        flex-wrap: wrap;
        color: {muted_colour};
        font-size: 0.76rem;
        margin-bottom: 0.6rem;
    }}

    .legend-dot {{
        display: inline-block;
        width: 0.55rem;
        height: 0.55rem;
        border-radius: 50%;
        margin-right: 0.25rem;
    }}

    .route-card {{
        padding: 0.75rem;
        margin-bottom: 0.55rem;
        border-radius: 0.8rem;
        border: 1px solid {border_colour};
        background: {soft_background};
    }}

    .route-card-title {{
        display: flex;
        justify-content: space-between;
        gap: 0.5rem;
        align-items: center;
        font-weight: 800;
        color: {text_colour};
    }}

    .route-card-meta {{
        color: {muted_colour};
        font-size: 0.73rem;
        margin-top: 0.25rem;
    }}

    .pill {{
        padding: 0.18rem 0.5rem;
        border-radius: 999px;
        font-size: 0.66rem;
        font-weight: 850;
        text-transform: capitalize;
    }}

    .pill-low {{
        background: #dcfce7;
        color: #166534;
    }}

    .pill-medium {{
        background: #fef3c7;
        color: #92400e;
    }}

    .pill-high {{
        background: #ffedd5;
        color: #9a3412;
    }}

    .pill-critical {{
        background: #fee2e2;
        color: #991b1b;
    }}

    div[data-baseweb="input"] > div,
    div[data-baseweb="select"] > div {{
        background: {input_background};
        color: {text_colour};
        border-color: {border_colour};
    }}

    div[data-testid="stDataFrame"] {{
        border: 1px solid {border_colour};
        border-radius: 1rem;
        overflow: hidden;
    }}

    label,
    .stCheckbox,
    .stToggle {{
        color: {text_colour};
    }}

    footer {{
        visibility: hidden;
    }}
    </style>
    """,
    unsafe_allow_html=True
)


def local_name(
    tag: str
) -> str:
    return tag.split(
        "}"
    )[-1]


def first_text(
    element: ET.Element,
    wanted_name: str
) -> str | None:
    for child in element.iter():
        if local_name(
            child.tag
        ) == wanted_name:
            if child.text is not None:
                value = child.text.strip()

                if value:
                    return value

    return None


def parse_float(
    value: str | None
) -> float | None:
    if value is None:
        return None

    try:
        return float(
            value
        )

    except (
        TypeError,
        ValueError
    ):
        return None


def parse_timestamp(
    value: str | None
) -> datetime | None:
    if not value:
        return None

    cleaned = value.replace(
        "Z",
        "+00:00"
    )

    try:
        parsed = datetime.fromisoformat(
            cleaned
        )

    except ValueError:
        return None

    if parsed.tzinfo is None:
        parsed = parsed.replace(
            tzinfo=timezone.utc
        )

    return parsed.astimezone(
        timezone.utc
    )


def get_secret(
    name: str,
    default: str | None = None
) -> str | None:
    try:
        value = st.secrets.get(
            name,
            None
        )

    except FileNotFoundError:
        value = None

    if value:
        return str(
            value
        )

    environment_value = os.getenv(
        name
    )

    if environment_value:
        return environment_value

    return default


@st.cache_data(
    show_spinner=False
)
def load_dashboard_data(
    file_path: str,
    modified_time: float
) -> dict[str, Any]:
    del modified_time

    path = Path(
        file_path
    )

    return json.loads(
        path.read_text(
            encoding="utf-8"
        )
    )


@st.cache_data(
    ttl=45,
    show_spinner=False
)
def fetch_live_vehicles(
    api_key: str,
    feed_id: str
) -> dict[str, Any]:
    feed_url = (
        "https://data.bus-data.dft.gov.uk/"
        f"api/v1/datafeed/{feed_id}/"
    )

    response = requests.get(
        feed_url,
        params={
            "api_key": api_key
        },
        timeout=120
    )

    response.raise_for_status()

    if not (
        response.content
        .lstrip()[:100]
        .startswith(
            b"<"
        )
    ):
        raise RuntimeError(
            "the BODS response was not XML"
        )

    root = ET.fromstring(
        response.content
    )

    fetched_at = datetime.now(
        timezone.utc
    )

    vehicle_rows: list[dict[str, Any]] = []

    for activity in root.iter():
        if local_name(
            activity.tag
        ) != "VehicleActivity":
            continue

        latitude = parse_float(
            first_text(
                activity,
                "Latitude"
            )
        )

        longitude = parse_float(
            first_text(
                activity,
                "Longitude"
            )
        )

        if latitude is None or longitude is None:
            continue

        if not (
            -90 <= latitude <= 90
            and
            -180 <= longitude <= 180
        ):
            continue

        recorded_text = first_text(
            activity,
            "RecordedAtTime"
        )

        recorded_time = parse_timestamp(
            recorded_text
        )

        age_seconds = None

        if recorded_time is not None:
            age_seconds = max(
                0,
                int(
                    (
                        fetched_at
                        -
                        recorded_time
                    ).total_seconds()
                )
            )

        vehicle_rows.append(
            {
                "vehicle_ref": first_text(
                    activity,
                    "VehicleRef"
                ),
                "line_ref": first_text(
                    activity,
                    "LineRef"
                ),
                "published_line_name": first_text(
                    activity,
                    "PublishedLineName"
                ),
                "direction_ref": first_text(
                    activity,
                    "DirectionRef"
                ),
                "destination_name": first_text(
                    activity,
                    "DestinationName"
                ),
                "recorded_at_time": recorded_text,
                "observation_age_seconds": age_seconds,
                "latitude": latitude,
                "longitude": longitude
            }
        )

    return {
        "fetched_at": fetched_at.isoformat(),
        "vehicles": vehicle_rows
    }


def priority_colour(
    priority: str
) -> list[int]:
    colours = {
        "critical": [
            220,
            38,
            38,
            220
        ],
        "high": [
            234,
            88,
            12,
            220
        ],
        "medium": [
            217,
            119,
            6,
            220
        ],
        "low": [
            22,
            163,
            74,
            220
        ]
    }

    return colours.get(
        str(
            priority
        ).lower(),
        [
            100,
            116,
            139,
            210
        ]
    )


def prepare_priority_points(
    routes: pd.DataFrame
) -> pd.DataFrame:
    if routes.empty:
        return pd.DataFrame()

    points = routes.copy()

    points[
        "latitude"
    ] = pd.to_numeric(
        points[
            "map_latitude"
        ],
        errors="coerce"
    )

    points[
        "longitude"
    ] = pd.to_numeric(
        points[
            "map_longitude"
        ],
        errors="coerce"
    )

    points = points.dropna(
        subset=[
            "latitude",
            "longitude"
        ]
    )

    points[
        "marker_type"
    ] = "Route recovery location"

    points[
        "route"
    ] = points[
        "published_line_name"
    ].fillna(
        points[
            "line_ref"
        ]
    ).astype(
        str
    )

    points[
        "direction"
    ] = points[
        "direction_ref"
    ].fillna(
        "unknown"
    ).astype(
        str
    )

    points[
        "severity"
    ] = points[
        "predicted_severity"
    ].fillna(
        "unknown"
    ).astype(
        str
    )

    risk_values = pd.to_numeric(
        points[
            "predicted_risk_probability"
        ],
        errors="coerce"
    ).fillna(
        0
    )

    score_values = pd.to_numeric(
        points[
            "recovery_priority_score"
        ],
        errors="coerce"
    ).fillna(
        0
    )

    points[
        "risk_display"
    ] = (
        risk_values
        *
        100
    ).round(
        1
    ).astype(
        str
    ) + "%"

    points[
        "priority_score_display"
    ] = score_values.round(
        2
    ).astype(
        str
    )

    points[
        "priority"
    ] = points[
        "recovery_priority_level"
    ].fillna(
        "unknown"
    ).astype(
        str
    )

    points[
        "vehicle_ref"
    ] = "-"

    points[
        "destination"
    ] = "-"

    points[
        "recorded_at"
    ] = points[
        "event_snapshot_time"
    ].fillna(
        "-"
    ).astype(
        str
    )

    points[
        "age_display"
    ] = "-"

    points[
        "colour"
    ] = points[
        "priority"
    ].apply(
        priority_colour
    )

    points[
        "radius"
    ] = (
        180
        +
        score_values
        *
        6
    ).clip(
        lower=180,
        upper=550
    )

    return points[
        [
            "marker_type",
            "route",
            "direction",
            "severity",
            "risk_display",
            "priority_score_display",
            "priority",
            "vehicle_ref",
            "destination",
            "recorded_at",
            "age_display",
            "latitude",
            "longitude",
            "colour",
            "radius"
        ]
    ]


def prepare_live_points(
    vehicles: pd.DataFrame
) -> pd.DataFrame:
    if vehicles.empty:
        return pd.DataFrame()

    points = vehicles.copy()

    points[
        "marker_type"
    ] = "Near-live vehicle"

    points[
        "route"
    ] = points[
        "published_line_name"
    ].fillna(
        points[
            "line_ref"
        ]
    ).fillna(
        "unknown"
    ).astype(
        str
    )

    points[
        "direction"
    ] = points[
        "direction_ref"
    ].fillna(
        "unknown"
    ).astype(
        str
    )

    points[
        "severity"
    ] = "-"

    points[
        "risk_display"
    ] = "-"

    points[
        "priority_score_display"
    ] = "-"

    points[
        "priority"
    ] = "-"

    points[
        "destination"
    ] = points[
        "destination_name"
    ].fillna(
        "-"
    ).astype(
        str
    )

    points[
        "recorded_at"
    ] = points[
        "recorded_at_time"
    ].fillna(
        "-"
    ).astype(
        str
    )

    points[
        "age_display"
    ] = (
        pd.to_numeric(
            points[
                "observation_age_seconds"
            ],
            errors="coerce"
        )
        .fillna(
            0
        )
        .astype(
            int
        )
        .astype(
            str
        )
        +
        " seconds"
    )

    points[
        "colour"
    ] = [
        [
            37,
            99,
            235,
            210
        ]
        for _ in range(
            len(
                points
            )
        )
    ]

    points[
        "radius"
    ] = 70

    return points[
        [
            "marker_type",
            "route",
            "direction",
            "severity",
            "risk_display",
            "priority_score_display",
            "priority",
            "vehicle_ref",
            "destination",
            "recorded_at",
            "age_display",
            "latitude",
            "longitude",
            "colour",
            "radius"
        ]
    ]


def make_map(
    priority_points: pd.DataFrame,
    live_points: pd.DataFrame
) -> pdk.Deck:
    frames = [
        dataframe
        for dataframe in [
            priority_points,
            live_points
        ]
        if not dataframe.empty
    ]

    if frames:
        points = pd.concat(
            frames,
            ignore_index=True
        )

        latitude = float(
            points[
                "latitude"
            ].mean()
        )

        longitude = float(
            points[
                "longitude"
            ].mean()
        )

    else:
        points = pd.DataFrame()
        latitude = 52.4862
        longitude = -1.8904

    layer = pdk.Layer(
        "ScatterplotLayer",
        data=points,
        get_position=[
            "longitude",
            "latitude"
        ],
        get_fill_color="colour",
        get_line_color=[
            255,
            255,
            255,
            220
        ],
        get_radius="radius",
        radius_min_pixels=3,
        radius_max_pixels=15,
        line_width_min_pixels=1,
        pickable=True,
        filled=True,
        stroked=True
    )

    tooltip = {
        "html": """
        <b>{marker_type}</b><br/>
        Route: {route}<br/>
        Direction: {direction}<br/>
        Vehicle: {vehicle_ref}<br/>
        Destination: {destination}<br/>
        Severity: {severity}<br/>
        Risk: {risk_display}<br/>
        Priority score: {priority_score_display}<br/>
        Priority: {priority}<br/>
        Recorded: {recorded_at}<br/>
        Age: {age_display}
        """,
        "style": {
            "backgroundColor": "#0f172a",
            "color": "white",
            "fontSize": "12px"
        }
    }

    return pdk.Deck(
        map_style=map_style,
        initial_view_state=pdk.ViewState(
            latitude=latitude,
            longitude=longitude,
            zoom=9.5,
            pitch=0
        ),
        layers=[
            layer
        ],
        tooltip=tooltip
    )


def render_kpi(
    label: str,
    value: str,
    detail: str
) -> None:
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-label">{label}</div>
            <div class="kpi-value">{value}</div>
            <div class="kpi-detail">{detail}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


if not DATA_FILE.exists():
    st.error(
        "dashboard_data.json is missing"
    )

    st.stop()


saved_data = load_dashboard_data(
    str(
        DATA_FILE
    ),
    DATA_FILE.stat().st_mtime
)


routes_df = pd.DataFrame(
    saved_data.get(
        "routes",
        []
    )
)

kpis = saved_data.get(
    "kpis",
    {}
)


api_key = get_secret(
    "BODS_API_KEY"
)

feed_id = get_secret(
    "BODS_FEED_ID",
    "10609"
)


with header_left:
    st.markdown(
        '<div class="dashboard-title">'
        'Bus Disruption and Route Recovery Dashboard'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="dashboard-subtitle">'
        'Simple map of near-live vehicles and the latest saved route priorities'
        '</div>',
        unsafe_allow_html=True
    )


kpi_columns = st.columns(
    4
)


with kpi_columns[
    0
]:
    render_kpi(
        "Predictions",
        f"{int(kpis.get('total_predictions', 0)):,}",
        "Test records scored"
    )


with kpi_columns[
    1
]:
    render_kpi(
        "High severity",
        f"{int(kpis.get('predicted_high_severity', 0)):,}",
        "Predicted high irregularity"
    )


with kpi_columns[
    2
]:
    render_kpi(
        "High priority",
        f"{int(kpis.get('high_priority_records', 0)):,}",
        "Routes requiring review"
    )


with kpi_columns[
    3
]:
    render_kpi(
        "Best model",
        str(
            kpis.get(
                "best_model",
                "-"
            )
        ).title(),
        f"Macro F1 {float(kpis.get('best_macro_f1', 0)):.4f}"
    )


st.write("")


filter_column_1, filter_column_2, filter_column_3 = st.columns(
    [
        2,
        1,
        1
    ]
)


with filter_column_1:
    route_search = st.text_input(
        "Search route",
        placeholder="Example: 15, X10 or 937"
    )


with filter_column_2:
    priority_filter = st.selectbox(
        "Priority",
        [
            "all",
            "high",
            "medium",
            "low",
            "critical"
        ]
    )


with filter_column_3:
    show_live = st.checkbox(
        "Show near-live buses",
        value=True
    )


filtered_routes = routes_df.copy()


if route_search:
    search_value = route_search.lower()

    search_text = (
        filtered_routes[
            "line_ref"
        ]
        .fillna(
            ""
        )
        .astype(
            str
        )
        +
        " "
        +
        filtered_routes[
            "published_line_name"
        ]
        .fillna(
            ""
        )
        .astype(
            str
        )
    ).str.lower()

    filtered_routes = filtered_routes[
        search_text.str.contains(
            search_value,
            regex=False
        )
    ]


if priority_filter != "all":
    filtered_routes = filtered_routes[
        filtered_routes[
            "recovery_priority_level"
        ]
        .fillna(
            ""
        )
        .astype(
            str
        )
        .str.lower()
        ==
        priority_filter
    ]


map_column, route_column = st.columns(
    [
        3,
        1
    ]
)


with map_column:
    st.markdown(
        '<div class="section-label">MAP</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="section-title">'
        'Vehicle and route-priority locations'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="legend-row">'
        '<span><i class="legend-dot" style="background:#2563eb"></i>Near-live bus</span>'
        '<span><i class="legend-dot" style="background:#22a34a"></i>Low</span>'
        '<span><i class="legend-dot" style="background:#d97706"></i>Medium</span>'
        '<span><i class="legend-dot" style="background:#ea580c"></i>High</span>'
        '<span><i class="legend-dot" style="background:#dc2626"></i>Critical</span>'
        '</div>',
        unsafe_allow_html=True
    )

    priority_points = prepare_priority_points(
        filtered_routes
    )


    @st.fragment(
        run_every="60s"
    )
    def render_map() -> None:
        live_points = pd.DataFrame()

        if show_live:
            if not api_key:
                st.warning(
                    "Near-live buses are hidden because the BODS API key is not configured"
                )

            else:
                try:
                    live_payload = fetch_live_vehicles(
                        api_key,
                        str(
                            feed_id
                        )
                    )

                    live_vehicle_df = pd.DataFrame(
                        live_payload.get(
                            "vehicles",
                            []
                        )
                    )

                    if route_search and not live_vehicle_df.empty:
                        search_value = route_search.lower()

                        live_text = (
                            live_vehicle_df[
                                "line_ref"
                            ]
                            .fillna(
                                ""
                            )
                            .astype(
                                str
                            )
                            +
                            " "
                            +
                            live_vehicle_df[
                                "published_line_name"
                            ]
                            .fillna(
                                ""
                            )
                            .astype(
                                str
                            )
                        ).str.lower()

                        live_vehicle_df = live_vehicle_df[
                            live_text.str.contains(
                                search_value,
                                regex=False
                            )
                        ]

                    live_points = prepare_live_points(
                        live_vehicle_df
                    )

                    st.markdown(
                        '<div class="live-status">'
                        f'<b>{len(live_points):,}</b> near-live buses '
                        f'· updated {live_payload.get("fetched_at", "-")}'
                        '</div>',
                        unsafe_allow_html=True
                    )

                except (
                    requests.RequestException,
                    RuntimeError,
                    ET.ParseError
                ) as error:
                    st.warning(
                        f"Near-live feed unavailable: {error}"
                    )

        st.pydeck_chart(
            make_map(
                priority_points,
                live_points
            ),
            width="stretch",
            height=560
        )


    render_map()


with route_column:
    st.markdown(
        '<div class="section-label">TOP ROUTES</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="section-title">'
        'Routes needing attention'
        '</div>',
        unsafe_allow_html=True
    )

    top_routes = (
        filtered_routes
        .sort_values(
            "latest_recovery_rank"
        )
        .head(
            8
        )
    )

    if top_routes.empty:
        st.info(
            "No routes match the filters"
        )

    else:
        for _, route in top_routes.iterrows():
            route_name = route.get(
                "published_line_name",
                route.get(
                    "line_ref",
                    "-"
                )
            )

            rank = int(
                route.get(
                    "latest_recovery_rank",
                    0
                )
            )

            priority = str(
                route.get(
                    "recovery_priority_level",
                    "low"
                )
            ).lower()

            direction = str(
                route.get(
                    "direction_ref",
                    "-"
                )
            )

            score = float(
                route.get(
                    "recovery_priority_score",
                    0
                )
            )

            risk = float(
                route.get(
                    "predicted_risk_probability",
                    0
                )
            )

            st.markdown(
                f"""
                <div class="route-card">
                    <div class="route-card-title">
                        <span>#{rank} Route {route_name}</span>
                        <span class="pill pill-{priority}">
                            {priority}
                        </span>
                    </div>
                    <div class="route-card-meta">
                        {direction} · score {score:.2f} · risk {risk * 100:.1f}%
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )


st.write("")


chart_column, table_column = st.columns(
    [
        1,
        2
    ]
)


with chart_column:
    st.markdown(
        '<div class="section-label">SUMMARY</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="section-title">'
        'Priority distribution'
        '</div>',
        unsafe_allow_html=True
    )

    if filtered_routes.empty:
        st.info(
            "No priority data"
        )

    else:
        priority_summary = (
            filtered_routes[
                "recovery_priority_level"
            ]
            .fillna(
                "unknown"
            )
            .value_counts()
            .rename_axis(
                "priority"
            )
            .reset_index(
                name="count"
            )
        )

        priority_chart = px.bar(
            priority_summary,
            x="priority",
            y="count",
            color="priority",
            color_discrete_map={
                "low": "#22a34a",
                "medium": "#d97706",
                "high": "#ea580c",
                "critical": "#dc2626"
            }
        )

        priority_chart.update_layout(
            showlegend=False,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color=text_colour,
            xaxis_title="Priority",
            yaxis_title="Route count",
            margin=dict(
                l=10,
                r=10,
                t=10,
                b=10
            )
        )

        st.plotly_chart(
            priority_chart,
            width="stretch",
            config={
                "displayModeBar": False
            }
        )


with table_column:
    st.markdown(
        '<div class="section-label">RANKING</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="section-title">'
        'Latest route recovery ranking'
        '</div>',
        unsafe_allow_html=True
    )

    table_columns = [
        "latest_recovery_rank",
        "published_line_name",
        "direction_ref",
        "predicted_severity",
        "recovery_priority_score",
        "recovery_priority_level",
        "recommended_recovery_action"
    ]

    available_columns = [
        column_name
        for column_name in table_columns
        if column_name in filtered_routes.columns
    ]

    ranking_table = (
        filtered_routes[
            available_columns
        ]
        .sort_values(
            "latest_recovery_rank"
        )
        .head(
            20
        )
    )

    st.dataframe(
        ranking_table,
        width="stretch",
        height=430,
        hide_index=True
    )


st.caption(
    "Blue points are near-live vehicle positions. "
    "Coloured points are the latest saved route-recovery locations. "
    "These are representative locations, not full route lines."
)
