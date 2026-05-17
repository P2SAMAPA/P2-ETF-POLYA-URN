# Pólya Urn Contagion Engine

Models ETF performance as a Pólya urn process: each ETF is an urn that gains a ball when it outperforms the universe median (reinforcement). With a small probability, a ball is transferred from a randomly chosen ETF to the winner (cross‑sector contagion). The final ball proportion is the empirical outperformance frequency – a bullish signal.

- **Windows evaluated:** 63, 126, 252 days (best per ETF)
- **Transfer probability:** 5% (configurable)
- **Output:** top 3 ETFs per universe by highest ball proportion (most frequent outperformers)
- **Dashboard:** shows top ETFs, best window, and full ranking tables

Runs daily on GitHub Actions.

## Local execution

```bash
pip install -r requirements.txt
export HF_TOKEN=<your_token>
python trainer.py
streamlit run streamlit_app.py
