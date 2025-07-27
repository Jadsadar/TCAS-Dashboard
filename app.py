from dash import Dash, html, dash_table, dcc, callback, Output, Input, State
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import datetime
import dash_bootstrap_components as dbc
from datetime import datetime, timedelta

# --- 1. Initialize the app ---
app = Dash(__name__, suppress_callback_exceptions=True, external_stylesheets=[dbc.themes.LUX])

# --- 2. Load CSV data ---
try:
    # --- Load and clean AI Programs Data ---
    ai_programs_df = pd.read_csv('cleaned_aie.csv')
    # Ensure numerical columns are correct type for AI data
    # Clean 'Total program cost'
    ai_programs_df['Total program cost (num)'] = pd.to_numeric(
        ai_programs_df["Total program cost"].astype(str).str.replace(",", ""), errors='coerce'
    )
    # Clean 'term'
    ai_programs_df['term'] = pd.to_numeric(
        ai_programs_df["term"].astype(str).str.replace(",", ""), errors='coerce'
    )
    ai_programs_df = ai_programs_df.dropna(subset=['Total program cost (num)'])

    # --- Load and clean COE Programs Data ---
    coe_programs_df = pd.read_csv('coe_with_term_and_total.csv')
    # Ensure numerical columns are correct type for COE data
    coe_programs_df['Total program cost (num)'] = pd.to_numeric(
        coe_programs_df["Total program cost"].astype(str).str.replace(",", ""), errors='coerce'
    )
    # Assuming 'coe_with_term_and_total.csv' already has a numeric 'term' column
    coe_programs_df = coe_programs_df.dropna(subset=['Total program cost (num)'])

    print("CSV files loaded and cleaned successfully!")
    print(f"AI Programs: {len(ai_programs_df)} records")
    print(f"COE Programs: {len(coe_programs_df)} records")

except FileNotFoundError as e:
    print(f"Error loading CSV files: {e}")
    # Exit if data files are not found to prevent runtime errors
    raise SystemExit("Please ensure 'cleaned_aie.csv' and 'coe_with_term_and_total.csv' are in the correct directory.")
except Exception as e:
    print(f"An error occurred during data loading or cleaning: {e}")
    raise SystemExit("Failed to initialize data. Please check your CSV files and column names.")

# --- 3. Navigation bar ---
navbar = dbc.Navbar(
    [
        dbc.Col(
            dbc.Nav([
                dbc.NavItem(dbc.NavLink("Home", href="/", active="exact", className="ms-5")),
                dbc.NavItem(dbc.NavLink("AI Programs", href="/ai-programs", active="exact")),
                dbc.NavItem(dbc.NavLink("Computer Engineering", href="/coe-programs", active="exact")),
            ], navbar=True),
            xs=12, md=6,
        ),
        dbc.Col(
            html.H1('Tcas Analytics Dashboard', className='text', id='logo', style={"color": "white"}),
            xs=12, md=6,
        ),
    ],
    color="dark",
    dark=True,
)

