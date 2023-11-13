import plotly.express as px
import plotly.figure_factory as ff
from datetime import datetime

TEMPLATE = "plotly_dark"


def _write_figure_to_file(fig, path):
    fig.write_image(path, width=700, height=500, scale=1.5)


def generate_stacked_bar_chart_png(df, title, project_color_sequence, path="bars.png"):
    # Sort the df for most ETH hours (Hours > 0)
    eth_hours = df[df.hours > 0].groupby("user_name")["hours"].sum()
    df["total_eth_hours"] = df.apply(
        axis="columns", func=lambda x: eth_hours.get(x.user_name, 0)
    )
    sorted_user_arr = (
        df.groupby("user_name")
        .first()
        .sort_values("total_eth_hours", ascending=False)
        .index.values.tolist()
    )  # .loc[:,"user_name"]

    fig = px.bar(
        df,
        x="user_name",
        y="hours",
        color="project_name",
        text="project_name",
        color_discrete_sequence=project_color_sequence,
        template=TEMPLATE,
    )
    fig.update_layout(
        title=f"{title} - Generated: {datetime.now().strftime('%d.%m.%Y %H:%M')}",
        barmode="relative",
        xaxis_title="",
        yaxis_title="Hours",
        legend_title="Projects",
        xaxis={"categoryorder": "array", "categoryarray": sorted_user_arr},
    )

    max_hours = max(6, df[df.hours > 0].groupby("user_name")["hours"].sum().max() + 1)
    min_hours = min(0, df[df.hours < 0].groupby("user_name")["hours"].sum().min() - 1)
    fig.update_yaxes(range=[min_hours, max_hours])

    _write_figure_to_file(fig, path)

    return path


def generate_schedule_chart_png(df, title, project_color_sequence, path="schedule.png"):
    fig = px.timeline(
        df,
        y="user_name",
        x_start="start",
        x_end="end",
        color="project_name",
        color_discrete_sequence=project_color_sequence,
        template=TEMPLATE,
    )

    fig.update_layout(
        title=f"{title} - Generated: {datetime.now().strftime('%d.%m.%Y %H:%M')}",
        xaxis_title="",
        yaxis_title="",
        legend_title="Projects",
        showlegend=False,
    )

    _write_figure_to_file(fig, path)

    return path
