#!/usr/bin/env python3
"""
Descarga el histórico oficial de Mega Millions y Powerball (Texas Lottery),
calcula frecuencias y pares concurrentes, y escribe stats.json para el
dashboard estático. Pensado para correr en GitHub Actions a diario.

    python3 build_stats.py
"""

import csv
import io
import json
import urllib.request
from collections import Counter
from datetime import date, datetime, timezone
from itertools import combinations
from pathlib import Path

HERE = Path(__file__).parent

GAMES = {
    "megamillions": {
        "label": "Mega Millions",
        "url": "https://www.texaslottery.com/export/sites/lottery/Games/Mega_Millions/Winning_Numbers/megamillions.csv",
        "white_max": 70,
        "special_max": 24,
        "special_name": "Mega Ball",
        # Blancas 1-70 desde 2017-10-31; Mega Ball 1-24 desde 2025-04-08
        "white_era": date(2017, 10, 31),
        "special_era": date(2025, 4, 8),
    },
    "powerball": {
        "label": "Powerball",
        "url": "https://www.texaslottery.com/export/sites/lottery/Games/Powerball/Winning_Numbers/powerball.csv",
        "white_max": 69,
        "special_max": 26,
        "special_name": "Powerball",
        # Matriz 5/69 + 1/26 desde 2015-10-07
        "white_era": date(2015, 10, 7),
        "special_era": date(2015, 10, 7),
    },
}


def load_draws(game):
    req = urllib.request.Request(game["url"], headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=60) as r:
        text = r.read().decode("utf-8", errors="replace")
    draws = []
    for row in csv.reader(io.StringIO(text)):
        if len(row) < 10:
            continue
        try:
            d = date(int(row[3]), int(row[1]), int(row[2]))
            whites = sorted(int(x) for x in row[4:9])
            special = int(row[9])
        except ValueError:
            continue
        draws.append((d, whites, special))
    if len(draws) < 100:
        raise SystemExit(f"Descarga sospechosa para {game['label']}: "
                         f"solo {len(draws)} sorteos")
    draws.sort(key=lambda x: x[0])
    return draws


def stats_for(key):
    game = GAMES[key]
    draws = load_draws(game)
    wd = [(d, w, s) for d, w, s in draws if d >= game["white_era"]]
    sd = [(d, w, s) for d, w, s in draws
          if d >= game["special_era"] and 1 <= s <= game["special_max"]]

    white_freq, pair_freq = Counter(), Counter()
    for _, whites, _ in wd:
        white_freq.update(whites)
        pair_freq.update(combinations(whites, 2))
    special_freq = Counter(s for _, _, s in sd)

    recent = Counter()
    for _, whites, _ in wd[-50:]:
        recent.update(whites)

    last = wd[-1]
    return {
        "key": key,
        "label": game["label"],
        "white_max": game["white_max"],
        "special_max": game["special_max"],
        "special_name": game["special_name"],
        "white_era": game["white_era"].isoformat(),
        "special_era": game["special_era"].isoformat(),
        "draws": len(wd),
        "special_draws": len(sd),
        "first_date": wd[0][0].isoformat(),
        "last_date": last[0].isoformat(),
        "last_draw": {"whites": last[1], "special": last[2]},
        "white_freq": [[n, white_freq.get(n, 0)]
                       for n in range(1, game["white_max"] + 1)],
        "special_freq": [[n, special_freq.get(n, 0)]
                         for n in range(1, game["special_max"] + 1)],
        "pairs": [[a, b, c] for (a, b), c in pair_freq.items()],
        "top_pairs": [[a, b, c] for (a, b), c in pair_freq.most_common(10)],
        "recent": [[n, c] for n, c in recent.most_common(10)],
    }


def main():
    payload = {
        "updated": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "games": {k: stats_for(k) for k in GAMES},
    }
    out = HERE / "stats.json"
    out.write_text(json.dumps(payload, separators=(",", ":")))
    for k, g in payload["games"].items():
        print(f"{g['label']}: {g['draws']} sorteos, último {g['last_date']}")
    print(f"OK → {out} ({out.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
