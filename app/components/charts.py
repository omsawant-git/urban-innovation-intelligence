import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

def city_map_chart(df: pd.DataFrame, color_col: str, title: str):
    fig = px.scatter_geo(
        df, lat="latitude", lon="longitude",
        color=color_col, hover_name="city",
        size_max=20, projection="natural earth",
        title=title,
        color_continuous_scale="RdYlGn_r"
    )
    fig.update_layout(height=500, margin=dict(l=0, r=0, t=40, b=0))
    return fig

def line_chart(df: pd.DataFrame, x: str, y: str, color: str, title: str):
    fig = px.line(df, x=x, y=y, color=color, title=title, markers=True)
    fig.update_layout(height=400)
    return fig

def bar_chart(df: pd.DataFrame, x: str, y: str, color: str, title: str):
    fig = px.bar(df, x=x, y=y, color=color, title=title, barmode="group")
    fig.update_layout(height=400)
    return fig

def scatter_chart(df: pd.DataFrame, x: str, y: str, color: str, hover: str, title: str):
    fig = px.scatter(df, x=x, y=y, color=color, hover_name=hover, title=title, size_max=15)
    fig.update_layout(height=400)
    return fig

def radar_chart(categories: list, values: list, name: str):
    fig = go.Figure(go.Scatterpolar(
        r=values, theta=categories, fill="toself", name=name
    ))
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
        height=400
    )
    return fig

def forecast_chart(history_df, forecast_df, target: str, city: str):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=history_df["year"], y=history_df[target],
        name="Historical", line=dict(color="royalblue")
    ))
    fig.add_trace(go.Scatter(
        x=forecast_df["year"], y=forecast_df["forecast"],
        name="Forecast", line=dict(color="orange", dash="dash")
    ))
    fig.add_trace(go.Scatter(
        x=pd.concat([forecast_df["year"], forecast_df["year"][::-1]]),
        y=pd.concat([forecast_df["upper_bound"], forecast_df["lower_bound"][::-1]]),
        fill="toself", fillcolor="rgba(255,165,0,0.1)",
        line=dict(color="rgba(255,255,255,0)"),
        name="95% CI"
    ))
    fig.update_layout(
        title=f"{city} — {target.replace('_', ' ').title()} Forecast",
        xaxis_title="Year", yaxis_title=target,
        height=450
    )
    return fig