import plotly.express as px


def _write_figure_to_file(fig, path):
    fig.write_image(path)

def generate_stacked_bar_chart_png(df):
    #df = px.data.medals_long()

    fig = px.bar(df, x="user_name", y="hours", color="project_name", text="project_name")
    
    path = "bars.png"
    _write_figure_to_file(fig, path)

    return path
