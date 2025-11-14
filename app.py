import json
import numpy as np
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objects as go

# =============================
# Load presets from external JSON file
# =============================
with open("presets_config.json", "r") as f:
    presets = json.load(f)

# =============================
# Compute probabilities
# =============================
P_uf_values = np.linspace(0, 1, 101)

def compute_probabilities(P_ab_pred, P_prev_ab, P_fn, P_man):
    P_alg_fail = P_ab_pred * P_prev_ab
    return P_man - (P_uf_values * P_alg_fail + (1 - P_uf_values) * P_fn)

# Initial preset
first_preset_name = list(presets.keys())[0]
initial = presets[first_preset_name]
initial_P_ab_pred = initial["P_ab_pred"]
initial_P_prev_ab = initial["P_prev_ab"]
initial_P_fn = initial["P_fn"]
initial_P_man = initial.get("P_man", 0.05)

# Initial curve
initial_curve = compute_probabilities(initial_P_ab_pred, initial_P_prev_ab, initial_P_fn, initial_P_man)

# Initial figure
fig = go.Figure()
fig.add_trace(go.Scatter(x=P_uf_values, y=initial_curve, mode='lines', name='P(A): Algorithm Failure'))
fig.update_layout(title=f"Preset: {first_preset_name}", xaxis_title="P_uf", yaxis_title="P(A)")

# =============================
# Dash App Layout
# =============================
app = dash.Dash(__name__)
app.layout = html.Div([
    html.H1("Interactive Simulation"),
    dcc.Graph(id='probability-graph', figure=fig),

    html.Div([
        html.Label("Preset"),
        dcc.Dropdown(
            id='preset-dropdown',
            options=[{'label': k, 'value': k} for k in presets.keys()],
            value=first_preset_name
        ),
        html.Br(),

        html.Label("Probability of Failure if Poor Input (User Error)"),
        dcc.Slider(id='slider-ab-pred', min=0, max=1, step=0.01, value=initial_P_ab_pred, marks={0: '0', 0.5: '0.5', 1: '1'},tooltip={"placement": "bottom", "always_visible": True}),
        html.Label("Prevalence of Condition in Population"),
        dcc.Slider(id='slider-prev-ab', min=0, max=1, step=0.01, value=initial_P_prev_ab, marks={0: '0', 0.5: '0.5', 1: '1'},tooltip={"placement": "bottom", "always_visible": True}),
        html.Label("Probability of Failure if Sufficient Input"),
        dcc.Slider(id='slider-fn', min=0, max=1, step=0.01, value=initial_P_fn, marks={0: '0', 0.5: '0.5', 1: '1'},tooltip={"placement": "bottom", "always_visible": True}),
        html.Label("Probability of Failure with Manual Method"),
        dcc.Slider(id='slider-man', min=0, max=1, step=0.01, value=initial_P_man, marks={0: '0', 0.5: '0.5', 1: '1'},tooltip={"placement": "bottom", "always_visible": True}),

        html.Br(),
        html.Button("Reset to Default", id='reset-button', n_clicks=0)
    ], style={'marginTop': '30px'})
])

# =============================
# Callback
# =============================
@app.callback(
    Output('probability-graph', 'figure'),
    Output('slider-ab-pred', 'value'),
    Output('slider-prev-ab', 'value'),
    Output('slider-fn', 'value'),
    Output('slider-man', 'value'),
    Input('preset-dropdown', 'value'),
    Input('slider-ab-pred', 'value'),
    Input('slider-prev-ab', 'value'),
    Input('slider-fn', 'value'),
    Input('slider-man', 'value'),
    Input('reset-button', 'n_clicks')
)
def update_graph(preset, ab_pred, prev_ab, fn, man, reset_clicks):
    ctx = dash.callback_context
    # If dropdown or reset button triggered, use preset values
    if ctx.triggered and ('preset-dropdown' in ctx.triggered[0]['prop_id'] or 'reset-button' in ctx.triggered[0]['prop_id']):
        vals = presets[preset]
        ab_pred = vals["P_ab_pred"]
        prev_ab = vals["P_prev_ab"]
        fn = vals["P_fn"]
        man = vals.get("P_man", 0.05)

    curve = compute_probabilities(ab_pred, prev_ab, fn, man)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=P_uf_values, y=curve, mode='lines', name='Failure Rate Margin (Manual Method Failure - SS Failure)'))
    fig.update_layout(title=f"Preset: {preset}<br>{ab_pred},{prev_ab},{fn},{man}", xaxis_title="Probability of User Failure", yaxis_title="Failure Rate Margin (Manual Method Failure - SS Failure)")
    return fig, ab_pred, prev_ab, fn, man

# =============================
# Run App
# =============================
if __name__ == '__main__':
    app.run(debug=True)