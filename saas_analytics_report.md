# SaaS Analytics Report

## 1. Executive Summary
- Current recurring revenue is $530 MRR and $6,360 ARR as of 2024-10-01, based on the sample dataset.
- Churn is meaningful but manageable: 33.3% logo churn and 24.3% revenue churn, with the largest losses concentrated in lower-usage accounts.
- Expansion is present but not strong enough to offset churn, yielding NRR of 82.1% and GRR of 73.6%.
- The strongest leading indicators of churn in this sample are low usage, higher support ticket volume, and longer inactivity gaps.
- Payback is healthy at about 2.5 months, but retention needs improvement to support efficient growth.

## 2. Assumptions and Data Quality Notes
- This report uses the sample dataset in [sample_saas_data.csv](sample_saas_data.csv).
- Gross margin was assumed at 70% because no explicit gross margin field was supplied for every account.
- CAC was averaged across available records because the dataset does not include a single uniform acquisition-cost field for every customer.
- The dataset is small (6 accounts), so findings should be treated as directional rather than definitive.

## 3. Metrics Table
| Metric | Value | Benchmark Comparison | Trend |
| --- | ---: | --- | --- |
| MRR | $530 | No external benchmark supplied | Stable but vulnerable to churn |
| ARR | $6,360 | No external benchmark supplied | Stable |
| Logo churn rate | 33.3% | No benchmark supplied | Elevated |
| Revenue churn rate | 24.3% | No benchmark supplied | Elevated |
| NRR | 82.1% | No benchmark supplied | Below healthy growth levels |
| GRR | 73.6% | No benchmark supplied | Weak retention signal |
| LTV | $278.25 | No benchmark supplied | Moderate |
| CAC | $231.67 | No benchmark supplied | Reasonable |
| Payback period | 2.5 months | No benchmark supplied | Healthy |

## 4. Calculation Logic
- ARR = MRR × 12 = $530 × 12 = $6,360
- Logo churn rate = churned customers / total customers = 2 / 6 = 33.3%
- Revenue churn rate = churned MRR / total MRR = $128.8 / $530 = 24.3%
- NRR = (starting MRR + expansion - contraction - churn) / starting MRR = 82.1%
- GRR = (starting MRR - contraction - churn) / starting MRR = 73.6%
- LTV = (ARPU × gross margin) / monthly churn rate; using 70% gross margin and the observed churn level gives approximately $278.25
- Payback period = CAC / (ARPU × gross margin) = 2.5 months

## 5. Key Insights
1. Churn is concentrated in lower-engagement accounts.
   - Churned customers averaged 46.5 usage score versus 83.5 for active customers.
   - Churned accounts also had 4.5 support tickets on average versus 1.0 for active accounts.
2. Inactivity is a strong precursor to loss.
   - Churned accounts averaged 37.5 days since last login versus 4.5 for active customers.
3. Revenue retention is weaker than customer retention.
   - The 24.3% revenue churn rate indicates that the accounts exiting are not trivial accounts; they carry a meaningful portion of revenue.
4. Expansion is not offsetting losses.
   - NRR and GRR both indicate that growth is being constrained by churn and contraction.

## 6. Risks and Red Flags
- The business is losing customers faster than it is replacing them through expansion.
- The sample shows that lower-usage customers are disproportionately at risk.
- Small sample size makes the analysis sensitive to a few accounts.
- Without a richer longitudinal dataset, it is difficult to separate seasonal effects from true retention issues.

## 7. Prioritized Recommendations
1. Target at-risk accounts immediately with re-engagement campaigns.
   - Prioritize customers with low usage, high support volume, or long periods without activity.
2. Tighten onboarding and activation milestones.
   - Focus on the first 30–60 days to ensure users reach core product value quickly.
3. Add a renewal-risk dashboard for the leadership team.
   - Monitor usage score, support tickets, login recency, and plan downgrade signals weekly.
4. Improve expansion plays for healthy accounts.
   - Use upgrade offers and feature adoption nudges to increase expansion MRR.
5. Validate the churn model with a larger, cleaner dataset.
   - Add complete customer lifecycle and product usage history for better forecasting.
