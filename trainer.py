import pandas as pd
import numpy as np
from pathlib import Path
import json
from datetime import datetime
import config
import data_manager
from polya_urn import polya_urn_simulation

def main():
    if not config.HF_TOKEN:
        print("HF_TOKEN not set")
        return

    df = data_manager.load_master_data()
    all_results = {}
    today = datetime.now().strftime("%Y-%m-%d")

    for universe_name, tickers in config.UNIVERSES.items():
        print(f"\n=== Universe: {universe_name} (Pólya Urn) ===")
        returns = data_manager.prepare_returns_matrix(df, tickers)
        if returns.empty or len(returns) < min(config.WINDOWS) + 10:
            print("  Insufficient data")
            all_results[universe_name] = {"top_etfs": []}
            continue

        best_per_etf = {}   # ticker -> (best_score, best_window)
        window_results = {} # win -> scores dict

        for win in config.WINDOWS:
            if len(returns) < win:
                print(f"  Skipping window {win}d (insufficient data)")
                continue
            print(f"  Processing window {win}d...")
            scores = polya_urn_simulation(returns, win, transfer_prob=config.TRANSFER_PROB)
            if scores is None:
                continue
            window_results[win] = scores
            for etf, score in scores.items():
                if etf not in best_per_etf or score > best_per_etf[etf][0]:
                    best_per_etf[etf] = (score, win)

        if not best_per_etf:
            print("  No valid predictions")
            all_results[universe_name] = {"top_etfs": []}
            continue

        # Sort by best score descending
        sorted_etfs = sorted(best_per_etf.items(), key=lambda x: x[1][0], reverse=True)
        top_etfs = []
        full_scores = {}
        for ticker, (score, win) in sorted_etfs[:config.TOP_N]:
            top_etfs.append({"ticker": ticker, "ball_proportion": float(score), "best_window": win})
            full_scores[ticker] = {"score": float(score), "best_window": win}
        print(f"  Top 3 ETFs by ball proportion: {[e['ticker'] for e in top_etfs]}")
        all_results[universe_name] = {
            "top_etfs": top_etfs,
            "full_scores": full_scores,
            "window_results": window_results,
            "run_date": today
        }

    Path("results").mkdir(exist_ok=True)
    local_path = Path(f"results/polya_urn_{today}.json")
    with open(local_path, "w") as f:
        json.dump({"run_date": today, "universes": all_results}, f, indent=2)

    import push_results
    push_results.push_daily_result(local_path)
    print("\n=== Pólya Urn Contagion Engine complete ===")

if __name__ == "__main__":
    main()
