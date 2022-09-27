import plotly.express as px


def _write_figure_to_file(fig, path):
    fig.write_image(path, width=700, height=500, scale=1.5)

def generate_stacked_bar_chart_png(df, title, path="bars.png"):
    fig = px.bar(df, x="user_name", y="hours", color="project_name", text="project_name")
    fig.update_layout(
    title=title,
    xaxis_title="",
    yaxis_title="Hours",
)

    _write_figure_to_file(fig, path)

    return path