# --- 4. Components (Reusable Layout Elements) ---
def create_program_filters(program_type, df):
    """Create filter components for university programs"""
    return dbc.Card([
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    html.Label("University:", className="fw-bold"),
                    dcc.Dropdown(
                        id=f'{program_type}-university-filter',
                        options=[{'label': uni, 'value': uni} for uni in sorted(df['University'].unique())],
                        placeholder="Select University",
                        multi=True
                    )
                ], md=4),
                dbc.Col([
                    html.Label("Cost Range (Baht):", className="fw-bold"),
                    dcc.RangeSlider(
                        id=f'{program_type}-cost-range',
                        min=int(df['Total program cost (num)'].min()),
                        max=int(df['Total program cost (num)'].max()),
                        value=[int(df['Total program cost (num)'].min()), int(df['Total program cost (num)'].max())],
                        marks={
                            int(df['Total program cost (num)'].min()): f'{int(df["Total program cost (num)"].min()):,}',
                            int(df['Total program cost (num)'].max()): f'{int(df["Total program cost (num)"].max()):,}'
                        },
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

# --- Modified Chart Components to be in Cards (like Home page) ---
def create_program_charts(program_type):
    """Create charts for university programs, wrapped in cards like the home page"""
    return dbc.Row([
        # --- Chart Card for Cost Distribution (Left) ---
        dbc.Col([
            dbc.Card([
                dbc.CardHeader(html.H5("Cost Distribution", className="mb-0")),
                dbc.CardBody([
                    dcc.Graph(id=f'{program_type}-cost-histogram', config={'displayModeBar': False})
                ]),
            ], className="mb-4 shadow rounded-3") # Added rounded corners and shadow
        ], md=6),  # Left column
        # --- Chart Card for Programs by University (Right) ---
        dbc.Col([
            dbc.Card([
                dbc.CardHeader(html.H5("Programs by University", className="mb-0")),
                dbc.CardBody([
                    dcc.Graph(id=f'{program_type}-university-bar', config={'displayModeBar': False})
                ]),
            ], className="mb-4 shadow rounded-3") # Added rounded corners and shadow
        ], md=6),  # Right column
    ], className="mb-3") # Added margin bottom for spacing

# --- END OF MODIFICATION ---

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

# --- 5. Helper Function for Filtering and Sorting ---
def filter_and_sort_data(df, selected_universities, cost_range, sort_by):
    """Helper function to filter and sort data"""
    filtered_df = df.copy()
    # Filter by University
    if selected_universities and len(selected_universities) > 0:
        filtered_df = filtered_df[filtered_df['University'].isin(selected_universities)]
    # Filter by Cost Range
    if cost_range and len(cost_range) == 2:
        filtered_df = filtered_df[
            (filtered_df['Total program cost (num)'] >= cost_range[0]) &
            (filtered_df['Total program cost (num)'] <= cost_range[1])
        ]
    # Sort
    if sort_by == 'cost_asc':
        filtered_df = filtered_df.sort_values(by='Total program cost (num)', ascending=True)
    elif sort_by == 'cost_desc':
        filtered_df = filtered_df.sort_values(by='Total program cost (num)', ascending=False)
    elif sort_by == 'university':
        filtered_df = filtered_df.sort_values(by='University')
    elif sort_by == 'term':
        # Handle potential NaN in 'term' if necessary
        filtered_df = filtered_df.sort_values(by='term', ascending=True)
    return filtered_df

# --- 6. Page layouts ---
home_layout = html.Div([
    dbc.Row([
        dbc.Col([
            html.H1("Welcome to University Programs Dashboard", className="text-center mb-4"),
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader(html.H4("Cost Overview - AI Engineering", className="mb-0")),
                        dbc.CardBody([
                            dcc.Graph(
                                id='home-ai-cost-graph',
                                figure=px.bar(
                                    ai_programs_df.sort_values(by="Total program cost (num)", ascending=False),
                                    x="University",
                                    y="Total program cost (num)",
                                    title='Total Program Cost (AI Engineering)',
                                    labels={
                                        "Total program cost (num)": "Total Cost (Baht)",
                                        "University": ""
                                    },
                                    color="University",
                                    color_discrete_sequence=px.colors.qualitative.Set1,
                                ).update_layout(
                                    xaxis_tickangle=-45,
                                    height=500,
                                    showlegend=False,
                                    xaxis=dict(showticklabels=False)
                                ).update_traces(),
                                config={'displayModeBar': False}
                            ),
                            html.P("Showing all AI Engineering programs sorted by cost.", className="text-muted small mt-2")
                        ]),
                    ], className="mb-4 shadow rounded-3")
                ], md=6),
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader(html.H4("Cost Overview - Computer Engineering", className="mb-0")),
                        dbc.CardBody([
                            dcc.Graph(
                                id='home-coe-cost-graph',
                                figure=px.bar(
                                    coe_programs_df.sort_values(by="Total program cost (num)", ascending=False).head(10),
                                    x='University',
                                    y='Total program cost (num)',
                                    title='Top 10 Universities - Total Program Cost (Computer Engineering)',
                                    labels={
                                        'Total program cost (num)': 'Total Cost (Baht)',
                                        'University': ''
                                    },
                                    color="University",
                                    color_discrete_sequence=px.colors.qualitative.Set1,
                                ).update_layout(
                                    xaxis_tickangle=-45,
                                    height=500,
                                    showlegend=False,
                                    xaxis=dict(showticklabels=False)
                                ).update_traces(),
                                config={'displayModeBar': False}
                            ),
                            html.P("Showing the top 10 universities by program cost.", className="text-muted small mt-2")
                        ]),
                    ], className="mb-4 shadow rounded-3")
                ], md=6),
            ]),
            dbc.Card([
                dbc.CardBody([
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
                    ])
                ])
            ])
        ])
    ])
])

