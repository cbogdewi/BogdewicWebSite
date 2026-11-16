#!/usr/bin/env python3
"""Fetch, validate, transform, and summarize FEMA disaster declarations."""

from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen
import json
import time

API_URL = "https://www.fema.gov/api/open/v2/DisasterDeclarationsSummaries"
OUTPUT = Path("data/fema-disasters.json")
PAGE_SIZE = 1000
FIELDS = ",".join((
    "disasterNumber", "state", "declarationDate", "incidentType",
    "declarationTitle", "designatedArea", "fyDeclared", "ihProgramDeclared",
    "iaProgramDeclared", "paProgramDeclared", "hmProgramDeclared",
))


def fetch_page(offset):
    params = {"$select": FIELDS, "$orderby": "declarationDate desc", "$top": PAGE_SIZE, "$skip": offset}
    url = f"{API_URL}?{urlencode(params)}"
    request = Request(url, headers={"Accept": "application/json", "User-Agent": "BogdewicPortfolioETL/1.0"})
    for attempt in range(4):
        try:
            with urlopen(request, timeout=60) as response:
                payload = json.load(response)
            rows = payload.get("DisasterDeclarationsSummaries")
            if not isinstance(rows, list):
                raise ValueError("FEMA response did not contain a DisasterDeclarationsSummaries list")
            return rows
        except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as error:
            if attempt == 3:
                raise RuntimeError(f"FEMA API request failed at offset {offset}: {error}") from error
            time.sleep(2 ** attempt)
    return []


def clean_text(value):
    return value.strip() if isinstance(value, str) else ""


def transform(rows):
    records = {}
    rejected = 0
    for row in rows:
        number = row.get("disasterNumber")
        state = clean_text(row.get("state"))
        date = clean_text(row.get("declarationDate"))
        if number is None or not state or not date:
            rejected += 1
            continue
        try:
            datetime.fromisoformat(date.replace("Z", "+00:00"))
        except ValueError:
            rejected += 1
            continue
        key = str(number)
        records[key] = {
            "disasterNumber": number,
            "state": state,
            "declarationDate": date,
            "incidentType": clean_text(row.get("incidentType")) or "Unknown",
            "declarationTitle": clean_text(row.get("declarationTitle")) or "Untitled declaration",
            "designatedArea": clean_text(row.get("designatedArea")),
            "fyDeclared": row.get("fyDeclared"),
            "programs": {
                "individualAssistance": row.get("ihProgramDeclared") is True,
                "publicAssistance": row.get("paProgramDeclared") is True,
                "hazardMitigation": row.get("hmProgramDeclared") is True,
            },
        }
    return list(records.values()), rejected


def main():
    raw_rows = []
    offset = 0
    while True:
        page = fetch_page(offset)
        raw_rows.extend(page)
        print(f"Fetched {len(page)} records at offset {offset}")
        if len(page) < PAGE_SIZE:
            break
        offset += PAGE_SIZE

    records, rejected = transform(raw_rows)
    if not records:
        raise RuntimeError("No valid FEMA declaration records were returned; refusing to publish empty output")

    by_state = Counter(row["state"] for row in records)
    by_type = Counter(row["incidentType"] for row in records)
    by_year = Counter(row["declarationDate"][:4] for row in records)
    records.sort(key=lambda row: row["declarationDate"], reverse=True)
    output = {
        "source": API_URL,
        "dataset": "FEMA Disaster Declarations Summaries (OpenFEMA API v2)",
        "generatedAt": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "recordCount": len(records),
        "rejectedCount": rejected,
        "states": [{"name": name, "count": count} for name, count in by_state.most_common()],
        "incidentTypes": [{"name": name, "count": count} for name, count in by_type.most_common()],
        "declarationYears": [{"year": name, "count": count} for name, count in sorted(by_year.items(), reverse=True)],
        "latest": records[:20],
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(output, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {len(records)} unique valid declarations; rejected {rejected}; output: {OUTPUT}")


if __name__ == "__main__":
    main()
