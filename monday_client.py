"""
Monday.com API Client
Handles all communication with Monday.com GraphQL API (2024-01)
"""

import requests
import json
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import re
from datetime import datetime
from typing import Optional


class MondayClient:
    API_URL = "https://api.monday.com/v2"

    def __init__(self, api_token: str):
        self.api_token = api_token.strip()
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": self.api_token,
            "API-Version": "2024-01",
        }
        self._board_cache = {}
        self._items_cache = {}

    def _run_query(self, query: str, variables: dict = None) -> dict:
        payload = {"query": query}
        if variables:
            payload["variables"] = variables
        try:
            resp = requests.post(
                self.API_URL,
                headers=self.headers,
                json=payload,
                timeout=30,
                verify=False,
            )
            if not resp.ok:
                raise ConnectionError(
                    f"HTTP {resp.status_code}: {resp.text[:400]}"
                )
            result = resp.json()
            if "errors" in result:
                raise ValueError(f"GraphQL errors: {result['errors']}")
            return result.get("data", {})
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Monday.com API request failed: {e}")

    def test_connection(self) -> tuple:
        """Returns (success: bool, message: str)"""
        try:
            data = self._run_query("{ me { name email } }")
            if "me" in data and data["me"]:
                name = data["me"].get("name", "")
                email = data["me"].get("email", "")
                return True, f"Connected as {name} ({email})"
            return False, "API responded but returned no user data. Check token permissions."
        except ConnectionError as e:
            return False, str(e)
        except Exception as e:
            return False, f"Unexpected error: {e}"

    def get_board_info(self, board_id: str) -> dict:
        if board_id in self._board_cache:
            return self._board_cache[board_id]
        query = """
        query ($boardId: [ID!]) {
          boards(ids: $boardId) {
            id name description
            columns { id title type settings_str }
            groups { id title }
          }
        }
        """
        data = self._run_query(query, {"boardId": [board_id]})
        boards = data.get("boards", [])
        if not boards:
            raise ValueError(f"Board {board_id} not found or not accessible")
        self._board_cache[board_id] = boards[0]
        return boards[0]

    def get_all_items(self, board_id: str, limit: int = 200) -> list:
        """Fetch all items using cursor-based pagination (Monday.com 2024-01)"""
        if board_id in self._items_cache:
            return self._items_cache[board_id]

        all_items = []

        # First page
        first_query = """
        query ($boardId: ID!, $limit: Int!) {
          boards(ids: [$boardId]) {
            items_page(limit: $limit) {
              cursor
              items {
                id name
                group { id title }
                column_values { id text value column { title type } }
              }
            }
          }
        }
        """
        data = self._run_query(first_query, {"boardId": board_id, "limit": limit})
        boards = data.get("boards", [])
        if not boards:
            return []

        page = boards[0].get("items_page", {})
        items = page.get("items", [])
        all_items.extend(items)
        cursor = page.get("cursor")

        # Subsequent pages using next_items_page
        while cursor and items:
            next_query = """
            query ($limit: Int!, $cursor: String!) {
              next_items_page(limit: $limit, cursor: $cursor) {
                cursor
                items {
                  id name
                  group { id title }
                  column_values { id text value column { title type } }
                }
              }
            }
            """
            data = self._run_query(next_query, {"limit": limit, "cursor": cursor})
            page = data.get("next_items_page", {})
            items = page.get("items", [])
            all_items.extend(items)
            cursor = page.get("cursor")

        self._items_cache[board_id] = all_items
        return all_items

    def clear_cache(self):
        self._board_cache = {}
        self._items_cache = {}


class DataProcessor:
    """Cleans and normalizes raw Monday.com data"""

    @staticmethod
    def parse_date(raw: str) -> Optional[str]:
        if not raw or str(raw).strip() in ("", "null", "None"):
            return None
        raw = str(raw).strip().strip('"')

        try:
            parsed = json.loads(raw)
            if isinstance(parsed, dict):
                raw = parsed.get("date", raw)
        except Exception:
            pass

        formats = [
            "%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y",
            "%d-%m-%Y", "%m-%d-%Y", "%Y/%m/%d",
            "%d %b %Y", "%d %B %Y", "%b %d, %Y",
        ]
        for fmt in formats:
            try:
                return datetime.strptime(raw, fmt).strftime("%Y-%m-%d")
            except Exception:
                pass
        return raw

    @staticmethod
    def parse_number(raw: str) -> Optional[float]:
        if not raw or str(raw).strip() in ("", "null", "None", "-"):
            return None
        cleaned = re.sub(r"[^\d.\-]", "", str(raw).replace(",", ""))
        try:
            return float(cleaned)
        except Exception:
            return None

    @staticmethod
    def normalize_status(raw: str) -> str:
        if not raw or str(raw).strip() in ("", "null", "None"):
            return "Unknown"
        try:
            parsed = json.loads(raw)
            if isinstance(parsed, dict):
                raw = parsed.get("label", raw)
        except Exception:
            pass
        return str(raw).strip()

    @staticmethod
    def item_to_dict(item: dict) -> dict:
        record = {
            "id": item.get("id", ""),
            "name": item.get("name", "").strip(),
            "group": item.get("group", {}).get("title", "") if item.get("group") else "",
        }
        for cv in item.get("column_values", []):
            col_title = cv.get("column", {}).get("title", cv.get("id", ""))
            col_type = cv.get("column", {}).get("type", "")
            text_val = cv.get("text", "") or ""
            value_raw = cv.get("value", "") or ""

            key = col_title.lower()
            key = re.sub(r"[^a-z0-9]+", "_", key).strip("_")

            if col_type in ("numeric", "numbers"):
                record[key] = DataProcessor.parse_number(text_val or value_raw)
            elif col_type in ("date", "timeline"):
                record[key] = DataProcessor.parse_date(text_val or value_raw)
            elif col_type in ("status", "color"):
                record[key] = DataProcessor.normalize_status(text_val or value_raw)
            else:
                val = text_val
                if not val and value_raw:
                    try:
                        parsed = json.loads(value_raw)
                        if isinstance(parsed, dict):
                            val = parsed.get("text") or parsed.get("label") or str(parsed)
                        else:
                            val = str(parsed)
                    except Exception:
                        val = value_raw
                record[key] = val.strip() if val else ""

        return record

    @staticmethod
    def process_board_items(items: list) -> list:
        return [DataProcessor.item_to_dict(item) for item in items]
