# Import required libraries
import pandas as pd
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
# filtered_df is only successful landings.

max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(
    children=[html.H1('SpaceX Launch Records Dashboard',
                  style={'textAlign': 'center', 'color': '#503D36',
                  'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                  dcc.Dropdown(id='site-dropdown', options=[
                                  {'label':'All', 'value':'All Sites'},
                                  {'label':'CCAFS LC-40', 'value':'CCAFS LC-40'},
                                  {'label':'VAFB SLC-4E', 'value':'VAFB SLC-4E'},
                                  {'label':'KSC LC-39A', 'value':'KSC LC-39A'},
                                  {'label':'CCAFS SLC-40', 'value':'CCAFS SLC-40'}],
                                  placeholder='Please Select A Launch Site',
                                  searchable=True
                                  ),
                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                dcc.RangeSlider(id='payload-slider',
                                                min=0,
                                                max=10000,
                                                step=1000,
                                                value=[min_payload, max_payload]),

                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    [Input(component_id='site-dropdown', component_property='value')]
)
def get_pie_chart(selected_site):
    def create_placeholder_pie_chart(message):
        """Creates a placeholder pie chart with a given message."""
        return px.pie(
            names=[message],
            values=[1],
            title=message
        )

    def create_site_pie_chart(site):
        """Creates a success vs failure pie chart for a specific site."""
        launch_site_data = spacex_df[spacex_df['Launch Site'] == site]
        print(launch_site_data)
        if launch_site_data.empty:
            return create_placeholder_pie_chart(f"No data available for {site}")

        success_count = launch_site_data[launch_site_data['class'] == 1].shape[0]
        print(success_count)
        failure_count = launch_site_data[launch_site_data['class'] == 0].shape[0]
        print(failure_count)
        return px.pie(
            names=['Success', 'Failure'],
            values=[success_count, failure_count],
            color=['Success', 'Failure'],
            color_discrete_map={'Success': 'red', 'Failure': 'blue'},
            title=f"Total Success Launches for {site}"
        )

    def create_overall_pie_chart():
        """Creates a pie chart showing success percentages across all sites."""
        successful_launches = spacex_df[spacex_df['class'] == 1]
        site_success_counts = successful_launches.groupby('Launch Site').size().reset_index(name='count')
        return px.pie(
            site_success_counts,
            names='Launch Site',
            values='count',
            title="Percentage of Successful Launches by Launch Site"
        )

    # Main logic
    if not selected_site:
        return create_placeholder_pie_chart("Please select a launch site from the dropdown menu")

    if selected_site == 'All Sites':
        return create_overall_pie_chart()

    return create_site_pie_chart(selected_site)
#       title='no go'
# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [Input(component_id='site-dropdown', component_property='value'), Input(component_id='payload-slider', component_property='value')]
)
def get_scatter_chart(selected_site, payload_range):
    def create_placeholder_scatter_chart(message):
        """Creates a placeholder scatter chart with a given message."""
        return px.scatter(
            x=[message],
            y=[message],
            title=message
        )
    def create_site_scatter_chart(site, payload_range):
        fig = px.scatter(
            spacex_df[spacex_df['Launch Site'] == site],
            x="Payload Mass (kg)",
            y="class",
            color="Booster Version Category",
            # color_discrete_map={1:"green", 0:"red"},
            title=f"Payload vs. Success for {site}"
        )
        fig.update_xaxes(range=payload_range)
        return fig
    def create_overall_scatter_chart(payload_range):
        fig = px.scatter(
            spacex_df,
            x="Payload Mass (kg)",
            y="class",
            color="Booster Version Category",
            # color_discrete_map={1:"green", 0:"red"},
            title="Payload vs. Success for All Sites"
        )
        fig.update_xaxes(range=payload_range)
        return fig

    if not selected_site:
        return create_placeholder_scatter_chart("Please select a launch site from the dropdown menu")
    if selected_site == 'All Sites':
        return create_overall_scatter_chart(payload_range)
    return create_site_scatter_chart(selected_site, payload_range)



# Run the app
if __name__ == '__main__':
    app.run_server()
