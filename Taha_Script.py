# -*- coding: utf-8 -*-
"""
Created on Fri Nov 22 08:50:31 2019

@author: Pedro
"""

def import_tdms(file_directory, group_name):
    import pandas as pd
    from nptdms import TdmsFile

    df = pd.DataFrame()
    channels = ["X", "Y", "Z", "Force (from DC)", "Force (from RMS)"]

    for chl in channels:
        df[chl] = TdmsFile(file_directory).object(group_name, chl).data

    df["Z0"]= 0
    df["Y0"]=min(df.Y) - 1

    return df

# =========== View Section =================
import base64
import io
import pandas as pd

import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html

app = dash.Dash(__name__)

app.layout = html.Div(

style={
    "backgroundColor":"rgb(240,240,240)",
    "width":"100%",
    "height": "97vh",
    "display":"flex",
    "alignItems":"center",
    "justifyContent":"center",
},

children=[
    html.Div(
        style={
            "height":"100%",
            "width":"40%",
            "display":"flex",
            "alignItems":"center",
            "justifyContent":"center",

        },
        children = [
        html.Div([
            dcc.Upload(
                id='upload-data',
                children= html.Div(['Drag and Drop or ', html.A('Select Files')]),
                style={
                'borderWidth': '1px',
                'borderStyle': 'dashed',
                'borderRadius': '5px',
                'textAlign': 'center',
                'margin': '10px',
                "height": "60%"},
            ),

            html.Div(
                id='output-data-upload',
                children= html.Div(id="hidden-div", style={"display":"none"})
                ),

            dcc.Dropdown(
                id="graph-dropdown",
                options=[
                    {'label': '3-D Graph', 'value': '1'},
                    {'label': "X-Y Projection", 'value': '2'},
                    {'label': 'X-Z Projection', 'value': '3'}
                ],
                value=["1","2"],
                multi=True),

            html.Div(
                id="options-div",
                style = {
                    "display" : "flex",
                    "justifyContent" : "space-around",
                },
                children = [
                    dcc.RadioItems(
                        id = "Unit Selection",
                        style = {"background":"white", "width": "40%",
                        "display":"flex", "justifyContent":"space-around",
                        "borderRadius":"15px"},
                        options = [
                            {"label":"English Units", "value": 0},
                            {"label": "Metric Units", "value": 1}],
                        value = 0,
                        labelStyle={"display":"inline-block"}
                    ),

                    html.Div(
                        style = {"display" : "flex", "justifyContent" : "center",},
                        children = ["Force Threshold:",

                        dcc.Input(
                            id = "Threshold Input",
                            style = {"width": "15%", "marginLeft":"5px",
                            "display":"flex", "justifyContent":"center"},
                            type = "number",
                            step = 0.01,
                            value = 0.00,
                        )]
                    )]
            ),

            dash_table.DataTable(
                id='table',
                style_cell={
                        'minWidth': '0px', 'maxWidth': '180px',
                    },
                columns=[
                {"name":"Coverage", "id":"coverage"},
                {"name":"Average Force", "id":"Avg Force"},
                {"name":"Max Force", "id":"M Force"},
                {"name":"Total Force", "id":"T Force"}],
            ),

            dcc.Graph(
                id='second-graph',
                style={
                    "position":"relative",
                    "width":"100%",
                    "height":"78%",
                    "bottom":"0",
                },
            ),
            ],

            style={
                "height":"90%",
                "width":"90%",
                'borderWidth': '1px',
                'borderStyle': 'solid',
                'borderRadius': '5px',
                "overflow":"auto",
            }
            ),
        ],

    ),

    html.Div([
        dcc.Graph(
            id='example-graph',
            style={
                "width":"95%",
                "height":"95%",
            })],

        style={
            "height":"100%",
            "width":"55%",
            "display":"flex",
            "justifyContent": "center",
            "alignItems":"center",
        },
        id="main-graph-div"
    )])

# =========== Callback Section =================
from dash.dependencies import Input, Output, State

@app.callback(
    Output(component_id='example-graph', component_property='figure'),
    [Input(component_id='graph-dropdown', component_property='value'),
    Input("hidden-div", "children"),
    Input('Unit Selection', "value"),
    Input("Threshold Input", "value"),]
)

