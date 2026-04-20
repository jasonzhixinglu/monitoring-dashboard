import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime
import sys
import os
sys.path.insert(0, '/workspaces/monitoring-dashboard')
sys.path.insert(0, '/workspaces/haver-data')

import kaleido  # for static image export

# Set output directory
output_dir = '/workspaces/monitoring-dashboard/sandbox/charts'
os.makedirs(output_dir, exist_ok=True)

from src.data_access import load_series

# Load the two GDP series
qoq_sa = load_series('s924ngcp@emergepr')  # Q/Q % change, SA
level = load_series('h924ngpc@emergepr')   # Level, SA, for YoY calc

# Compute YoY growth from level series
# YoY = (level_t / level_t-4 - 1) * 100 for quarterly data
level_sorted = level.sort_index()
yoy = ((level_sorted / level_sorted.shift(4)) - 1) * 100

# Combine into one dataframe
gdp_df = pd.DataFrame({
    'QoQ_SA': qoq_sa,
    'YoY': yoy
}).dropna()

print("GDP data loaded:")
print(gdp_df.tail(8))
print(f"\nLatest Q1 2026 QoQ: {gdp_df['QoQ_SA'].iloc[-1]:.2f}%")
print(f"Latest Q1 2026 YoY: {gdp_df['YoY'].iloc[-1]:.2f}%")

# Create dual-axis chart: bars for Q/Q, line for YoY
fig = go.Figure()

# Bar chart for Q/Q SA (left axis)
fig.add_trace(go.Bar(
    x=gdp_df.index,
    y=gdp_df['QoQ_SA'],
    name='Q/Q % change (SA)',
    marker=dict(color='steelblue', opacity=0.7),
    yaxis='y1'
))

# Line chart for YoY (right axis)
fig.add_trace(go.Scatter(
    x=gdp_df.index,
    y=gdp_df['YoY'],
    name='Year-on-year %',
    mode='lines+markers',
    line=dict(color='darkred', width=2),
    marker=dict(size=6),
    yaxis='y2'
))

# Highlight the latest Q1 2026 release
latest_date = gdp_df.index[-1].strftime('%Y-%m-%d')
fig.add_shape(type='line', x0=latest_date, x1=latest_date, y0=0, y1=1, xref='x', yref='paper',
              line=dict(dash='dash', color='gray'))
fig.add_annotation(x=latest_date, y=1, xref='x', yref='paper', text='Q1 2026',
                   showarrow=False, xanchor='right', yanchor='top')

# Layout with dual axes
fig.update_layout(
    title='China: Real GDP Growth',
    xaxis=dict(title='Quarter'),
    yaxis=dict(title='Q/Q % change (SA)', side='left'),
    yaxis2=dict(title='YoY %', overlaying='y', side='right'),
    hovermode='x unified',
    template='plotly_white',
    height=500,
    width=900
)

cutoff = pd.Timestamp.now() - pd.DateOffset(years=5)
fig.update_xaxes(range=[cutoff, pd.Timestamp.now()])
gdp_visible = gdp_df[gdp_df.index >= cutoff]
fig.update_layout(
    yaxis=dict(range=[gdp_visible['QoQ_SA'].min() - 0.5, gdp_visible['QoQ_SA'].max() + 0.5]),
    yaxis2=dict(range=[gdp_visible['YoY'].min() - 1, gdp_visible['YoY'].max() + 1], overlaying='y', side='right'),
)
fig.write_image(f'{output_dir}/gdp_chart.png', width=1200, height=600)
print(f"GDP chart saved to {output_dir}/gdp_chart.png")

import plotly.subplots as sp
from src.factor_analysis import extract_factor

# === ACTIVITY INDICATORS ===
# Load March activity data: IVA, Retail, Exports, TSF

iva_level = load_series('n924d@emergepr')
retail_level = load_series('n924trs@emergepr')
exports_level = load_series('h924ixd@emergepr')
tsf_level = load_series('n924fczm@emergepr')

# Compute YoY growth
iva_yoy = iva_level.pct_change(12) * 100
retail_yoy = retail_level.pct_change(12) * 100
exports_yoy = exports_level.pct_change(12) * 100
tsf_yoy = tsf_level.pct_change(12) * 100

# Combine into dataframe
activity_df = pd.DataFrame({
    'IVA_YoY': iva_yoy,
    'Retail_YoY': retail_yoy,
    'Exports_YoY': exports_yoy,
    'TSF_YoY': tsf_yoy
}).dropna()

