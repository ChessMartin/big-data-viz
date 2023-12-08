import pandas as pd
import pandas as pd
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt
import plotly.express as px
from dash.dash_table.Format import Group
from dash import Dash, html, dcc, callback, Output, Input
import plotly.graph_objs as go
import seaborn as sns
import viz_query
import viz_database

app = Dash('__name__')

#set dropdown options
weekly_top10_artists = viz_query.find_weeklytop10('artist')
weekly_top10_albums = viz_query.find_weeklytop10('album')
weekly_top10_tracks = viz_query.find_weeklytop10('track')
weekly_top10_listeners = viz_query.find_weeklytop10('listener')

week_options = [{'label': str(week), 'value': str(week)} for week in weekly_top10_artists['week'].unique()]


Ranktrack10 = viz_query.find_alltime("track",10)
Rankalbum10 = viz_query.find_alltime("album",10)
Rankartist10 = viz_query.find_alltime("artist",10)
Ranklistener10 = viz_query.find_alltime("listener",10)
most_listened_artist = viz_query.find_alltime("artist",1).iloc[0, 0]
most_listened_track = viz_query.find_alltime("track",1).iloc[0, 0]
# we found that the most listened album is None. So I choose the second factor.[1,0]
most_listened_album = viz_query.find_alltime("album",2).iloc[1, 0]
most_listened_listener = viz_query.find_alltime("listener",1).iloc[0, 0]
# webbrowser.open_new('http://127.0.0.1:8050/')


Rankartistfig=px.bar(Rankartist10[::-1], x='count', y='artist', orientation='h',title='Top 10 Artist of all time',text='count',template='seaborn')
Rankalbumfig=px.bar(Rankalbum10[::-1], x='count', y='album', orientation='h',title='Top 10 Album of all time',text='count',template='seaborn')
Ranktrackfig=px.bar(Ranktrack10[::-1], x='count', y='track', orientation='h',title='Top 10 Track of all time',text='count',template='seaborn')
Ranklistenerfig=px.bar(Ranklistener10[::-1], x='count', y='listener', orientation='h',title='Top 10 Listener of all time',text='count',template='seaborn')

#crosstab artist-listener
cross_tab = viz_query.Cross_Tabulation('listener','artist')
listener_artist = cross_tab.sort_values(by='count', ascending=False).head(50)
listener_artist_table = listener_artist.pivot_table(index='listener', columns='artist', values='count',fill_value=0)
bubble_df = listener_artist_table.reset_index().melt(id_vars='listener', var_name='artist', value_name='count')
bubblefig = px.scatter(bubble_df, x='artist', y='listener', size='count', color='count',
                 labels={'count': 'Track Count'},
                 title='Bubble Plot of Listener-Artist TrackCount')

#fourth graph
artist_year = viz_query.year_count("artist")
total_track = artist_year.groupby(['year']).size().reset_index(name='count')
yearly_track = artist_year

