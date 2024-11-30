import dash
import dash_bootstrap_components as dbc
from dash import html, dcc, Input, Output
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

app = dash.Dash(__name__, external_stylesheets=[
    dbc.themes.BOOTSTRAP,
    'https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap',
    'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.3/css/all.min.css'
])


df = pd.read_csv('fitness_data.csv')
df['Date'] = pd.to_datetime(df['Date'])

def create_header():
    return dbc.Navbar(
        dbc.Container([
            html.Div([
                html.I(className="fas fa-dumbbell me-2"),
                html.H1("FitTrack", className="navbar-brand mb-0"),
            ], className="d-flex align-items-center"),
            
            dbc.Nav([
                dbc.NavItem(dbc.NavLink("Dashboard", href="#", active=True)),
                
                dbc.NavItem(
                    html.Div([
                        html.Img(src="/assets/boy.png", className="avatar"),
                        html.Span("Waliy", className="ms-2 d-none d-md-inline")
                    ], className="user-profile")
                )
            ], className="ms-auto")
        ]),
        className="navbar-custom",
        dark=False,
    )

def create_kpi_cards(df):
    total_hours = df['Duration'].sum() / 60
    total_calories = df['Calories'].sum()
    goal_progress = 75

    return dbc.Row([
        dbc.Col(
            dbc.Card([
                dbc.CardBody([
                    html.Div([
                        html.I(className="fas fa-clock stat-icon"),
                        html.Div([
                            html.P("Total Hours", className="stat-label"),
                            html.H3(f"{total_hours:.1f}", className="stat-value"),
                            html.P("↑ 12% vs last month", className="stat-change positive")
                        ])
                    ], className="d-flex align-items-center")
                ])
            ], className="stat-card")
        ),
        dbc.Col(
            dbc.Card([
                dbc.CardBody([
                    html.Div([
                        html.I(className="fas fa-fire stat-icon"),
                        html.Div([
                            html.P("Calories Burned", className="stat-label"),
                            html.H3(f"{total_calories:,}", className="stat-value"),
                            html.P("↑ 8% vs last month", className="stat-change positive")
                        ])
                    ], className="d-flex align-items-center")
                ])
            ], className="stat-card")
        ),
        dbc.Col(
            dbc.Card([
                dbc.CardBody([
                    html.Div([
                        html.I(className="fas fa-bullseye stat-icon"),
                        html.Div([
                            html.P("Goal Progress", className="stat-label"),
                            html.H3(f"{goal_progress}%", className="stat-value"),
                            html.Div(className="progress mt-2",
                                children=html.Div(className="progress-bar", 
                                                style={"width": f"{goal_progress}%"}))
                        ])
                    ], className="d-flex align-items-center")
                ])
            ], className="stat-card")
        ),
    ], className="g-4 mb-4")


def create_charts(df):
    weekly_data = df.groupby(df['Date'].dt.strftime('%Y-%W')).agg({
        'Calories': 'sum',
        'Duration': 'sum'
    }).reset_index()
    
    line_chart = go.Figure()
    line_chart.add_trace(go.Scatter(
        x=weekly_data['Date'],
        y=weekly_data['Calories'],
        name='Calories',
        line=dict(color='#4361ee', width=3),
        fill='tonexty',
        fillcolor='rgba(67, 97, 238, 0.1)'
    ))
    
    line_chart.update_layout(
        title=None,
        template='plotly_white',
        height=350,
        margin=dict(l=20, r=20, t=20, b=20),
        paper_bgcolor='white',
        plot_bgcolor='white',
        font=dict(family="Inter"),
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor='#f0f0f0')
    )
    
   
    workout_dist = df['Workout_Type'].value_counts()
    pie_chart = px.pie(
        values=workout_dist.values,
        names=workout_dist.index,
        hole=0.7,
        color_discrete_sequence=['#4361ee', '#3f37c9', '#3a0ca3', '#480ca8']
    )
    
    pie_chart.update_layout(
        title=None,
        height=350,
        margin=dict(l=20, r=20, t=20, b=20),
        paper_bgcolor='white',
        font=dict(family="Inter"),
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    return line_chart, pie_chart

def create_activity_log(df):
    return dbc.Table.from_dataframe(
        df[['Date', 'Workout_Type', 'Duration', 'Calories', 'Intensity']],
        striped=True,
        bordered=True,
        hover=True,
        responsive=True,
        className="activity-table"
    )

app.layout = dbc.Container([
    create_header(),
    html.Div([
        create_kpi_cards(df),
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.H5("Weekly Progress", className="mb-0"),
                        dbc.ButtonGroup([
                            dbc.Button("Week", color="light", size="sm"),
                            dbc.Button("Month", color="light", size="sm", outline=True),
                            dbc.Button("Year", color="light", size="sm", outline=True),
                        ], size="sm")
                    ], className="d-flex justify-content-between align-items-center"),
                    dbc.CardBody([
                        dcc.Graph(figure=create_charts(df)[0], config={'displayModeBar': False})
                    ])
                ], className="chart-card")
            ], width=8),
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.H5("Workout Distribution", className="mb-0")
                    ]),
                    dbc.CardBody([
                        dcc.Graph(figure=create_charts(df)[1], config={'displayModeBar': False})
                    ])
                ], className="chart-card")
            ], width=4)
        ], className="g-4 mb-4"),
        dbc.Card([
            dbc.CardHeader([
                html.H5("Recent Activities", className="mb-0"),
                dbc.Button("View All", color="primary", size="sm")
            ], className="d-flex justify-content-between align-items-center"),
            dbc.CardBody([
                create_activity_log(df.head(5))
            ])
        ], className="chart-card")
    ], className="dashboard-content")
], fluid=True, className="px-4 py-3")

if __name__ == '__main__':
    app.run(debug=True) 