def create_trace(values, data, unit_type, threshold):
        try:
            df = pd.read_json(data)
            trace = []

            if unit_type == 0:
                df["Force (from RMS)"]=df["Force (from RMS)"].apply(lambda x: x*0.224809)
                df.X = df.X.apply(lambda x: x* 0.03937)
                df.Y = df.Y.apply(lambda x: x* 0.03937)

            df["Force (from RMS)"] [df["Force (from RMS)"] <= threshold]=0

            if "1" in values:
                trace.append(
                {
                'x': df.X, 'y': df.Y, "z": df["Force (from RMS)"],
                "colorscale":"Portland", "intensity": df["Force (from RMS)"],
                'type': 'mesh3d', 'name': '3D Plot'},
                )

            if "2" in values:
                trace.append(
                {
                'x': df.X, 'y': df.Y, "z": df["Z0"],
                "colorscale":"Portland", "intensity": df["Force (from RMS)"],
                'type': 'mesh3d', 'name': '3D Plot'}
                )

            if "3" in values:
                trace.append(
                {
                'x': df.X, 'y': df["Y0"], "z": df["Force (from RMS)"],
                "colorscale":"Portland", "intensity": df["Force (from RMS)"],
                'type': 'mesh3d', 'name': '3D Plot'},
                )

            return {
                "data":trace,
                "layout":{
                    "paper_bgcolor":"transparent",
                    "scene": {
                        "aspectmode":"manual",
                        "aspectratio":{"x":15, "y":1, "z":5},
                        "yaxis":{"nticks":5, "title":"Y-axis (mm)"},
                        "xaxis":{"title":"X-axis (mm)"},
                        "zaxis":{"title":"Impact Force (N)"},
                        "camera":{
                            "center":{"x":2, "y":0, "z":0},
                            "eye": {"x":10, "y":10, "z":3},
                        }
                        },
                }
                }

        except:
             return {
             "data":[],
             "layout":{
                    'paper_bgcolor': "transparent",
                    "plot_bgcolor":'rgba(0,0,0,0)'
                    }
            }


@app.callback(Output('hidden-div', 'children'),
              [Input('upload-data', 'contents')],
              [State('upload-data', 'filename'),
               State('upload-data', 'last_modified')])

def update_output(list_of_contents, list_of_names, list_of_dates):
    if list_of_contents is not None:
        return parse_contents(list_of_contents, list_of_names, list_of_dates)

def parse_contents(contents, filename, date):
    content_type, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)

    if 'tdms' in filename:
        # Assume that the user uploaded a CSV file
        df = import_tdms("tdms/" + filename, "Readings").to_json(orient="columns")
        return df


@app.callback(Output("table", "data"),
            [Input("hidden-div", "children"),
            Input("Threshold Input", "value"),
            Input('Unit Selection', "value"),])

def make_table_data(jsonified_input, threshold, unit_type):

    xcoverage=[]
    ycoverage=[]
    force=[]
    counter= 0
    cfactor = 1

    try:
        df = pd.read_json(jsonified_input)

        if unit_type == 0:
            cfactor = 0.03937
            df["Force (from RMS)"]=df["Force (from RMS)"].apply(lambda x: x*0.224809)

        for n in df["Force (from RMS)"]:
            if n > threshold:
                xcoverage.append(df.X[counter])
                force.append(n)
                ycoverage.append(df.Y[counter])
            counter = counter+1

        xcoverage = round((max(xcoverage) - min(xcoverage))*cfactor, 2)
        ycoverage = round((max(ycoverage) - min(ycoverage))*cfactor, 2)
        force = round(sum(force),2)
        Fmax = round(max(df["Force (from RMS)"]),2)
        avg = round((force/(xcoverage*ycoverage)),2)

        if unit_type == 0:
            return [{"coverage":str(xcoverage) + " in X " + str(ycoverage) + " in",
                "Avg Force": str(avg) + " psi", "M Force": str(Fmax) + " lbf",
                "T Force":str(force) + " lbf"}]

        else:
            return [{"coverage":str(xcoverage) + " mm X " + str(ycoverage) + " mm",
                "Avg Force": str(avg) + " N/mm^2", "M Force": str(Fmax) + " N",
                "T Force":str(force) + " N"}]

    except:
        return [{"coverage":"N/A", "Avg Force": "N/A",
         "M Force":"N/A", "T Force":"N/A"}]


@app.callback(Output("second-graph", "figure"),
            [Input("hidden-div", "children"),
            Input('Unit Selection', "value"),
            Input("Threshold Input", "value"),])

def make_second_graph(jsonified_input, unit_type, threshold):
    try:
        df = pd.read_json(jsonified_input)
        counter=0
        data=[]

        if unit_type == 0:
            df["Force (from RMS)"]=df["Force (from RMS)"].apply(lambda x: x*0.224809)
            df.X = df.X.apply(lambda x: x* 0.0394)
            df.Y = df.Y.apply(lambda x: x* 0.0394)

        df["Force (from RMS)"] [df["Force (from RMS)"] <= threshold]=0

        return {
            "layout":{
                'paper_bgcolor': "transparent",
                "plot_bgcolor":'rgba(0,0,0,0)',
                "yaxis":{
                    "scaleanchor":"x",
                    "scaleratio":"1",
                    },},

            "data":[{
                'x': df.X, 'y': df.Y, "z": df["Force (from RMS)"],
                "colorscale":"Portland", "intensity": df["Force (from RMS)"],
                'type': 'heatmap',
                'name': '2D Plot',
                "visible": "false",
                "connectgaps":"true",
                "zsmooth":"best",
                "contours": {
                    "coloring": 'fill',
                    "showlines": "false",
                    },
            }]
        }

    except:
        return {
            "layout":{
                'paper_bgcolor': "transparent",
                },}

if __name__ == '__main__':
    app.run_server(debug=True)
