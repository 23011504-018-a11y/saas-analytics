import json
from pathlib import Path
import pandas as pd
import plotly.express as px
from flask import Flask, render_template_string

app = Flask(__name__, static_folder="static")
ROOT = Path(__file__).resolve().parent
METRICS_PATH = ROOT / "saas_metrics.json"
COHORT_PATH = ROOT / "cohort_retention.csv"

HTML_TEMPLATE = """
<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <title>SaaS Analytics Dashboard</title>
  <link rel="stylesheet" href="/static/styles.css">
  <script src="https://cdn.plot.ly/plotly-1.58.5.min.js"></script>
</head>
<body>
  <div class="container">
    <div class="hero">
      <div>
        <h1>SaaS Analytics Dashboard</h1>
        <div class="subtitle">A polished view of retention, growth, and churn metrics.</div>
      </div>
      <div class="badge">Live from the latest analysis</div>
    </div>

    <div class="showcase">
      <div class="pulse-card">
        <div class="score-ring" style="--score: {{ health_score }}%;">
          <div class="ring-inner">
            <span class="ring-value">{{ health_score }}</span>
            <span class="ring-label">health</span>
          </div>
        </div>
        <div class="pulse-copy">
          <div class="eyebrow">Northstar Pulse</div>
          <h2>{{ health_label }}</h2>
          <p>Balanced momentum with strong revenue potential, but retention deserves immediate attention.</p>
          <div class="signal-row">
            <span class="signal-pill">Growth: {{ mrr_display }}</span>
            <span class="signal-pill">Retention: {{ logo_churn_display }}</span>
          </div>
        </div>
      </div>
    </div>

    <div class="grid">
      <div class="metric"><h3>MRR</h3><div class="value">{{ mrr_display }}</div></div>
      <div class="metric"><h3>ARR</h3><div class="value">{{ arr_display }}</div></div>
      <div class="metric"><h3>Logo Churn</h3><div class="value">{{ logo_churn_display }}</div></div>
      <div class="metric"><h3>Revenue Churn</h3><div class="value">{{ revenue_churn_display }}</div></div>
      <div class="metric"><h3>NNR</h3><div class="value">{{ nrr_display }}</div></div>
      <div class="metric"><h3>GRR</h3><div class="value">{{ grr_display }}</div></div>
    </div>

    <div class="card">
      <h2>Cohort Retention</h2>
      <p>How customer retention evolves after signup across each cohort.</p>
      <div class="chart-shell">
        <div id="cohort-chart"></div>
      </div>
    </div>

    <div class="card table-card">
      <h2>Executive Summary</h2>
      <table>
        <thead>
          <tr>
            <th>Focus area</th>
            <th>Current status</th>
            <th>Signal</th>
          </tr>
        </thead>
        <tbody>
          <tr><td>Growth</td><td>Steady</td><td>MRR and ARR are positive.</td></tr>
          <tr><td>Retention</td><td>Needs attention</td><td>Logo and revenue churn are material.</td></tr>
          <tr><td>Expansion</td><td>Moderate</td><td>NNR and GRR indicate room to improve.</td></tr>
        </tbody>
      </table>
    </div>
  </div>

  <script>
    var data = {{ plotly_data_json|safe }};
    Plotly.newPlot('cohort-chart', data.data, data.layout, {responsive: true});
  </script>
</body>
</html>
"""


@app.route("/")
def index():
    metrics = json.loads(METRICS_PATH.read_text(encoding="utf-8"))
    cohort_df = pd.read_csv(COHORT_PATH)
    fig = px.line(
        cohort_df,
        x="month_since_signup",
        y="retention_pct",
        color="cohort",
        markers=True,
        title="Cohort Retention by Month Since Signup",
    )
    fig.update_layout(template="plotly_white", margin=dict(l=30, r=20, t=50, b=20))
    plotly_data = fig.to_plotly_json()
    plotly_data_json = json.dumps(plotly_data)

    mrr_display = f"${metrics.get('mrr', 0):,.0f}"
    arr_display = f"${metrics.get('arr', 0):,.0f}"
    logo_churn_display = f"{metrics.get('logo_churn_rate', 0):.1f}%"
    revenue_churn_display = f"{metrics.get('revenue_churn_rate', 0):.1f}%"
    nrr_display = f"{metrics.get('nrr', 0):.1f}%"
    grr_display = f"{metrics.get('grr', 0):.1f}%"

    health_score = max(0, min(100, round(100 - metrics.get('logo_churn_rate', 0) * 0.8 - metrics.get('revenue_churn_rate', 0) * 0.5 + metrics.get('nrr', 0) * 0.1)))
    health_label = "Thriving" if health_score >= 80 else "Steady" if health_score >= 65 else "Watch"

    return render_template_string(
        HTML_TEMPLATE,
        mrr_display=mrr_display,
        arr_display=arr_display,
        logo_churn_display=logo_churn_display,
        revenue_churn_display=revenue_churn_display,
        nrr_display=nrr_display,
        grr_display=grr_display,
        health_score=health_score,
        health_label=health_label,
        plotly_data_json=plotly_data_json,
    )


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
