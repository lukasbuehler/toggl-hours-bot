import plotly.express as px
from datetime import datetime


def _write_figure_to_file(fig, path):
    fig.write_image(path, width=700, height=500, scale=1.5)

def generate_stacked_bar_chart_png(df, title, project_color_sequence, path="bars.png"):
    fig = px.bar(df, x="user_name", y="hours", color="project_name", text="project_name", color_discrete_sequence=project_color_sequence)
    fig.update_layout(
    title=f"{title} - Generated: {datetime.now().strftime('%d.%m.%Y %H:%M')}",
    barmode='relative',
    xaxis_title="",
    yaxis_title="Hours",
    legend_title="Projects",
    xaxis={'categoryorder':'total descending'}
    )

    max_hours = max(6, df[df.hours > 0].groupby("user_name")["hours"].sum().max() + 1)
    min_hours = min(0, df[df.hours < 0].groupby("user_name")["hours"].sum().min() - 1)
    fig.update_yaxes(range=[min_hours, max_hours])

    _write_figure_to_file(fig, path)

    return path