print("\nActivity indicators (last 12 months):")
print(activity_df.tail(12))

# Chart 1: YoY trends (4-panel)
fig_yoy = sp.make_subplots(
    rows=4, cols=1,
    subplot_titles=('Industrial Value Added', 'Retail Sales', 'Exports (SA, USD)', 'Total Social Financing'),
)

colors = ['steelblue', 'darkgreen', 'darkred', 'purple']
for i, col in enumerate(['IVA_YoY', 'Retail_YoY', 'Exports_YoY', 'TSF_YoY'], 1):
    fig_yoy.add_trace(
        go.Scatter(x=activity_df.index, y=activity_df[col], name=col.replace('_', ' '),
                   line=dict(color=colors[i-1], width=2), mode='lines+markers'),
        row=i, col=1
    )
    fig_yoy.add_hline(y=0, line_dash='dash', line_color='lightgray', row=i, col=1)

fig_yoy.update_layout(
    title='China: Activity Indicators (YoY %)',
    height=1000,
    width=900,
    hovermode='x unified',
    template='plotly_white',
    showlegend=False
)

cutoff_activity = pd.Timestamp.now() - pd.DateOffset(years=5)
fig_yoy.update_xaxes(range=[cutoff_activity, pd.Timestamp.now()])
activity_visible = activity_df[activity_df.index >= cutoff_activity]
for i, col in enumerate(['IVA_YoY', 'Retail_YoY', 'Exports_YoY', 'TSF_YoY'], 1):
    ymin = activity_visible[col].min()
    ymax = activity_visible[col].max()
    margin = (ymax - ymin) * 0.15
    fig_yoy.update_yaxes(range=[ymin - margin, ymax + margin], row=i, col=1)
fig_yoy.write_image(f'{output_dir}/activity_yoy_chart.png', width=1200, height=1000)
print(f"\nActivity YoY chart saved to {output_dir}/activity_yoy_chart.png")

# Chart 2: Common factor via PCA
activity_for_pca = activity_df[['IVA_YoY', 'Retail_YoY', 'Exports_YoY', 'TSF_YoY']].copy()
activity_for_pca_std = (activity_for_pca - activity_for_pca.mean()) / activity_for_pca.std()

pca_input = activity_for_pca_std.reset_index().rename(columns={'date': 'date'})
result = extract_factor(pca_input)
factor = result['factor']
loadings = result['loadings']

print("\nPCA loadings:")
print(loadings)

fig_factor = go.Figure()
fig_factor.add_trace(
    go.Scatter(x=factor.index, y=factor, name='Common Factor',
               line=dict(color='black', width=2), mode='lines+markers')
)
fig_factor.add_hline(y=0, line_dash='dash', line_color='lightgray')

fig_factor.update_layout(
    title='China: Activity Indicators - Common Factor (PCA)',
    xaxis_title='Date',
    yaxis_title='Factor (standardized)',
    height=500,
    width=900,
    hovermode='x unified',
    template='plotly_white'
)

cutoff_factor = pd.Timestamp.now() - pd.DateOffset(years=5)
factor_visible = factor[factor.index >= cutoff_factor]
fig_factor.update_xaxes(range=[cutoff_factor, pd.Timestamp.now()])
fig_factor.update_yaxes(range=[factor_visible.min() - 0.5, factor_visible.max() + 0.5])
fig_factor.write_image(f'{output_dir}/activity_factor_chart.png', width=1200, height=600)
print(f"Factor chart saved to {output_dir}/activity_factor_chart.png")

# Check what other series have March data (even if not in Apr 15 release)
meta = pd.read_parquet('/workspaces/haver-data/data/metadata.parquet')
china_meta = meta[meta['database'].isin(['emergepr', 'mktpmi'])].copy()
china_meta = china_meta[~china_meta['code'].str.startswith(('h536', 'n536'))]

# Look for series that would cover: IP, Retail, FAI, TSF, Exports, Imports
search_terms = ['industrial', 'retail', 'investment', 'financing', 'export', 'import']
relevant = china_meta[china_meta['descriptor'].str.lower().str.contains('|'.join(search_terms))]

print("\n\nAll China series matching activity indicators:")
print(relevant[['code', 'descriptor', 'frequency', 'enddate']].sort_values('enddate', ascending=False).to_string())
