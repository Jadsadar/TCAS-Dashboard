from dash import dash, html, dash_table, dcc, callback, Output, Input, State
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import datetime
import dash_bootstrap_components as dbc
from datetime import datetime, timedelta

# Initialize the app
app = dash.Dash(__name__, suppress_callback_exceptions=True, external_stylesheets=[dbc.themes.LUX, 'styles.css'])

# Load CSV data
try:
    ai_programs_df = pd.read_csv('cleaned_aie.csv')
    coe_programs_df = pd.read_csv('coe_with_term_and_total.csv')
    print("CSV files loaded successfully!")
    print(f"AI Programs: {len(ai_programs_df)} records")
    print(f"COE Programs: {len(coe_programs_df)} records")
except FileNotFoundError as e:
    print(f"CSV file not found: {e}")
    # Create sample data if files don't exist
    ai_programs_df = pd.DataFrame({
        'University': ['Sample University 1', 'Sample University 2'],
        'Program': ['AI Engineering', 'AI Engineering'],
        'Course Name': ['Sample AI Course 1', 'Sample AI Course 2'],
        'Cost': ['100,000', '150,000'],
        'CleanCosts': [100000, 150000],
        'term': [12500, 18750],
        'Total program cost': [100000, 150000]
    })
    coe_programs_df = pd.DataFrame({
        'University': ['Sample University 1', 'Sample University 2'],
        'Program': ['Computer Engineering', 'Computer Engineering'],
        'Course Name': ['Sample COE Course 1', 'Sample COE Course 2'],
        'Cost': ['120,000', '180,000'],
        'CleanCosts': [120000, 180000],
        'term': [15000, 22500],
        'Total program cost': [120000, 180000]
    })

# Navigation bar
navbar = dbc.Navbar(
    [
        dbc.Col(
            dbc.Nav([
                dbc.NavItem(dbc.NavLink("Home", href="/", active="exact", className="ms-3")),
                dbc.NavItem(dbc.NavLink("AI Programs", href="/ai-programs", active="exact")),
                dbc.NavItem(dbc.NavLink("Computer Engineering", href="/coe-programs", active="exact")),
            ], navbar=True),
            xs=12, md=6,
        ),
        dbc.Col(
            html.H1('University Programs Dashboard', className='text', id='logo'),
            xs=12, md=6,
        ),
    ],
    color="dark",
    dark=True,
)

# University Programs Components
def create_program_filters(program_type):
    """Create filter components for university programs"""
    return dbc.Card([
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    html.Label("University:", className="fw-bold"),
                    dcc.Dropdown(
                        id=f'{program_type}-university-filter',
                        placeholder="Select University",
                        multi=True
                    )
                ], md=4),
                dbc.Col([
                    html.Label("Cost Range (Baht):", className="fw-bold"),
                    dcc.RangeSlider(
                        id=f'{program_type}-cost-range',
                        tooltip={"placement": "bottom", "always_visible": True}
                    )
                ], md=4),
                dbc.Col([
                    html.Label("Sort by:", className="fw-bold"),
                    dcc.Dropdown(
                        id=f'{program_type}-sort',
                        options=[
                            {'label': 'Total Cost (Low to High)', 'value': 'cost_asc'},
                            {'label': 'Total Cost (High to Low)', 'value': 'cost_desc'},
                            {'label': 'University Name', 'value': 'university'},
                            {'label': 'Term Cost', 'value': 'term'}
                        ],
                        value='cost_asc'
                    )
                ], md=4),
            ])
        ])
    ], className="mb-3")

def create_program_table(program_type):
    """Create table component for university programs"""
    return dbc.Card([
        dbc.CardHeader(html.H5("Program Details")),
        dbc.CardBody([
            html.Div(id=f'{program_type}-table-container')
        ])
    ])

def create_program_charts(program_type):
    """Create charts for university programs"""
    return dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader(html.H5("Cost Distribution")),
                dbc.CardBody([
                    dcc.Graph(id=f'{program_type}-cost-histogram')
                ])
            ])
        ], md=6),
        dbc.Col([
            dbc.Card([
                dbc.CardHeader(html.H5("Programs by University")),
                dbc.CardBody([
                    dcc.Graph(id=f'{program_type}-university-bar')
                ])
            ])
        ], md=6),
    ], className="mb-3")

def create_summary_stats(program_type):
    """Create summary statistics cards"""
    return dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4(id=f'{program_type}-total-programs', className="text-primary"),
                    html.P("Total Programs")
                ])
            ], className="text-center")
        ], md=3),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4(id=f'{program_type}-avg-cost', className="text-success"),
                    html.P("Average Cost")
                ])
            ], className="text-center")
        ], md=3),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4(id=f'{program_type}-min-cost', className="text-info"),
                    html.P("Lowest Cost")
                ])
            ], className="text-center")
        ], md=3),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4(id=f'{program_type}-max-cost', className="text-warning"),
                    html.P("Highest Cost")
                ])
            ], className="text-center")
        ], md=3),
    ], className="mb-3")

# Page layouts
home_layout = html.Div([
    dbc.Row([
        dbc.Col([
            html.H1("Welcome to University Programs Dashboard", className="text-center mb-4"),
            dbc.Card([
                dbc.CardBody([
                    html.H4("Overview"),
                    html.P(f"This dashboard provides comprehensive information about university programs in Thailand."),
                    html.Hr(),
                    dbc.Row([
                        dbc.Col([
                            dbc.Card([
                                dbc.CardBody([
                                    html.H3(f"{len(ai_programs_df)}", className="text-primary"),
                                    html.P("AI Engineering Programs")
                                ])
                            ], className="text-center")
                        ], md=6),
                        dbc.Col([
                            dbc.Card([
                                dbc.CardBody([
                                    html.H3(f"{len(coe_programs_df)}", className="text-success"),
                                    html.P("Computer Engineering Programs")
                                ])
                            ], className="text-center")
                        ], md=6),
                    ]),
                    html.Hr(),
                    html.H5("Features:"),
                    html.Ul([
                        html.Li("Filter programs by university and cost range"),
                        html.Li("Interactive data visualization"),
                        html.Li("Compare program costs across universities"),
                        html.Li("Detailed program information tables")
                    ])
                ])
            ])
        ])
    ])
])

ai_programs_layout = html.Div([
    html.H2("AI Engineering Programs", className="mb-4 text-center"),
    create_summary_stats('ai'),
    create_program_filters('ai'),
    create_program_charts('ai'),
    create_program_table('ai')
])

coe_programs_layout = html.Div([
    html.H2("Computer Engineering Programs", className="mb-4 text-center"),
    create_summary_stats('coe'),
    create_program_filters('coe'),
    create_program_charts('coe'),
    create_program_table('coe')
])

# Main layout with URL routing
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    navbar,
    dbc.Container([
        html.Div(id='page-content')
    ], fluid=True, className="mt-3")
])



if __name__ == '__main__':
    app.run(debug=True)