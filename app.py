# Import required libraries
import pickle
import pathlib
import dash
import datetime as dt
import pandas as pd
from dash.dependencies import Input, Output, State, ClientsideFunction
import dash_core_components as dcc
import dash_html_components as html
import dash_helper
import itertools

# get relative data folder
PATH = pathlib.Path(__file__).parent
DATA_PATH = PATH.joinpath("data").resolve()

app = dash.Dash(
    __name__, meta_tags=[{"name": "viewport", "content": "width=device-width"}]
)
server = app.server

layout = dict(
    autosize=True,
    automargin=True,
    margin=dict(l=30, r=30, b=20, t=40),
    hovermode="closest",
    plot_bgcolor="#F9F9F9",
    paper_bgcolor="#F9F9F9",
    legend=dict(font=dict(size=10), orientation="h"),
    title="Satellite Overview",
)

# Create app layout


app.layout = html.Div(
    [
        dcc.Store(id="aggregate_data"),
        # empty Div to trigger javascript file for graph resizing
        html.Div(id="output-clientside"),
        html.Div(
            id="output-data-upload",
            style={"display": "none"}
        ),
        html.Div(
            [
                html.Div(
                    [
                        html.Img(
                            src=app.get_asset_url("dash-logo.png"),
                            id="plotly-image",
                            style={
                                "height": "60px",
                                "width": "auto",
                                "margin-bottom": "25px",
                            },
                        )
                    ],
                    className="one-third column",
                ),
                html.Div(
                    [
                        html.Div(
                            [
                                html.H3(
                                    "New York Oil and Gas",
                                    style={"margin-bottom": "0px"},
                                ),
                                html.H5(
                                    "Production Overview", style={"margin-top": "0px"}
                                ),
                            ]
                        )
                    ],
                    className="one-half column",
                    id="title",
                ),
                html.Div(
                    [
                        html.A(
                            html.Button("Learn More", id="learn-more-button"),
                            href="https://plot.ly/dash/pricing/",
                        )
                    ],
                    className="one-third column",
                    id="button",
                ),
                html.Div(
                    [
                        dcc.Upload(
                            id="upload-data",
                            multiple=True,
                            children=html.Button(
                                "Upload CSVs")
                        ),
                    ],
                ),
            ],
            id="header",
            className="row flex-display",
            style={"margin-bottom": "25px"},
        ),
    ],
    id="mainContainer",
    style={"display": "flex", "flex-direction": "column"},
)

@app.callback(
        Output("output-data-upload", "children"),
        [Input("upload-data", "contents"),
         Input("upload-data", "filename")],
        [State("output-data-upload", "children")],
    )
def upload(contents, filenames, list_of_ds):
    """ Handles upload and creation of CSVs"""
    # Dash elements default to None but returning None will break callbacks
    if list_of_ds is None:
        list_of_ds = []
    # Check that contents has content
    if contents is None:
        return list_of_ds
    # Check that there is no duplicates in the filenames of the upload
    if dash_helper.duplicate_filename_check(filenames):
        return list_of_ds

    children = [dash_helper.parse_contents(c, f) for c, f in zip(contents, filenames)]


    children, filenames = dash_helper.remove_bad_files(children, filenames)
    filenames = dash_helper.remove_file_extension(filenames)
    if not children:
        return list_of_ds
    if list_of_ds is not None:
        children = list_of_ds + children
    return children


# Main
if __name__ == "__main__":
    app.run_server(debug=True)
