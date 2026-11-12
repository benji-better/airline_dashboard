import dash
from dash import Dash, html, dcc
import os


app = Dash(__name__, use_pages=True, suppress_callback_exceptions=True)

app.layout = html.Div([
    html.H1("Airline Cancellations Dashboard"),

    # Generate navigation links automatically from registered files
    html.Div([
        dcc.Link(f"{page['name'].replace("_", " ").title()}", href=page["relative_path"], style={"margin-right": "30px", "margin-left": "30px",  "font-size": "18px"})
        for page in dash.page_registry.values()
    ], style={"padding": "10px", "background-color": "#f8f9fa", "margin-bottom": "20px", "text-align": "center"}),

    dash.page_container
])

if __name__ == "__main__":
    app.run(debug=True)