ai_programs_layout = html.Div([
    html.H2("AI Engineering Programs", className="mb-4 text-center"),
    create_summary_stats('ai'),
    create_program_filters('ai', ai_programs_df),
    # --- Use the modified chart component ---
    create_program_charts('ai'),
    # --- END OF MODIFICATION ---
    create_program_table('ai')
])

coe_programs_layout = html.Div([
    html.H2("Computer Engineering Programs", className="mb-4 text-center"),
    create_summary_stats('coe'),
    create_program_filters('coe', coe_programs_df),
    # Assuming you want the same card style for COE charts, you would modify its chart component too.
    # For now, keeping the original structure for COE as per your initial request to focus on AI.
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader(html.H5("Cost Distribution")),
                dbc.CardBody([
                    dcc.Graph(id=f'coe-cost-histogram')
                ])
            ])
        ], md=6),
        dbc.Col([
            dbc.Card([
                dbc.CardHeader(html.H5("Programs by University")),
                dbc.CardBody([
                    dcc.Graph(id=f'coe-university-bar')
                ])
            ])
        ], md=6),
    ], className="mb-3"),
    create_program_table('coe')
])

# --- 7. Main layout with URL routing ---
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    navbar,
    dbc.Container([
        html.Div(id='page-content')
    ], fluid=True, className="mt-3")
])

# --- 8. Callbacks ---
@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    """Display the appropriate page layout based on the URL."""
    if pathname == '/ai-programs':
        return ai_programs_layout
    elif pathname == '/coe-programs':
        return coe_programs_layout
    else:
        return home_layout

# --- Callbacks for AI Programs Page ---
@app.callback(
    [Output('ai-total-programs', 'children'),
     Output('ai-avg-cost', 'children'),
     Output('ai-min-cost', 'children'),
     Output('ai-max-cost', 'children')],
    [Input('ai-university-filter', 'value'),
     Input('ai-cost-range', 'value'),
     Input('ai-sort', 'value')]
)
def update_ai_summary_stats(selected_universities, cost_range, sort_by):
    """Update the summary statistics cards for AI."""
    filtered_df = filter_and_sort_data(ai_programs_df, selected_universities, cost_range, sort_by)
    total_programs = len(filtered_df)
    if total_programs > 0:
        avg_cost = f"{filtered_df['Total program cost (num)'].mean():,.0f} Baht"
        min_cost_val = filtered_df['Total program cost (num)'].min()
        min_cost = f"{min_cost_val:,.0f} Baht"
        max_cost_val = filtered_df['Total program cost (num)'].max()
        max_cost = f"{max_cost_val:,.0f} Baht"
    else:
        avg_cost = "N/A"
        min_cost = "N/A"
        max_cost = "N/A"
    return total_programs, avg_cost, min_cost, max_cost

