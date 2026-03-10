"""
Business Intelligence Analysis Engine
Handles data analysis, metrics computation, and insight generation
"""

import re
from datetime import datetime, date
from typing import Any, Optional
from collections import defaultdict


def safe_float(val) -> Optional[float]:
    if val is None or val == "":
        return None
    try:
        return float(str(val).replace(",", "").strip())
    except Exception:
        return None


def safe_date(val) -> Optional[date]:
    if not val or str(val).strip() in ("", "None", "null"):
        return None
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y"):
        try:
            return datetime.strptime(str(val).strip(), fmt).date()
        except Exception:
            pass
    return None


def current_quarter() -> tuple:
    today = date.today()
    q = (today.month - 1) // 3 + 1
    year = today.year
    starts = {1: date(year, 1, 1), 2: date(year, 4, 1), 3: date(year, 7, 1), 4: date(year, 10, 1)}
    ends = {1: date(year, 3, 31), 2: date(year, 6, 30), 3: date(year, 9, 30), 4: date(year, 12, 31)}
    return starts[q], ends[q], q, year


class DataAnalyzer:
    def __init__(self, deals: list, work_orders: list):
        self.deals = deals
        self.work_orders = work_orders
        self._deals_columns = self._infer_columns(deals)
        self._wo_columns = self._infer_columns(work_orders)

    def _infer_columns(self, records: list) -> dict:
        """Infer which column keys map to which business concepts"""
        if not records:
            return {}
        all_keys = set()
        for r in records:
            all_keys.update(r.keys())

        mapping = {}
        key_lower = {k: k.lower() for k in all_keys}

        # Revenue / value columns
        for k, kl in key_lower.items():
            if any(x in kl for x in ["revenue", "value", "amount", "deal_value", "contract_value", "arr", "mrr", "price"]):
                mapping.setdefault("value", k)
            if any(x in kl for x in ["sector", "industry", "vertical", "segment"]):
                mapping.setdefault("sector", k)
            if any(x in kl for x in ["stage", "pipeline", "status", "phase"]):
                mapping.setdefault("status", k)
            if any(x in kl for x in ["close_date", "closing", "close", "expected_close", "due_date", "deadline"]):
                mapping.setdefault("close_date", k)
            if any(x in kl for x in ["created", "start", "open_date", "date_created"]):
                mapping.setdefault("start_date", k)
            if any(x in kl for x in ["owner", "rep", "assigned", "account_manager", "sales_rep"]):
                mapping.setdefault("owner", k)
            if any(x in kl for x in ["company", "account", "client", "customer", "contact"]):
                mapping.setdefault("company", k)
            if any(x in kl for x in ["probability", "prob", "likelihood", "confidence"]):
                mapping.setdefault("probability", k)
            if any(x in kl for x in ["budget", "budget_amount"]):
                mapping.setdefault("budget", k)

        return mapping

    def _get(self, record: dict, concept: str, col_map: dict) -> Any:
        key = col_map.get(concept)
        if key:
            return record.get(key)
        return None

    # ─── DEALS ANALYTICS ───────────────────────────────────────────────

    def pipeline_overview(self) -> dict:
        total = len(self.deals)
        total_value = 0.0
        value_count = 0
        status_dist = defaultdict(int)
        sector_dist = defaultdict(float)
        data_quality = {"missing_value": 0, "missing_status": 0, "missing_sector": 0}

        for deal in self.deals:
            val = safe_float(self._get(deal, "value", self._deals_columns))
            status = self._get(deal, "status", self._deals_columns) or deal.get("group", "Unknown")
            sector = self._get(deal, "sector", self._deals_columns) or "Unknown"

            if val is not None:
                total_value += val
                value_count += 1
                if sector != "Unknown":
                    sector_dist[sector] += val
            else:
                data_quality["missing_value"] += 1

            if not status or status == "Unknown":
                data_quality["missing_status"] += 1
            else:
                status_dist[status] += 1

            if not sector or sector == "Unknown":
                data_quality["missing_sector"] += 1

        return {
            "total_deals": total,
            "total_pipeline_value": total_value,
            "deals_with_value": value_count,
            "avg_deal_size": total_value / value_count if value_count else 0,
            "status_distribution": dict(status_dist),
            "sector_distribution": dict(sector_dist),
            "data_quality": data_quality,
        }

    def pipeline_by_sector(self, sector_filter: str = None) -> list:
        sector_data = defaultdict(lambda: {"count": 0, "value": 0.0, "deals": []})

        for deal in self.deals:
            sector = self._get(deal, "sector", self._deals_columns) or deal.get("group", "Unknown")
            val = safe_float(self._get(deal, "value", self._deals_columns)) or 0.0

            if sector_filter:
                if sector_filter.lower() not in sector.lower():
                    continue

            sector_data[sector]["count"] += 1
            sector_data[sector]["value"] += val
            sector_data[sector]["deals"].append(deal.get("name", ""))

        result = []
        for sector, info in sorted(sector_data.items(), key=lambda x: -x[1]["value"]):
            result.append({
                "sector": sector,
                "deal_count": info["count"],
                "total_value": info["value"],
                "deals": info["deals"][:5],  # top 5 deal names
            })
        return result

    def quarterly_pipeline(self, quarter: int = None, year: int = None) -> dict:
        q_start, q_end, cur_q, cur_year = current_quarter()
        if quarter and year:
            starts = {1: date(year, 1, 1), 2: date(year, 4, 1), 3: date(year, 7, 1), 4: date(year, 10, 1)}
            ends = {1: date(year, 3, 31), 2: date(year, 6, 30), 3: date(year, 9, 30), 4: date(year, 12, 31)}
            q_start, q_end = starts.get(quarter, q_start), ends.get(quarter, q_end)
            cur_q, cur_year = quarter, year

        in_quarter = []
        no_date = []
        for deal in self.deals:
            close_raw = self._get(deal, "close_date", self._deals_columns)
            close_dt = safe_date(close_raw)
            if close_dt:
                if q_start <= close_dt <= q_end:
                    in_quarter.append(deal)
            else:
                no_date.append(deal)

        total_val = sum(safe_float(self._get(d, "value", self._deals_columns)) or 0 for d in in_quarter)
        return {
            "quarter": f"Q{cur_q} {cur_year}",
            "q_start": str(q_start),
            "q_end": str(q_end),
            "deals_in_quarter": len(in_quarter),
            "total_value": total_val,
            "deals_without_close_date": len(no_date),
            "deals": [{"name": d.get("name"), "value": safe_float(self._get(d, "value", self._deals_columns))} for d in in_quarter],
        }

    def won_lost_analysis(self) -> dict:
        won, lost, open_deals = [], [], []
        for deal in self.deals:
            status = (self._get(deal, "status", self._deals_columns) or deal.get("group", "")).lower()
            if any(w in status for w in ["won", "closed won", "win"]):
                won.append(deal)
            elif any(l in status for l in ["lost", "closed lost", "lose"]):
                lost.append(deal)
            else:
                open_deals.append(deal)

        won_val = sum(safe_float(self._get(d, "value", self._deals_columns)) or 0 for d in won)
        lost_val = sum(safe_float(self._get(d, "value", self._deals_columns)) or 0 for d in lost)

        total = len(won) + len(lost)
        win_rate = (len(won) / total * 100) if total else 0

        return {
            "won_count": len(won),
            "lost_count": len(lost),
            "open_count": len(open_deals),
            "won_value": won_val,
            "lost_value": lost_val,
            "win_rate_pct": win_rate,
        }

    def top_deals(self, n: int = 10, sector: str = None) -> list:
        filtered = self.deals
        if sector:
            filtered = [d for d in self.deals if sector.lower() in (self._get(d, "sector", self._deals_columns) or "").lower()]
        scored = []
        for d in filtered:
            val = safe_float(self._get(d, "value", self._deals_columns)) or 0
            scored.append((val, d))
        scored.sort(key=lambda x: -x[0])
        result = []
        for val, d in scored[:n]:
            result.append({
                "name": d.get("name", ""),
                "value": val,
                "status": self._get(d, "status", self._deals_columns) or d.get("group", ""),
                "sector": self._get(d, "sector", self._deals_columns) or "",
                "close_date": self._get(d, "close_date", self._deals_columns) or "",
                "owner": self._get(d, "owner", self._deals_columns) or "",
            })
        return result

    # ─── WORK ORDER ANALYTICS ──────────────────────────────────────────

    def work_order_overview(self) -> dict:
        total = len(self.work_orders)
        status_dist = defaultdict(int)
        sector_dist = defaultdict(int)
        value_sum = 0.0
        value_count = 0
        data_quality = {"missing_value": 0, "missing_status": 0}

        for wo in self.work_orders:
            status = self._get(wo, "status", self._wo_columns) or wo.get("group", "Unknown")
            sector = self._get(wo, "sector", self._wo_columns) or "Unknown"
            val = safe_float(self._get(wo, "value", self._wo_columns))

            if not status or status == "Unknown":
                data_quality["missing_status"] += 1
            else:
                status_dist[status] += 1

            sector_dist[sector] += 1

            if val is not None:
                value_sum += val
                value_count += 1
            else:
                data_quality["missing_value"] += 1

        return {
            "total_work_orders": total,
            "status_distribution": dict(status_dist),
            "sector_distribution": dict(sector_dist),
            "total_contract_value": value_sum,
            "work_orders_with_value": value_count,
            "data_quality": data_quality,
        }

    def work_order_by_sector(self) -> list:
        sector_data = defaultdict(lambda: {"count": 0, "value": 0.0, "statuses": defaultdict(int)})

        for wo in self.work_orders:
            sector = self._get(wo, "sector", self._wo_columns) or wo.get("group", "Unknown")
            val = safe_float(self._get(wo, "value", self._wo_columns)) or 0.0
            status = self._get(wo, "status", self._wo_columns) or wo.get("group", "Unknown")

            sector_data[sector]["count"] += 1
            sector_data[sector]["value"] += val
            sector_data[sector]["statuses"][status] += 1

        result = []
        for sector, info in sorted(sector_data.items(), key=lambda x: -x[1]["count"]):
            result.append({
                "sector": sector,
                "count": info["count"],
                "total_value": info["value"],
                "status_breakdown": dict(info["statuses"]),
            })
        return result

    def operational_health(self) -> dict:
        on_time, delayed, no_date = 0, 0, 0
        today = date.today()

        active_statuses = ["in progress", "active", "open", "in_progress", "in-progress", "started"]
        complete_statuses = ["done", "complete", "completed", "closed", "finished", "delivered"]

        for wo in self.work_orders:
            status = (self._get(wo, "status", self._wo_columns) or wo.get("group", "")).lower()
            due_raw = self._get(wo, "close_date", self._wo_columns)
            due_dt = safe_date(due_raw)

            if any(s in status for s in complete_statuses):
                continue  # Exclude completed

            if due_dt:
                if due_dt < today:
                    delayed += 1
                else:
                    on_time += 1
            else:
                no_date += 1

        active_total = on_time + delayed + no_date
        return {
            "active_work_orders": active_total,
            "on_track": on_time,
            "overdue": delayed,
            "no_due_date": no_date,
            "overdue_pct": (delayed / active_total * 100) if active_total else 0,
        }

    # ─── CROSS-BOARD ANALYTICS ─────────────────────────────────────────

    def sector_360(self, sector: str = None) -> dict:
        """Cross-board sector analysis"""
        deals_by_sector = {s["sector"]: s for s in self.pipeline_by_sector(sector)}
        wo_by_sector = {s["sector"]: s for s in self.work_order_by_sector()}

        if sector:
            all_sectors = {sector}
        else:
            all_sectors = set(deals_by_sector.keys()) | set(wo_by_sector.keys())

        result = {}
        for s in all_sectors:
            result[s] = {
                "pipeline": deals_by_sector.get(s, {"deal_count": 0, "total_value": 0}),
                "operations": wo_by_sector.get(s, {"count": 0, "total_value": 0}),
            }
        return result

    def get_column_map_summary(self) -> dict:
        return {
            "deals_columns_detected": self._deals_columns,
            "work_order_columns_detected": self._wo_columns,
        }

    def data_quality_report(self) -> dict:
        deals_ov = self.pipeline_overview()
        wo_ov = self.work_order_overview()

        total_deals = deals_ov["total_deals"]
        total_wo = wo_ov["total_work_orders"]

        return {
            "deals": {
                "total": total_deals,
                "missing_value_pct": round(deals_ov["data_quality"]["missing_value"] / max(total_deals, 1) * 100, 1),
                "missing_status_pct": round(deals_ov["data_quality"]["missing_status"] / max(total_deals, 1) * 100, 1),
                "missing_sector_pct": round(deals_ov["data_quality"]["missing_sector"] / max(total_deals, 1) * 100, 1),
            },
            "work_orders": {
                "total": total_wo,
                "missing_value_pct": round(wo_ov["data_quality"]["missing_value"] / max(total_wo, 1) * 100, 1),
                "missing_status_pct": round(wo_ov["data_quality"]["missing_status"] / max(total_wo, 1) * 100, 1),
            },
        }
