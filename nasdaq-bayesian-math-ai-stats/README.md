# NASDAQ Bayesian Math AI Stats

> **Part of [Python AI Course](../README.md)** - A comprehensive learning repository covering AI, algorithms, and real-world applications.  
> See also: [NASDAQ CSE](../nasdaq-cse/) | [Fintech Tools](../fintech-tools/)

This directory contains two major applications for educational and analytical purposes:

## 1. Bayesian Stock and Commodity Market Analysis

This project provides a robust Python script for live, multi-market analysis of global equity and commodity data using Bayesian statistics and visualization. It supports major stock exchanges (NYSE, NASDAQ, LSE, HKEX, Euronext, Tokyo-SE, Shanghai-SE, Bombay-SE, NSE-India, etc.) and commodities (Gold, Oil, Silver, etc.). For markets without public APIs, web scraping is used where possible, with placeholders for easy extension.

Key concepts include Bayesian estimation of daily returns, volatility computation, and clear data visualization with Matplotlib. The code is modular, allowing for easy addition of new stock exchanges, commodities, or improvements to web scraping logic.

### Usage
```bash
python bayesian_stock_prediction.py
```

You can customize the exchanges and tickers analyzed by editing the appropriate lists in the script. For unsupported exchanges, fill in the web scraping routines for live data.

Example output includes mean return, volatility, Bayesian posterior estimates, and price/return plots for each market and commodity.

## 2. AI Interview Trick Question Trainer 🎯

**NEW!** A comprehensive Tkinter-based desktop application for practicing technical interview trick questions in Java and Python.

### Features
- **20 Curated Trick Questions**: Carefully selected Java and Python interview questions
- **Language Filtering**: Focus on Python, Java, or practice both languages  
- **Difficulty Levels**: Easy, Medium, and Hard questions
- **Timed Practice**: Configurable timers for realistic interview pressure
- **Progress Tracking**: Visual charts and statistics
- **Custom Questions**: Add your own questions via GUI dialog
- **JSON Persistence**: All data stored locally

### Quick Start
```bash
python3 ai_trick_question_interview_app.py
```

### Application Structure
- `ai_trick_question_interview_app.py` - Main application
- `trick_questions_db.json` - Question database and user statistics

### Key Benefits
- Practice realistic interview trick questions
- Learn from detailed explanations  
- Track improvement over time
- Focus on specific languages or difficulties
- Timed practice to simulate interview pressure

---

## Prerequisites

Ensure you have Python 3.x installed. Required packages:
- For Bayesian Analysis: `pymc3`, `yfinance`, `matplotlib`, `pandas`, `requests`, `beautifulsoup4`
- For Interview Trainer: `tkinter` (usually included), `json` (built-in)

## Resources

- [PyMC3 documentation](https://docs.pymc.io/) for Bayesian statistics
- [Yahoo Finance](https://finance.yahoo.com/) for live market data

Feel free to fork and contribute improvements!
