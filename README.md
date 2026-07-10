# SaaS Analytics Workspace

This workspace includes a simple analytics workflow for SaaS subscription data.

## Features
- Analyze SaaS CSV data to calculate MRR, ARR, churn, NRR, GRR, LTV, CAC, and payback
- Generate cohort retention output and a markdown report
- Serve a polished web dashboard locally
- Include goals, OKR, review, and executive scorecard templates

## Files
- [analyze_saas.py](analyze_saas.py) — analyze CSV data and generate outputs
- [app.py](app.py) — Flask dashboard
- [sample_saas_data.csv](sample_saas_data.csv) — example dataset
- [saas_metrics.json](saas_metrics.json) — generated metrics output
- [cohort_retention.csv](cohort_retention.csv) — generated cohort retention output
- [saas_report.md](saas_report.md) — generated markdown report
- [goals_loop.md](goals_loop.md) — repeatable goals-and-review loop
- [weekly_okrs.md](weekly_okrs.md) — weekly OKR-style goals
- [dashboard_template.md](dashboard_template.md) — dashboard template
- [executive_scorecard.md](executive_scorecard.md) — one-page executive scorecard
- [weekly_review_template.md](weekly_review_template.md) — weekly review template
- [example_workflow.md](example_workflow.md) — example workflow for recurring reviews
- [test_analyze_saas.py](test_analyze_saas.py) — regression test

## Run locally
```powershell
cd /d "e:\web peojects\saas analytics"
& "e:/web peojects/saas analytics/.venv/Scripts/python.exe" analyze_saas.py sample_saas_data.csv --as-of-date 2024-10-01 --output-dir .
```

```powershell
cd /d "e:\web peojects\saas analytics"
& "e:/web peojects/saas analytics/.venv/Scripts/python.exe" app.py
```

Then open http://127.0.0.1:5000.

## Deploy to GitHub
1. Create a new repository on GitHub.
2. In the project folder, run:
   ```powershell
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin <your-github-repo-url>
   git push -u origin main
   ```
