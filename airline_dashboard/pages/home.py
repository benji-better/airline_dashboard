import dash
from dash import html

dash.register_page(__name__, path='/', name='Home')

layout = html.Div([
    html.H1(
        "An Explanation of the Dashboard and Data!",
            style={"text-align": "center",
                   "padding": "10px",
                   "background-color": "#f8f9fa",
                   "margin-bottom": "20px"}),

    html.P(
        "The first dash page is a live chart showing a simulated real-time comparison of flight cancellations "
        "since the beginning of the day at midnight (EST) between our airline (Southwest) "
        "and our three largest competing airlines (America, Delta, & United)",
           style={"margin-left": "2rem",
                  "margin-right": "2rem",
                  "font-size": "1.25rem"}),

    html.P(
        "The second dash page is a simulated live map showing our airline's cancellations at our airports within the US, "
        "since the beginning of the day at midnight (EST). When an airport has more cancellations, the dot above the airport grows larger",
           style={"margin-left": "2rem",
                  "margin-right": "2rem",
                  "font-size": "1.25rem"}),

    html.P(
        "This Dashboard shows simulated live data specifically from 12AM EST of the "
           "27th of December, 2022 until 11:50 PM EST of the same day with updates happening every ten minutes."
           "The data used in this dashboard comes from a Department of Transportation dataset of all domestic commercial flights from 2019 until August 2023."
           " The dataset is available here: kaggle.com/datasets/patrickzel/flight-delay-and-cancellation-dataset-2019-2023/",
           style={"margin-left": "2rem",
                  "margin-right": "2rem",
                  "font-size": "1.25rem"})
])