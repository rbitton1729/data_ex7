import altair as alt
import pandas as pd

def base_theme():
    return {
        "config": {
            "view": {"stroke": None},
            "axis": {"labelFontSize": 12, "titleFontSize": 14},
            "legend": {"labelFontSize": 12, "titleFontSize": 14},
        }
    }

def chart_hook_temp_over_time(df: pd.DataFrame) -> alt.Chart:
    return (
        alt.Chart(df)
        .mark_line()
        .encode(
            x=alt.X("date:T", title="Date"),
            y=alt.Y("temp_max:Q", title="Daily max temp (°C)"),
            tooltip=[alt.Tooltip("date:T"), alt.Tooltip("temp_max:Q", format=".1f")],
        )
        .properties(height=320)
    )

def chart_context_seasonality(df: pd.DataFrame) -> alt.Chart:
    month_order = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
    return (
        alt.Chart(df)
        .mark_boxplot()
        .encode(
            x=alt.X("month_name:N", title="Month", sort=month_order),
            y=alt.Y("temp_max:Q", title="Daily max temp (°C)"),
        )
        .properties(height=320)
    )

def chart_surprise_extremes(df: pd.DataFrame) -> alt.Chart:
    q = float(df["temp_max"].quantile(0.99))
    df2 = df.copy()
    df2["extreme"] = df2["temp_max"] >= q

    base = (
        alt.Chart(df2)
        .mark_point(filled=True, size=35)
        .encode(
            x=alt.X("date:T", title="Date"),
            y=alt.Y("temp_max:Q", title="Daily max temp (°C)"),
            color=alt.condition("datum.extreme", alt.value("red"), alt.value("lightgray")),
            tooltip=[alt.Tooltip("date:T"), alt.Tooltip("temp_max:Q", format=".1f")],
        )
        .properties(height=320)
    )

    rule = alt.Chart(pd.DataFrame({"q": [q]})).mark_rule(strokeDash=[6, 4]).encode(y="q:Q")
    return base + rule

def chart_explain_precip_vs_temp(df: pd.DataFrame) -> alt.Chart:
    return (
        alt.Chart(df)
        .mark_point(opacity=0.45)
        .encode(
            x=alt.X("precipitation:Q", title="Precipitation (in)"),
            y=alt.Y("temp_max:Q", title="Daily max temp (°C)"),
            tooltip=[
                "date:T",
                alt.Tooltip("precipitation:Q", format=".2f"),
                alt.Tooltip("temp_max:Q", format=".1f"),
            ],
        )
        .properties(height=320)
    )

def chart_dashboard(df: pd.DataFrame) -> alt.Chart:
    weather_types = sorted(df["weather"].unique())

    w_select = alt.selection_point(
        fields=["weather"],
        bind=alt.binding_select(options=weather_types, name="Weather: "),
    )
    brush = alt.selection_interval(encodings=["x"], name="Time window")

    line = (
        alt.Chart(df)
        .mark_line()
        .encode(
            x=alt.X("date:T", title="Date"),
            y=alt.Y("temp_max:Q", title="Daily max temp (°C)"),
            color=alt.Color("weather:N", title="Weather"),
            tooltip=["date:T", "weather:N", alt.Tooltip("temp_max:Q", format=".1f")],
        )
        .add_params(w_select, brush)
        .transform_filter(w_select)
        .properties(height=260)
    )

    hist = (
        alt.Chart(df)
        .mark_bar()
        .encode(
            x=alt.X("temp_max:Q", bin=alt.Bin(maxbins=30), title="Daily max temp (°C)"),
            y=alt.Y("count():Q", title="Days"),
            tooltip=[alt.Tooltip("count():Q", title="Days")],
        )
        .transform_filter(w_select)
        .transform_filter(brush)
        .properties(height=260)
    )

    return alt.vconcat(line, hist).resolve_scale(color="independent")

def chart_new_static_avg_precip_by_month(df: pd.DataFrame) -> alt.Chart:
    month_order = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    return (
        alt.Chart(df)
        .mark_bar()
        .encode(
            x=alt.X("month_name:N", title="Month", sort=month_order),
            y=alt.Y("mean(precipitation):Q", title="Average daily precipitation (in)"),
            tooltip=[
                alt.Tooltip("month_name:N", title="Month"),
                alt.Tooltip("mean(precipitation):Q", title="Avg precipitation", format=".2f"),
            ],
        )
        .properties(height=320)
    )

def chart_new_interactive_temp_minmax(df: pd.DataFrame) -> alt.Chart:
    weather_options = ["all"] + sorted(df["weather"].unique().tolist())
    weather_filter = alt.param(
        name="weather_filter",
        bind=alt.binding_select(options=weather_options, name="Weather type: "),
        value="all",
    )
    brush = alt.selection_interval(encodings=["x", "y"], name="Range")

    scatter = (
        alt.Chart(df)
        .transform_filter("weather_filter == 'all' || datum.weather == weather_filter")
        .mark_circle(size=48, opacity=0.55)
        .encode(
            x=alt.X("temp_min:Q", title="Daily min temp (°C)"),
            y=alt.Y("temp_max:Q", title="Daily max temp (°C)"),
            color=alt.Color("weather:N", title="Weather"),
            tooltip=[
                alt.Tooltip("date:T"),
                alt.Tooltip("weather:N"),
                alt.Tooltip("temp_min:Q", format=".1f"),
                alt.Tooltip("temp_max:Q", format=".1f"),
            ],
        )
        .add_params(weather_filter, brush)
        .properties(height=280)
    )

    summary = (
        alt.Chart(df)
        .transform_filter("weather_filter == 'all' || datum.weather == weather_filter")
        .transform_filter(brush)
        .transform_calculate(temp_range="datum.temp_max - datum.temp_min")
        .mark_bar()
        .encode(
            x=alt.X("temp_range:Q", bin=alt.Bin(maxbins=24), title="Daily temperature range (°C)"),
            y=alt.Y("count():Q", title="Days in selected scatter region"),
            tooltip=[alt.Tooltip("count():Q", title="Days")],
        )
        .properties(height=220)
    )

    return alt.vconcat(scatter, summary)
