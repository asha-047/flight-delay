# dashboard.py
import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html

# Load dataset
df = pd.read_csv(r"D:\Projects\FlightDelayApp\Airlines.csv")

# Keep only top 10 airports, others as 'OTHER'
top_airports = ["JFK","LAX","ORD","ATL","SFO","MIA","SEA","DFW","DEN","BOS"]
df['AirportFrom'] = df['AirportFrom'].apply(lambda x: x if x in top_airports else 'OTHER')
df['AirportTo'] = df['AirportTo'].apply(lambda x: x if x in top_airports else 'OTHER')

# Add Flight_Status column based on Delay
df['Flight_Status'] = df['Delay'].apply(lambda x: 'Delayed' if x > 0 else 'On Time')

# --- Summary cards ---
top_airlines = ["AA","DL","UA","WN","CO","US","AS","B6","HA","OO"]  # all airlines used in model
df_model_airlines = df[df['Airline'].isin(top_airlines)]

total_airlines = df_model_airlines['Airline'].nunique()
total_sources = df_model_airlines['AirportFrom'].nunique()
total_destinations = df_model_airlines['AirportTo'].nunique()
total_flights = len(df_model_airlines)

# --- Flights by Airline ---
airline_summary = df_model_airlines.groupby('Airline').agg(
    On_Time=('Flight_Status', lambda x: (x=='On Time').sum()),
    Delayed=('Flight_Status', lambda x: (x=='Delayed').sum())
).reset_index()

fig_airline = px.bar(
    airline_summary,
    x='Airline',
    y=['On_Time','Delayed'],
    title='Flights by Airline',  # Removed "Top 10"
    barmode='stack',
    labels={'value':'Number of Flights','Airline':'Airline'},
    color_discrete_map={'On_Time':'green','Delayed':'red'}
)

# --- Pie chart: Overall On Time vs Delayed ---
status_summary = df_model_airlines['Flight_Status'].value_counts().reset_index()
status_summary.columns = ['Flight_Status','Count']

fig_pie = px.pie(
    status_summary,
    names='Flight_Status',
    values='Count',
    title='Overall Flight Status',
    color='Flight_Status',
    color_discrete_map={'On Time':'green','Delayed':'red'}
)

# --- Bar chart: Delays by DayOfWeek ---
day_summary = df_model_airlines.groupby('DayOfWeek')['Delay'].sum().reset_index()
fig_day = px.bar(
    day_summary,
    x='DayOfWeek',
    y='Delay',
    title='Delays by Day of Week',
    labels={'DayOfWeek':'Day of Week','Delay':'Number of Delayed Flights'},
    color='Delay',
    color_continuous_scale='reds'
)

# --- Dash app ---
app = Dash(__name__)

app.layout = html.Div([
    html.H1("✈️ Flight Delay Dashboard", style={'textAlign':'center', 'color':'#4B0082', 'marginBottom':'20px'}),
    
    # Summary cards
    html.Div([
        html.Div(f"Total Airlines: {total_airlines}", style={'backgroundColor':'#E0FFFF','padding':'15px','margin':'5px','borderRadius':'10px','textAlign':'center','fontWeight':'bold'}),
        html.Div(f"Total Sources: {total_sources}", style={'backgroundColor':'#E6E6FA','padding':'15px','margin':'5px','borderRadius':'10px','textAlign':'center','fontWeight':'bold'}),
        html.Div(f"Total Destinations: {total_destinations}", style={'backgroundColor':'#FFFACD','padding':'15px','margin':'5px','borderRadius':'10px','textAlign':'center','fontWeight':'bold'}),
        html.Div(f"Total Flights: {total_flights}", style={'backgroundColor':'#F0E68C','padding':'15px','margin':'5px','borderRadius':'10px','textAlign':'center','fontWeight':'bold'}),
    ], style={'display':'flex','justifyContent':'space-around','marginBottom':'30px'}),
    
    # Graphs: stacked bar, pie, day-of-week bar
    html.Div([
        dcc.Graph(figure=fig_airline, style={'width':'32%','display':'inline-block'}),
        dcc.Graph(figure=fig_pie, style={'width':'32%','display':'inline-block'}),
        dcc.Graph(figure=fig_day, style={'width':'32%','display':'inline-block'})
    ], style={'display':'flex','justifyContent':'space-around'})
])

# Run the app
if __name__ == '__main__':
    app.run(debug=True, port=8050)
