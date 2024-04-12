from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd

def register_callbacks(app, melted_df):
    ### define function for plot 
    @app.callback(
        Output('emissions-time-series', 'figure'),
        [Input('country-dropdown', 'value'), Input('year-slider', 'value')]
    )

    def update_graph(selected_countries, selected_years):
        if not selected_countries or not selected_years:
            return px.line(title='Select countries and year range to see CO2 Emissions Over Time')
        
        df_filtered = melted_df[(melted_df['Country Name'].isin(selected_countries)) & 
                                (melted_df['Year'] >= selected_years[0]) & 
                                (melted_df['Year'] <= selected_years[1])]
        
        fig = px.line(df_filtered, x='Year', y='Emissions', color='Country Name',
                    title='CO2 Emissions Over Time for Selected Countries')
        
        return fig


    ## Bar Chart @ Jing
    @app.callback(
        Output('emissions-bar-chart', 'figure'),
        [Input('region-dropdown', 'value')]
    )

    def update_bar_chart(selected_regions):
        if not selected_regions:
            return px.bar(title='Choose any Region(s): <br>For CO2 Emissions Bar Chart')

        df_filtered_by_region = melted_df[melted_df['Region'].isin(selected_regions)]
        df_top_countries = df_filtered_by_region.groupby('Country Name').agg({'Emissions':'sum'}).nlargest(5, 'Emissions').reset_index()

        max_emissions_value = df_top_countries['Emissions'].max()
        y_axis_max = max_emissions_value * 1.2

        fig = px.bar(df_top_countries, x='Country Name', y='Emissions', text='Emissions',
                    title='Top 5 Countries\' Total CO2 Emissions<br>in Selected Region(s)')

        fig.update_traces(texttemplate='%{text:.2s}', textposition='outside')
        fig.update_xaxes(title_text='')
        fig.update_yaxes(range=[0, y_axis_max])

        return fig


    # Pie Chart @ Jo
    @app.callback(
        Output('emissions-pie-chart', 'figure'),
        [Input('region-dropdown', 'value')]
    )
    def update_pie_chart(selected_regions):
        if not selected_regions:
            return px.pie(title='Choose any Region(s): <br>For CO2 Emissions Pie Chart')

        df_filtered_by_region = melted_df[melted_df['Region'].isin(selected_regions)]
        df_countries = df_filtered_by_region.groupby('Country Name', as_index=False).agg({'Emissions':'sum'})
        
        df_top_countries = df_countries.sort_values('Emissions', ascending=False).head(5)
        if len(df_countries) > 5: 
            other_emissions = df_countries.sort_values('Emissions', ascending=False)[5:]['Emissions'].sum()
            other_row = pd.DataFrame(data={'Country Name': ['Others'], 'Emissions': [other_emissions]})
            df_display = pd.concat([df_top_countries, other_row], ignore_index=True)
        else:
            df_display = df_top_countries
        
        fig = px.pie(data_frame=df_display,
                    names='Country Name', 
                    values='Emissions',
                    hover_data={'Country Name': True, 'Emissions': ':.2f'}, 
                    hole=.2,
                    title='CO2 Emissions of the Selected Region(s): <br>Top 5 Countries and Others')
        
        fig.update_traces(hovertemplate='%{label}: <br>Percentage: %{percent} <br>CO2 Emission: %{value} MT/capita<br>', textposition='outside')

        return fig

    ## Map Chart @ Yili
    @app.callback(
        Output('emissions-map-chart', 'figure'),
        [Input('country-dropdown', 'value'), Input('year-slider', 'value'), Input('data-scope-check', 'value')]
    )

    def update_map(selected_countries, selected_years, scope):
        if 'ALL' in scope:
            df_filtered = melted_df[
                (melted_df['Year'] >= selected_years[0]) &
                (melted_df['Year'] <= selected_years[1])
            ]
        elif not selected_countries or not selected_years:
            
            return px.choropleth(title="Select countries and year range to see the map")
        else:
            df_filtered = melted_df[
                (melted_df['Country Name'].isin(selected_countries)) &
                (melted_df['Year'] >= selected_years[0]) &
                (melted_df['Year'] <= selected_years[1])
            ]
    
        # Calculate summary statistics for each country
        stats_by_country = df_filtered.groupby('Country Name').agg(
            Total_Emissions=pd.NamedAgg(column='Emissions', aggfunc='sum'),
            Average_Emissions=pd.NamedAgg(column='Emissions', aggfunc='mean'),
            Std_Emissions=pd.NamedAgg(column='Emissions', aggfunc='std'), 
            Max_Emissions=pd.NamedAgg(column='Emissions', aggfunc='max'),
            Min_Emissions=pd.NamedAgg(column='Emissions', aggfunc='min')
        ).reset_index()

        # Create the choropleth map
        fig = px.choropleth(
            stats_by_country,
            locations="Country Name",
            locationmode="country names",
            color="Total_Emissions",
            hover_name="Country Name",
            hover_data={
                'Total_Emissions': True,
                'Average_Emissions': ':.2f',
                'Std_Emissions': ':.2f',
                'Max_Emissions': ':.2f',
                'Min_Emissions': ':.2f'
            },
            color_continuous_scale=px.colors.qualitative.Dark24,
            title="CO2 Emissions by Country"
        )

        fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
        fig.update_geos(projection_type="natural earth")

        return fig
