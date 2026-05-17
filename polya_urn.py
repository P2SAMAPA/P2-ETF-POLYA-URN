import numpy as np
import pandas as pd

def polya_urn_simulation(returns_df, window, transfer_prob=0.05):
    """
    Simulate Pólya urn process over the last `window` days.
    Each ETF starts with 1 ball.
    Each day, identify ETFs with return > median return (universe median).
    For each such ETF, add one ball to its urn.
    Additionally, with probability `transfer_prob`, transfer one ball from a random other ETF to this ETF.
    Return the final ball counts and proportion (score) per ETF.
    """
    if len(returns_df) < window:
        return None
    # Take last window days
    data = returns_df.iloc[-window:].copy()
    n_etfs = data.shape[1]
    etf_names = data.columns.tolist()
    # Initialise urn counts (each ETF starts with 1 ball)
    balls = np.ones(n_etfs)
    total_days = len(data)
    for t in range(total_days):
        daily_returns = data.iloc[t].values
        # Median of daily returns across ETFs (universe median)
        median_ret = np.median(daily_returns)
        # Find outperforming ETFs (return > median)
        winners = np.where(daily_returns > median_ret)[0]
        for idx in winners:
            # Reinforcement: add ball to winner
            balls[idx] += 1
            # Possible transfer: with probability transfer_prob, steal a ball from a random other ETF
            if np.random.rand() < transfer_prob:
                # Choose a different ETF uniformly at random
                others = [j for j in range(n_etfs) if j != idx and balls[j] > 0]
                if others:
                    victim = np.random.choice(others)
                    balls[victim] -= 1
                    balls[idx] += 1   # the winner gains an extra ball (transfer)
    total_balls = np.sum(balls)
    if total_balls == 0:
        return {etf: 0.0 for etf in etf_names}
    scores = {etf: balls[i] / total_balls for i, etf in enumerate(etf_names)}
    return scores
