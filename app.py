# Import required libraries
import pathlib
import dash
from dash.dependencies import Input, Output, State, ClientsideFunction
import dash_core_components as dcc
import dash_html_components as html
import dash_helper
import dash_table
import pandas as pd
from algor import allocate
from Package import Package
from Truck import Truck
from Destination import Destination

# get relative data folder
PATH = pathlib.Path(__file__).parent
DATA_PATH = PATH.joinpath("data").resolve()

app = dash.Dash(
    __name__, meta_tags=[{"name": "viewport", "content": "width=device-width"}]
)
server = app.server

# Read in files.
PAGE_SIZE = 10
# File Dependancies for filtering
operators = [['ge ', '>='],
             ['le ', '<='],
             ['lt ', '<'],
             ['gt ', '>'],
             ['ne ', '!='],
             ['eq ', '='],
             ['contains '],
             ['datestartswith ']]

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
                            src=app.get_asset_url("cow.png"),
                            id="plotly-image",
                            style={
                                "height": "100px",
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
                                    "Delivery Tracker",
                                    style={"margin-bottom": "0px"},
                                ),

                            ]
                        )
                    ],
                    className="one-half column",
                    id="title",
                ),
                html.Div(
                    [

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
        html.Div(

            [

                html.Div(

                    [

                        dash_table.DataTable(
                            id='table-filtering',
                            page_current=0,
                            page_size=PAGE_SIZE,
                            page_action='custom',
                            filter_action='custom',
                            filter_query=''
                        )

                    ],

                    className='pretty_container twelve columns',

                ),

            ],

            className='row'

        ),
        html.Div(

            [

                html.Div(

                    [

                        html.P("Total Fuel Consumption"),

                        html.H6(

                            id="FuelText",

                            className="info_text"

                        )

                    ],

                    id="FuelConsumption",

                    className="pretty_container"

                ),

                html.Div(

                    [

                        html.P("Trips Taken"),

                        html.H6(

                            id="TripsText",

                            className="info_text"

                        )

                    ],

                    id="TripsTaken",

                    className="pretty_container"

                ),

                html.Div(

                    [

                        html.P("Total Distance Travelled"),

                        html.H6(

                            id="DistanceText",

                            className="info_text"

                        )

                    ],

                    id="Distance",

                    className="pretty_container"

                ),
                html.Div(

                    [

                        html.P("Extra Capacity"),

                        html.H6(

                            id="CapacityText",

                            className="info_text"

                        )

                    ],

                    id="Capacity",

                    className="pretty_container"

                ),
                html.Div(

                    [

                        html.P("Time Wasted"),

                        html.H6(

                            id="TimeText",

                            className="info_text"

                        )

                    ],

                    id="Time",

                    className="pretty_container"

                ),
                html.Div(

                    [

                        html.P("Arrival Time of Last Truck"),

                        html.H6(

                            id="ArrivalText",

                            className="info_text"

                        )

                    ],

                    id="Arrival",

                    className="pretty_container"

                ),
                html.Div(

                    [

                        html.P("Number of Expired Parcels"),

                        html.H6(

                            id="ExpiredText",

                            className="info_text"

                        )

                    ],

                    id="Expired",

                    className="pretty_container"

                ),

            ],

            id="tripleContainer",

        ),

    ],
    id="mainContainer",
    style={"display": "flex", "flex-direction": "column"},
)


def split_filter_part(filter_part):
    for operator_type in operators:
        for operator in operator_type:
            if operator in filter_part:
                name_part, value_part = filter_part.split(operator, 1)
                name = name_part[name_part.find('{') + 1: name_part.rfind('}')]

                value_part = value_part.strip()
                v0 = value_part[0]
                if (v0 == value_part[-1] and v0 in ("'", '"', '`')):
                    value = value_part[1: -1].replace('\\' + v0, v0)
                else:
                    try:
                        value = float(value_part)
                    except ValueError:
                        value = value_part

                # word operators need spaces after them in the filter string,
                # but we don't want these later
                return name, operator_type[0].strip(), value

    return [None] * 3


@app.callback(
    [Output('table-filtering', "data"),
     Output('table-filtering', "columns")],
    [Input('table-filtering', "page_current"),
     Input('table-filtering', "page_size"),
     Input('table-filtering', "filter_query"),
     Input("output-data-upload", "children")])
def update_table(page_current, page_size, filter, df_json_list):
    print(filter)
    if not df_json_list:
        return [], []
    df_list = dash_helper.read_json(df_json_list)
    filtering_expressions = filter.split(' && ')
    destination_df = df_list[0]
    parcel_df = df_list[1]
    truck_df = df_list[2]
    trucks, parcels, destinations = [], [], []
    for index, row in destination_df.iterrows():
        destinations.append(
            Destination(row['id'], row['name'], row['distance']))

    for index, row in parcel_df.iterrows():
        dest = 0
        for d in destinations:
            if row['destination'] == d.theid:
                dest = d
        parcels.append(
            Package(row['id'], row['arrival_time'], dest, row['expiry'], row['weight'], row['delicate'], row['cold']))

    for index, row in truck_df.iterrows():
        trucks.append(
            Truck(row['id'], row['distance'], row['speed'], row['capacity'], row['fuel_efficiency'], row['delicate'],
                  row['cold']))

    allocate(parcels, trucks)
    ids, ats, dels, refrigs, weights, expiry, destination_names = [], [], [], [], [], [], [],
    parcels = [p for p in parcels if p.destination != 0]
    for p in parcels:
        ids.append(p.theid)
        ats.append(p.arrivetime)
        dels.append(p.delicate)
        refrigs.append(p.refrig)
        weights.append(p.weight)
        expiry.append(p.expiry)
        destination_names.append(p.destination.name)
    dff = pd.DataFrame(list(zip(ids, ats, expiry, weights, dels, refrigs, destination_names)),
                       columns=['ID number', 'Arrival time', 'Expiry (hours from now)',
                                'Weight (kg) ', 'Delicate (Y/N)', 'Refrigerated (Y/N)', "Destination Name"])
    print(dff)

    for filter_part in filtering_expressions:
        col_name, operator, filter_value = split_filter_part(filter_part)

        if operator in ('eq', 'ne', 'lt', 'le', 'gt', 'ge'):
            # these operators match pandas series operator method names
            dff = dff.loc[getattr(dff[col_name], operator)(filter_value)]
        elif operator == 'contains':
            dff = dff.loc[dff[col_name].str.contains(filter_value)]
        elif operator == 'datestartswith':
            # this is a simplification of the front-end filtering logic,
            # only works with complete fields in standard format
            dff = dff.loc[dff[col_name].str.startswith(filter_value)]

    return dff.iloc[
           page_current * page_size:(page_current + 1) * page_size
           ].to_dict('records'), dash_helper.name_ID_form(dff.columns)


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


if __name__ == "__main__":
    app.run_server(debug=True)
