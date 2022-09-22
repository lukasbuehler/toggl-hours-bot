import plotly.express as px


def _write_figure_to_file(fig):
    print("Writing image to file")
    fig.write_image("test.png")

def generate_stacked_bar_chart_png(df):
    #df = px.data.medals_long()

    print(df)

    fig = px.bar(df, x="user_name", y="hours", color="project_name", text="project_name")
    _write_figure_to_file(fig)
