import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import numpy as np
from dash.dependencies import Output, Input

import plotly.express as px

data = pd.read_csv("https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/latest/owid-covid-latest.csv")
# data = data.query("location == 'India'")
# data["Date"] = pd.to_datetime(data["Date"], format="%Y-%m-%d")
data.sort_values("location", inplace=True)

values = {"total_cases": 0, "total_cases_per_million": 0}
data = data.dropna(subset=['continent'])
data = data.fillna(value=values)

fig = px.scatter_geo(data, 
                    locations="iso_code", 
                     color="continent",
                     hover_name="location", 
                     size="total_cases",
                     projection="natural earth"
                     )

external_stylesheets = [
    {
        "href": "https://fonts.googleapis.com/css2?"
                "family=Lato:wght@400;700&display=swap",
        "rel": "stylesheet",
    },
    {
        "href": "./assets/style.css",
        "rel": "stylesheet",
    }
]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.title = "Covid - data vizualisation"

app.layout = html.Div(
    children=[
        html.Div(
            children=[
                html.H1(
                children="COVID data visualization",
                className="header-title",
                ),
                html.P(
                    children="Data Source: Data on COVID-19 (coronavirus) by Our World in Data, total number of cases in the world is {total}, and death cases reported is {death}, as per the data updated on {date}.".format(total=str(int(data.total_cases.sum())), death=str(int(data.total_deaths.sum())), date=str(data.last_updated_date[0])),
                    className="header-description",
                ),
                html.A(
                    children="Get the data here",
                    href="https://github.com/owid/covid-19-data/tree/master/public/data",
                    target="_blank",
                    className="header-a",
                )
                ],
            className="header"
        ),
        html.Div(
            children=[
                html.Div(
                    children=dcc.Graph(
                        config={"displayModeBar": False},
                        figure=fig
                    ),
                    className="card"
                ),
            ],
        ),
        html.Div(
            children=[
                html.Div(
                    children=[
                        html.Div(children="Continent", 
                        className="menu-title"
                        ),
                        dcc.Dropdown(
                            id="region-filter",
                            options=[
                                {"label": region, "value": region}
                                for region in np.sort(data.continent.unique())
                            ],
                            value="Asia",
                            clearable=False,
                            className="dropdown",
                        ),
                    ]
                ),
                html.Div(
                    children=[
                        html.Div(
                            children="Total Cases",
                            className="slider",
                            ),
                        dcc.RangeSlider(
                            id="case-filter",
                            count=1,
                            min=data.total_cases.min(),
                            max=data.total_cases.max(),
                            step=10000,
                            value=[data.total_cases.min(), data.total_cases.max()]
                        )
                    ]
                ),
            ],
            className="menu",
        ),
        html.Div(
            children=[
                html.Div(
                    children=dcc.Graph(
                        id="total-cases",
                        config={"displayModeBar": False},
                    ),
                    className="card2"
                ),
                html.Div(
                    children=dcc.Graph(
                        figure={
                            "data": [
                                {
                                    "x": data["location"],
                                    "y": data["new_cases"],
                                    "type": "line",
                                    "hovertemplate": "New cases: %{y}"
                                                "<extra></extra>",
                                },
                            ],
                            "layout": {
                                "title": {
                                    "text": "New cases reported",
                                    "x": 0.05,
                                    "xanchor": "left",
                                },
                                "xaxis": {"fixedrange": True},
                                "yaxis": {
                                    "fixedrange": True,
                                },
                                "colorway": ["#17B897"],
                            },
                        },
                        id="new-cases",
                        config={"displayModeBar": False},
                    ),
                    className="card3"
                ),
            ] 
        ),

    ]
)

@app.callback(
    [Output("total-cases", "figure"), Output("new-cases", "figure")],
    [
        Input("region-filter", "value"),
        Input("case-filter", "value"),
    ],
)
def update_charts(region, value):
    mask = (
        (data.continent == region)
        & (data.total_cases >= value[0])
        & (data.total_cases <= value[1])
    )
    filtered_data = data.loc[mask, :]
    total_cases_figure = {
                            "data": [
                                {
                                    "x": filtered_data["location"],
                                    "y": filtered_data["total_cases"],
                                    "type": "line",
                                    "hovertemplate": "Total cases: %{y}"
                                                "<extra></extra>",
                                },
                            ],
                            "layout": {
                                "title": {
                                    "text": "total cases",
                                    "x": 0.05,
                                    "xanchor": "left",
                                },
                                "xaxis": {"fixedrange": True},
                                "yaxis": {
                                    "fixedrange": True,
                                },
                                "colorway": ["#17B897"],
                            },
                        }

    new_cases_figure = {
                            "data": [
                                {
                                    "x": filtered_data["location"],
                                    "y": filtered_data["new_cases"],
                                    "type": "line",
                                    "hovertemplate": "New cases: %{y}"
                                                "<extra></extra>",
                                },
                            ],
                            "layout": {
                                "title": {
                                    "text": "New cases reported",
                                    "x": 0.05,
                                    "xanchor": "left",
                                },
                                "xaxis": {"fixedrange": True},
                                "yaxis": {
                                    "fixedrange": True,
                                },
                                "colorway": ["#17B897"],
                            },
                        }
    return total_cases_figure, new_cases_figure

if __name__ == "__main__":
    app.run_server(debug=True)