@app.callback(
    [Output('ai-cost-histogram', 'figure'),
     Output('ai-university-bar', 'figure')],
    [Input('ai-university-filter', 'value'),
     Input('ai-cost-range', 'value'),
     Input('ai-sort', 'value')]
)
def update_ai_charts(selected_universities, cost_range, sort_by):
    """Update the charts for AI."""
    filtered_df = filter_and_sort_data(ai_programs_df, selected_universities, cost_range, sort_by)
    # Histogram
    if filtered_df.empty:
        hist_fig = go.Figure()
        hist_fig.add_annotation(text="No data available", showarrow=False, xref="paper", yref="paper", x=0.5, y=0.5)
        hist_fig.update_layout(title="Cost Distribution")
    else:
        hist_fig = px.histogram(filtered_df, x='Total program cost (num)', nbins=10,
                                title='Distribution of Total Program Costs',
                                labels={'Total program cost (num)': 'Total Cost (Baht)'})
        hist_fig.update_layout(yaxis_title="Number of Programs")
    # Bar Chart - Programs per University
    if filtered_df.empty:
        bar_fig = go.Figure()
        bar_fig.add_annotation(text="No data available", showarrow=False, xref="paper", yref="paper", x=0.5, y=0.5)
        bar_fig.update_layout(title="Programs by University")
    else:
        uni_counts = filtered_df['University'].value_counts().reset_index()
        uni_counts.columns = ['University', 'Count']
        bar_fig = px.bar(uni_counts, x='University', y='Count',
                         title='Number of Programs per University',
                         labels={'Count': 'Number of Programs'})
        bar_fig.update_layout(xaxis_tickangle=-45)
    return hist_fig, bar_fig

# --- Modified AI Table Callback to include 'term' and format columns ---
# --- Modified AI Table Callback to match COE page columns ---
# --- Modified AI Table Callback for Text Wrapping ---
@app.callback(
    Output('ai-table-container', 'children'),
    [Input('ai-university-filter', 'value'),
     Input('ai-cost-range', 'value'),
     Input('ai-sort', 'value')]
)
def update_ai_table(selected_universities, cost_range, sort_by):
    """Update the data table for AI, including 'Total program cost (num)' and 'term' columns."""
    filtered_df = filter_and_sort_data(ai_programs_df, selected_universities, cost_range, sort_by)
    if filtered_df.empty:
        return html.P("No programs match the selected filters.", className="text-center text-muted")
    # Select columns to display in the table to match COE page
    display_columns = ['University', 'Course Name', 'Total program cost (num)', 'term']
    table_data = filtered_df[display_columns].copy()
    # Format the numeric columns for display in the table
    table_data['Total program cost (num)'] = table_data['Total program cost (num)'].apply(lambda x: f"{x:,.0f} Baht")
    # Handle potential NaN in 'term' (now numeric)
    table_data['term'] = table_data['term'].apply(lambda x: f"{x:,.0f} Baht/term" if pd.notnull(x) else "N/A")
    return dash_table.DataTable(
        data=table_data.to_dict('records'),
        columns=[{"name": col, "id": col} for col in display_columns], # Use display column names
        style_table={'overflowX': 'auto'},
        # --- START OF MODIFICATIONS FOR WRAPPING ---
        style_cell={
            'textAlign': 'left',
            'padding': '8px', # Slightly increased padding for readability
            'whiteSpace': 'normal', # Allow text to wrap
            'height': 'auto',      # Adjust height automatically
            'lineHeight': '1.4'    # Improve line spacing
        },
        style_header={
            'backgroundColor': 'rgb(230, 230, 230)',
            'fontWeight': 'bold',
             'whiteSpace': 'normal', # Allow header text to wrap if needed
             'height': 'auto'
        },
        # Optional: Set explicit column widths if needed for better control
        # style_data_conditional=[
        #     {
        #         'if': {'column_id': 'University'},
        #         'minWidth': '150px', 'width': '180px', 'maxWidth': '250px'
        #     },
        #     {
        #         'if': {'column_id': 'Course Name'},
        #         'minWidth': '200px', 'width': '250px', 'maxWidth': '400px'
        #     },
        #     # Add widths for other columns as needed
        # ],
        page_size=10
        # --- END OF MODIFICATIONS FOR WRAPPING ---
    )
# --- END OF MODIFICATION ---