app.layout = html.Div([

    html.H1(children='Playlist KPI Dashboard',
            style={'textAlign':'center', 'backgroundColor':'lightblue', 'borderRadius':'10px', 'height':'50px'}),
    html.Div(
    dcc.Tabs(id='tabs', value='artist-tab', children=[

        dcc.Tab(label=f'Most listened Artist: {most_listened_artist}',value='artist-tab', children=[
            dcc.Graph(id='rankartistfig',figure=Rankartistfig,style={'height': '400px'}),
            html.Label('Pick a date here'),
            dcc.Dropdown(id='dropdown-artist', options=week_options,
                         value=str(weekly_top10_artists['week'].iloc[-1]), clearable=False),
            dcc.Graph(id='output-dropdown-artist', style={'height': '400px'})
        ],style={'borderRadius': '10px','backgroundColor':'lightblue'}),

        dcc.Tab(label=f'Most listened Album: {most_listened_album}',value='album-tab', children=[
            dcc.Graph(id='rankalbumfig',figure=Rankalbumfig, style={'height': '400px'}),
            html.Label('Pick a date here'),
            dcc.Dropdown(id='dropdown-album', options=week_options,
                         value=str(weekly_top10_albums['week'].iloc[-1]), clearable=False),
            dcc.Graph(id='output-dropdown-album', style={'height': '400px'})
        ],style={'borderRadius': '10px'}),

        dcc.Tab(label=f'Most listened Track: {most_listened_track}',value='track-tab', children=[
            dcc.Graph(id='ranktrackfig',figure=Ranktrackfig, style={'height': '400px'}),
            html.Label('Pick a date here'),
            dcc.Dropdown(id='dropdown-track', options=week_options,
                         value=str(weekly_top10_tracks['week'].iloc[-1]), clearable=False),
            dcc.Graph(id='output-dropdown-track', style={'height': '400px'})
        ],style={'borderRadius': '10px'}),

        dcc.Tab(label=f'Most listened Listener: {most_listened_listener}',value='listener-tab', children=[
            dcc.Graph(id='ranklistenerfig',figure=Ranklistenerfig,style={'height': '400px'}),
            html.Label('Pick a date here'),
            dcc.Dropdown(id='dropdown-listener', options=week_options,
                         value=str(weekly_top10_listeners['week'].iloc[-1]), clearable=False),
            dcc.Graph(id='output-dropdown-listener', style={'height': '400px'})
        ],style={'borderRadius': '10px'}),
    ]),
    
    style={'width': '60%', 'float': 'left'}
        
    ),
    
    html.Div([
        dcc.Graph(id='bubblefig',figure=bubblefig, style={'width': '550px', 'height': '547px'}),
        dcc.Input(id='artist-input', type='text', placeholder='Enter an Artist', style={'width': '500px', 'height': '30px'}),
        dcc.Graph(id='track-trend-plot', style={'width': '550px', 'height': '400px'}),
    ], style={'width': '40%', 'float': 'right'})

])


def update_output(selected_week, selected_tab, top_data, y_label):
    filtered_data = top_data[top_data['week'] == selected_week]
    top_data_filtered = filtered_data.groupby(y_label)['count'].sum().nlargest(10).reset_index()
    
    weekfig = px.bar(
        top_data_filtered[::-1], x='count', y=y_label, orientation='h',
        labels={'count': 'count', y_label: y_label},
        title=f'Top 10 {y_label} for Week {selected_week}',
        text='count',
        template='seaborn'
    )
    return weekfig


@app.callback(
    Output('output-dropdown-artist', 'figure'),
    [Input('dropdown-artist', 'value')]
)
    
def update_output_artist(selected_week):
    return update_output(selected_week, 'artist-tab', weekly_top10_artists, 'artist')


@app.callback(
    Output('output-dropdown-album', 'figure'),
    [Input('dropdown-album', 'value')]
)
def update_output_album(selected_week):
    return update_output(selected_week, 'album-tab', weekly_top10_albums, 'album')

@app.callback(
    Output('output-dropdown-track', 'figure'),
    [Input('dropdown-track', 'value')]
)
def update_output_track(selected_week):
    return update_output(selected_week, 'track-tab', weekly_top10_tracks, 'track')

@app.callback(
    Output('output-dropdown-listener', 'figure'),
    [Input('dropdown-listener', 'value')]
)
def update_output_listener(selected_week):
    return update_output(selected_week, 'listener-tab', weekly_top10_listeners, 'listener')


#Line Plot
@app.callback(
    Output('track-trend-plot', 'figure'),
    [Input('artist-input', 'value')]
)

def update_track_trend_plot(selected_artist:str):
    if not selected_artist:
        fig = px.line(
            total_track, x='year', y='count',
            labels={'count': 'count', 'year': 'year'},
            title=f"Total Count of each year",
            template='seaborn'
        )
        fig.update_layout(xaxis_range=[2000, 2023])
        return fig
    
    
    else:
        filtered_data = yearly_track[yearly_track['artist'] == '{}'.format(selected_artist)]
        fig = px.line(
            filtered_data, x='year', y='count',
            labels={'count': 'count', 'year': 'year'},
            title=f"Track Count of {selected_artist} each year",
            template='seaborn'
        )
        fig.update_layout(xaxis_range=[2000, 2023])
        
        return fig

if __name__ == '__main__':
    
    app.run_server(debug=True)