import argparse
import csv
import json
import statistics
from collections import defaultdict
from datetime import datetime, date
from pathlib import Path
from typing import Dict, List, Optional


DATE_FORMATS = ("%Y-%m-%d", "%m/%d/%Y", "%Y/%m/%d", "%Y-%m-%d %H:%M:%S")


def parse_date(value: Optional[str]) -> Optional[date]:
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            continue
    return None


def parse_float(value: Optional[str]) -> Optional[float]:
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    try:
        return float(text.replace(",", ""))
    except ValueError:
        return None


def load_records(path: Path) -> List[Dict[str, object]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        records = []
        for idx, row in enumerate(reader, start=1):
            customer_id = row.get("customer_id") or row.get("account_id") or row.get("customer") or f"row_{idx}"
            signup_date = parse_date(row.get("signup_date") or row.get("signup") or row.get("created_at") or row.get("joined_at"))
            churn_date = parse_date(row.get("churn_date") or row.get("canceled_at") or row.get("cancelled_at") or row.get("ended_at"))

            mrr = parse_float(row.get("mrr") or row.get("monthly_revenue") or row.get("monthly_mrr"))
            if mrr is None:
                arr = parse_float(row.get("arr") or row.get("annual_revenue"))
                if arr is not None:
                    mrr = arr / 12.0

            plan = row.get("plan") or row.get("tier") or ""
            acquisition_channel = row.get("acquisition_channel") or row.get("channel") or row.get("acquired_by") or ""

            expansion_mrr = parse_float(row.get("expansion_mrr") or row.get("upsell_mrr") or row.get("expansion"))
            contraction_mrr = parse_float(row.get("contraction_mrr") or row.get("downgrade_mrr") or row.get("contraction"))
            gross_margin_pct = parse_float(row.get("gross_margin_pct") or row.get("gross_margin"))
            cac = parse_float(row.get("cac") or row.get("customer_acquisition_cost") or row.get("acquisition_cost"))
            usage_score = parse_float(row.get("usage_score") or row.get("engagement_score"))
            support_tickets = parse_float(row.get("support_tickets") or row.get("ticket_count"))
            days_since_last_login = parse_float(row.get("days_since_last_login") or row.get("days_since_last_activity"))

            records.append(
                {
                    "customer_id": customer_id,
                    "signup_date": signup_date,
                    "churn_date": churn_date,
                    "mrr": mrr,
                    "plan": plan,
                    "acquisition_channel": acquisition_channel,
                    "expansion_mrr": expansion_mrr,
                    "contraction_mrr": contraction_mrr,
                    "gross_margin_pct": gross_margin_pct,
                    "cac": cac,
                    "usage_score": usage_score,
                    "support_tickets": support_tickets,
                    "days_since_last_login": days_since_last_login,
                }
            )
    return records


def summarize_data_quality(records: List[Dict[str, object]]) -> Dict[str, object]:
    customer_ids = [r["customer_id"] for r in records if r["customer_id"] is not None]
    duplicate_customer_ids = len(customer_ids) - len(set(customer_ids))
    missing_signup_date_count = sum(1 for r in records if r["signup_date"] is None)
    missing_mrr_count = sum(1 for r in records if r["mrr"] is None)

    mrr_values = [r["mrr"] for r in records if r["mrr"] is not None]
    median_mrr = statistics.median(mrr_values) if mrr_values else None
    outlier_mrr_count = 0
    if median_mrr is not None:
        outlier_threshold = max(1.0, median_mrr * 3.0)
        outlier_mrr_count = sum(1 for value in mrr_values if value is not None and value > outlier_threshold)

    return {
        "total_rows": len(records),
        "missing_signup_date_count": missing_signup_date_count,
        "missing_mrr_count": missing_mrr_count,
        "duplicate_customer_ids_count": duplicate_customer_ids,
        "outlier_mrr_count": outlier_mrr_count,
    }


def build_metrics(records: List[Dict[str, object]], as_of_date: date) -> Dict[str, object]:
    data_quality = summarize_data_quality(records)
    active = [r for r in records if r["mrr"] is not None and r["mrr"] > 0 and (r["churn_date"] is None or r["churn_date"] > as_of_date)]
    churned = [r for r in records if r["churn_date"] is not None and r["churn_date"] <= as_of_date]
    total_customers = len(records)
    total_mrr = sum(r["mrr"] or 0 for r in records if r["mrr"] is not None)
    current_mrr = sum(r["mrr"] or 0 for r in active)
    current_arr = current_mrr * 12.0

    logo_churn_rate = len(churned) / total_customers if total_customers else 0.0
    revenue_churn_rate = sum(r["mrr"] or 0 for r in churned) / total_mrr if total_mrr else 0.0

    gross_margin_pct = next((r["gross_margin_pct"] for r in records if r["gross_margin_pct"] is not None), None)
    if gross_margin_pct is None:
        gross_margin_pct = 0.70

    arpu = current_mrr / len(active) if active else 0.0
    monthly_churn_rate = logo_churn_rate
    ltv = (arpu * gross_margin_pct / monthly_churn_rate) if monthly_churn_rate > 0 else None

    cac_values = [r["cac"] for r in records if r["cac"] is not None]
    cac = sum(cac_values) / len(cac_values) if cac_values else None
    payback_period_months = None
    if cac is not None and arpu > 0:
        payback_period_months = cac / (arpu * gross_margin_pct) if (arpu * gross_margin_pct) > 0 else None

    expansion_mrr = sum(r["expansion_mrr"] or 0 for r in records if r["expansion_mrr"] is not None)
    contraction_mrr = sum(r["contraction_mrr"] or 0 for r in records if r["contraction_mrr"] is not None)
    churn_mrr = sum(r["mrr"] or 0 for r in churned)

    nrr = None
    grr = None
    if total_mrr > 0:
        nrr = ((total_mrr + expansion_mrr - contraction_mrr - churn_mrr) / total_mrr) if (expansion_mrr or contraction_mrr or churn_mrr) else None
        grr = ((total_mrr - contraction_mrr - churn_mrr) / total_mrr) if (contraction_mrr or churn_mrr) else None

    lead_indicators = {
        "avg_usage_score_churned": round(sum(r["usage_score"] or 0 for r in churned) / len(churned), 2) if churned else None,
        "avg_usage_score_active": round(sum(r["usage_score"] or 0 for r in active) / len(active), 2) if active else None,
        "avg_support_tickets_churned": round(sum(r["support_tickets"] or 0 for r in churned) / len(churned), 2) if churned else None,
        "avg_support_tickets_active": round(sum(r["support_tickets"] or 0 for r in active) / len(active), 2) if active else None,
        "avg_days_since_last_login_churned": round(sum(r["days_since_last_login"] or 0 for r in churned) / len(churned), 2) if churned else None,
        "avg_days_since_last_login_active": round(sum(r["days_since_last_login"] or 0 for r in active) / len(active), 2) if active else None,
    }

    return {
        "as_of_date": as_of_date.strftime("%Y-%m-%d"),
        "data_quality": data_quality,
        "customers_total": total_customers,
        "customers_active": len(active),
        "customers_churned": len(churned),
        "mrr": round(current_mrr, 2),
        "arr": round(current_arr, 2),
        "logo_churn_rate": round(logo_churn_rate * 100, 2),
        "revenue_churn_rate": round(revenue_churn_rate * 100, 2),
        "nrr": round(nrr * 100, 2) if nrr is not None else None,
        "grr": round(grr * 100, 2) if grr is not None else None,
        "ltv": round(ltv, 2) if ltv is not None else None,
        "cac": round(cac, 2) if cac is not None else None,
        "payback_period_months": round(payback_period_months, 2) if payback_period_months is not None else None,
        "lead_indicators": lead_indicators,
    }


def build_cohort_retention(records: List[Dict[str, object]], as_of_date: date) -> List[Dict[str, object]]:
    cohorts: Dict[str, List[Dict[str, object]]] = defaultdict(list)
    for record in records:
        signup_date = record["signup_date"]
        if signup_date is None:
            continue
        cohort_key = signup_date.strftime("%Y-%m")
        cohorts[cohort_key].append(record)

    output = []
    for cohort_key in sorted(cohorts):
        cohort_records = cohorts[cohort_key]
        initial_size = len(cohort_records)
        if initial_size == 0:
            continue
        for month_index in range(0, 13):
            month_date = date(as_of_date.year, as_of_date.month, 1)
            # monthly retention is measured relative to the cohort's start month
            cohort_month = datetime.strptime(cohort_key + "-01", "%Y-%m-%d").date()
            target_date = (datetime(cohort_month.year + (cohort_month.month - 1 + month_index) // 12,
                                    ((cohort_month.month - 1 + month_index) % 12) + 1,
                                    1)).date()
            alive = 0
            for record in cohort_records:
                signup_date = record["signup_date"]
                churn_date = record["churn_date"]
                if signup_date is None:
                    continue
                if churn_date is None or churn_date >= target_date:
                    alive += 1
            if month_index == 0:
                retention = 100.0
            else:
                retention = round((alive / initial_size) * 100, 2) if initial_size else 0.0
            output.append({"cohort": cohort_key, "month_since_signup": month_index, "active_customers": alive, "retention_pct": retention})
    return output


def build_markdown_report(metrics: Dict[str, object], cohort_data: List[Dict[str, object]]) -> str:
    lead_indicators = metrics.get("lead_indicators", {})
    lines = []
    lines.append("# SaaS Analytics Report")
    lines.append("")
    lines.append("## Executive Summary")
    lines.append(f"- MRR is ${metrics['mrr']:,.0f} and ARR is ${metrics['arr']:,.0f} as of {metrics['as_of_date']}.")
    lines.append(f"- Logo churn is {metrics['logo_churn_rate']}% and revenue churn is {metrics['revenue_churn_rate']}%.")
    lines.append(f"- NRR is {metrics['nrr']}% and GRR is {metrics['grr']}%.")
    lines.append(f"- Churned accounts show lower average usage ({lead_indicators.get('avg_usage_score_churned')}) than active accounts ({lead_indicators.get('avg_usage_score_active')}).")
    lines.append(f"- Payback period is {metrics['payback_period_months']} months based on the available CAC and ARPU assumptions.")
    lines.append("")
    lines.append("## Data Quality")
    data_quality = metrics.get("data_quality", {})
    lines.append(f"- Total rows: {data_quality.get('total_rows', 0)}")
    lines.append(f"- Missing signup dates: {data_quality.get('missing_signup_date_count', 0)}")
    lines.append(f"- Missing MRR: {data_quality.get('missing_mrr_count', 0)}")
    lines.append(f"- Duplicate customer IDs: {data_quality.get('duplicate_customer_ids_count', 0)}")
    lines.append(f"- Outlier MRR records: {data_quality.get('outlier_mrr_count', 0)}")
    lines.append("")
    lines.append("## Metrics")
    lines.append("| Metric | Value |")
    lines.append("| --- | ---: |")
    lines.append(f"| MRR | ${metrics['mrr']:,.2f} |")
    lines.append(f"| ARR | ${metrics['arr']:,.2f} |")
    lines.append(f"| Logo churn rate | {metrics['logo_churn_rate']}% |")
    lines.append(f"| Revenue churn rate | {metrics['revenue_churn_rate']}% |")
    lines.append(f"| NRR | {metrics['nrr']}% |")
    lines.append(f"| GRR | {metrics['grr']}% |")
    lines.append(f"| LTV | ${metrics['ltv']:,.2f} |")
    lines.append(f"| CAC | ${metrics['cac']:,.2f} |")
    lines.append(f"| Payback period | {metrics['payback_period_months']} months |")
    lines.append("")
    lines.append("## Cohort Retention Snapshot")
    lines.append("| Cohort | Month 0 | Month 1 | Month 2 |")
    lines.append("| --- | ---: | ---: | ---: |")
    cohort_map = defaultdict(dict)
    for row in cohort_data:
        cohort_map[row["cohort"]][row["month_since_signup"]] = row["retention_pct"]
    for cohort_key in sorted(cohort_map):
        month0 = cohort_map[cohort_key].get(0, "")
        month1 = cohort_map[cohort_key].get(1, "")
        month2 = cohort_map[cohort_key].get(2, "")
        lines.append(f"| {cohort_key} | {month0} | {month1} | {month2} |")
    return "\n".join(lines) + "\n"


def write_outputs(metrics: Dict[str, object], cohort_data: List[Dict[str, object]], output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    with (output_dir / "saas_metrics.json").open("w", encoding="utf-8") as handle:
        json.dump(metrics, handle, indent=2)
    with (output_dir / "cohort_retention.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["cohort", "month_since_signup", "active_customers", "retention_pct"])
        writer.writeheader()
        writer.writerows(cohort_data)
    with (output_dir / "saas_report.md").open("w", encoding="utf-8") as handle:
        handle.write(build_markdown_report(metrics, cohort_data))


def main() -> None:
    parser = argparse.ArgumentParser(description="Analyze SaaS subscription data")
    parser.add_argument("input_csv", type=Path, help="Path to the input CSV file")
    parser.add_argument("--as-of-date", default=date.today().strftime("%Y-%m-%d"), help="Reference date for churn and cohort analysis")
    parser.add_argument("--output-dir", default=".", type=Path, help="Directory for JSON/CSV outputs")
    args = parser.parse_args()

    as_of_date = parse_date(args.as_of_date) or date.today()
    records = load_records(args.input_csv)
    metrics = build_metrics(records, as_of_date)
    cohort_data = build_cohort_retention(records, as_of_date)
    write_outputs(metrics, cohort_data, args.output_dir)

    print(json.dumps(metrics, indent=2))
    print(f"\nWrote outputs to {args.output_dir}")


if __name__ == "__main__":
    main()