# --- Callbacks for Computer Engineering Page ---
@app.callback(
    [Output('coe-total-programs', 'children'),
     Output('coe-avg-cost', 'children'),
     Output('coe-min-cost', 'children'),
     Output('coe-max-cost', 'children')],
    [Input('coe-university-filter', 'value'),
     Input('coe-cost-range', 'value'),
     Input('coe-sort', 'value')]
)
def update_coe_summary_stats(selected_universities, cost_range, sort_by):
    """Update the summary statistics cards for COE."""
    filtered_df = filter_and_sort_data(coe_programs_df, selected_universities, cost_range, sort_by)
    total_programs = len(filtered_df)
    if total_programs > 0:
        avg_cost = f"{filtered_df['Total program cost (num)'].mean():,.0f} Baht"
        min_cost_val = filtered_df['Total program cost (num)'].min()
        min_cost = f"{min_cost_val:,.0f} Baht"
        max_cost_val = filtered_df['Total program cost (num)'].max()
        max_cost = f"{max_cost_val:,.0f} Baht"
    else:
        avg_cost = "N/A"
        min_cost = "N/A"
        max_cost = "N/A"
    return total_programs, avg_cost, min_cost, max_cost

@app.callback(
    [Output('coe-cost-histogram', 'figure'),
     Output('coe-university-bar', 'figure')],
    [Input('coe-university-filter', 'value'),
     Input('coe-cost-range', 'value'),
     Input('coe-sort', 'value')]
)
def update_coe_charts(selected_universities, cost_range, sort_by):
    """Update the charts for COE."""
    filtered_df = filter_and_sort_data(coe_programs_df, selected_universities, cost_range, sort_by)
    # Histogram
    if filtered_df.empty:
        hist_fig = go.Figure()
        hist_fig.add_annotation(text="No data available", showarrow=False, xref="paper", yref="paper", x=0.5, y=0.5)
        hist_fig.update_layout(title="Cost Distribution")
    else:
        hist_fig = px.histogram(filtered_df, x='Total program cost (num)', nbins=10,
                                title='Distribution of Total Program Costs',
                                labels={'Total program cost (num)': 'Total Cost (Baht)'})
        hist_fig.update_layout(yaxis_title="Number of Programs")
    # Bar Chart - Programs per University
    if filtered_df.empty:
        bar_fig = go.Figure()
        bar_fig.add_annotation(text="No data available", showarrow=False, xref="paper", yref="paper", x=0.5, y=0.5)
        bar_fig.update_layout(title="Programs by University")
    else:
        uni_counts = filtered_df['University'].value_counts().reset_index()
        uni_counts.columns = ['University', 'Count']
        bar_fig = px.bar(uni_counts, x='University', y='Count',
                         title='Number of Programs per University',
                         labels={'Count': 'Number of Programs'})
        bar_fig.update_layout(xaxis_tickangle=-45)
    return hist_fig, bar_fig

@app.callback(
    Output('coe-table-container', 'children'),
    [Input('coe-university-filter', 'value'),
     Input('coe-cost-range', 'value'),
     Input('coe-sort', 'value')]
)
def update_coe_table(selected_universities, cost_range, sort_by):
    """Update the data table for COE."""
    filtered_df = filter_and_sort_data(coe_programs_df, selected_universities, cost_range, sort_by)
    if filtered_df.empty:
        return html.P("No programs match the selected filters.", className="text-center text-muted")
    # Select columns to display in the table
    display_columns = ['University', 'Course Name', 'Total program cost (num)', 'term']
    table_data = filtered_df[display_columns].copy()
    # Format currency columns for display
    table_data['Total program cost (num)'] = table_data['Total program cost (num)'].apply(lambda x: f"{x:,.0f} Baht")
    # Handle potential NaN in 'term'
    table_data['term'] = table_data['term'].apply(lambda x: f"{x:,.0f} Baht/term" if pd.notnull(x) else "N/A")
    return dash_table.DataTable(
        data=table_data.to_dict('records'),
        columns=[{"name": col, "id": col} for col in display_columns],
        style_table={'overflowX': 'auto'},
        style_cell={'textAlign': 'left', 'padding': '5px'},
        style_header={
            'backgroundColor': 'rgb(230, 230, 230)',
            'fontWeight': 'bold'
        },
        page_size=10
    )

# --- 9. Run the app ---
if __name__ == '__main__':
    app.run(debug=True)