[PROJECT_README.md](https://github.com/user-attachments/files/25373021/PROJECT_README.md)
# Swish - Basketball Analytics Platform

> **Your AI assistant for this project: Swish 🏀**

## Project Overview

Swish is a comprehensive basketball analytics platform that combines KenPom metrics visualization with machine learning-powered March Madness predictions. Built by Tyson for analyzing NCAA basketball performance and tournament outcomes.

## What It Does

### 1. **KenPom Season Trends** (`index.html`)
- Visualizes team metrics throughout the season
- Shows Adjusted Offense, Adjusted Defense, and Net Rating
- Historical data (all Sundays) + current ratings (through yesterday)
- Toggle between raw values and rankings
- Interactive Chart.js visualizations

### 2. **Team Comparison** (`compare.html`)
- Side-by-side comparison of two teams
- Three separate charts (AdjO, AdjD, Net Rating)
- Same historical + current data approach
- Rankings toggle

### 3. **March Madness Predictions** (`bracket.html`)
- AI-powered tournament bracket predictions
- Ensemble model: Seed Baseline + XGBoost + Neural Network
- Trained on historical data (2003-2024)
- Currently shows Final Four + Championship (2025)
- **TODO**: Expand to full 68-team bracket with ✅/❌ indicators

## Tech Stack

### Frontend
- **HTML/CSS/JavaScript** - Pure vanilla JS, no frameworks
- **Chart.js** - Data visualization
- **GitHub Pages** - Hosting
- **URL**: https://ttuboat.github.io/kenpom-metrics-viewer/

### Backend
- **Node.js + Express** - API server
- **Axios** - HTTP requests to KenPom API
- **CORS** - Cross-origin handling
- **Render** - Hosting (free tier)
- **URL**: https://kenpom-metrics-viewer.onrender.com

### Machine Learning
- **Python** - Training environment
- **PyTorch** - Neural network
- **XGBoost** - Gradient boosting
- **Kaggle Notebooks** - Training platform (free GPU)
- **scikit-learn** - Preprocessing, metrics
- **Pandas/NumPy** - Data manipulation

## Project Structure

```
kenpom-metrics-viewer/
├── index.html              # Single team trends viewer
├── compare.html            # Two-team comparison
├── bracket.html            # Tournament predictions (WIP)
├── server.js               # Backend API (on Render)
├── package.json            # Node dependencies
├── predictions_2025_all_matchups.csv   # ML predictions
├── teams_2025_with_seeds.csv           # Tournament teams
└── README.md               # GitHub repo readme

Kaggle:
└── march_madness_model.ipynb   # ML training notebook
```

## Deployment Details

### Frontend (GitHub Pages)
- **Repository**: https://github.com/ttuboat/kenpom-metrics-viewer
- **Branch**: main
- **Deploy from**: / (root)
- **Custom domain**: None (using ttuboat.github.io)

### Backend (Render)
- **Service name**: kenpom-metrics-viewer
- **Type**: Web Service
- **Environment**: Node
- **Build Command**: `npm install`
- **Start Command**: `npm start`
- **Port**: 10000 (auto-assigned)
- **Instance**: Free tier (sleeps after 15 min inactivity)

**Environment Variables:**
```
KENPOM_API_KEY=<secret>
```

## API Documentation

### Backend Endpoints

**1. Health Check**
```
GET /
Returns: { status: 'KenPom API Backend is running' }
```

**2. Archive Data (Historical)**
```
GET /api/archive?d=YYYY-MM-DD&y=YEAR&team=TEAM_NAME
Returns: KenPom data for specific date
```

**3. Current Ratings**
```
GET /api/ratings/current?y=YEAR&team=TEAM_NAME
Returns: Latest KenPom ratings (updated overnight)
```

**4. Team Data (Legacy)**
```
GET /api/team/:teamName?date=YYYY-MM-DD&year=YEAR
Returns: Team data for specific date
```

### KenPom API Integration
- **Base URL**: https://kenpom.com/api.php
- **Auth**: Bearer token
- **Endpoints Used**: 
  - `archive` - Historical data by date
  - `ratings` - Current season ratings

**Key Field Mappings:**
- `AdjOE` → Adjusted Offensive Efficiency
- `AdjDE` → Adjusted Defensive Efficiency  
- `AdjEM` → Adjusted Efficiency Margin (Net Rating)
- `RankAdjOE/DE/EM` → Rankings for each metric
- `TeamName` → Team identifier

## Machine Learning Model

### Architecture
**Ensemble of 3 models:**
1. **Seed Baseline** - Simple logistic function based on seed difference
2. **XGBoost** - Gradient boosting on tabular features
3. **Neural Network** - 4-layer PyTorch network with dropout

**Final prediction** = Weighted average (optimized via grid search)

### Features
- **Four Factors**: eFG%, TOV%, ORB%, FT Rate (offense + defense)
- **Efficiency Metrics**: AdjO, AdjD, AdjEM
- **Seeds**: Tournament seeding, seed differential
- **Momentum**: Last 10 games performance trends
- **Consistency**: Standard deviation of recent performance

### Training Data
- **Years**: 2003-2024 (22 seasons)
- **Games**: ~500 tournament games
- **Validation**: Temporal split (last 3 seasons for testing)

### Performance
- **Test Log Loss**: 0.574 (competitive with Kaggle submissions)
- **2025 Predictions**: 
  - ✅ Correctly predicted both finalists (Florida, Houston)
  - ❌ Predicted Houston to win (58.7%), Florida won (65-63)
  - Overall very close call!

## Current Status

### ✅ Completed
- KenPom season trends visualization
- Team comparison tool
- Backend API with CORS handling
- Historical + current data fetching
- ML model training and evaluation
- Basic bracket visualization (Final Four)
- CSV exports of predictions

### 🚧 In Progress
- Full 68-team bracket visualization
- Correct/incorrect prediction markers (✅/❌)

### 📋 TODO
- [ ] Expand bracket to show all 67 games
- [ ] Add visual indicators for prediction accuracy
- [ ] Calculate and display overall bracket score
- [ ] Add manual override functionality for predictions
- [ ] Mobile responsive improvements for bracket
- [ ] Add region-by-region views
- [ ] Export bracket as image/PDF
- [ ] Prepare for 2026 tournament predictions

## Development Notes

### Data Flow
1. User selects team(s) and season
2. Frontend calculates all Sundays in season (Nov-Mar)
3. For each Sunday: Frontend → Render backend → KenPom API
4. Backend filters for specific team, returns to frontend
5. Frontend also fetches "current" ratings (yesterday's data)
6. All data aggregated and visualized with Chart.js

### Key Lessons Learned
- KenPom API uses ending year (2024-25 season = `y=2025`)
- KenPom updates overnight, so "current" = yesterday's data
- Render free tier sleeps after 15min inactivity (30-60s wake time)
- CORS origin must match GitHub Pages URL exactly
- Team names must match KenPom's format exactly (case-sensitive)
- Archive endpoint uses `d` parameter, not `archivedD`

### Common Issues & Solutions

**Problem**: CORS errors
**Solution**: Check `server.js` origin matches `https://ttuboat.github.io`

**Problem**: 404 on current ratings
**Solution**: Use archive endpoint with yesterday's date instead

**Problem**: No data for 2026 season
**Solution**: Check if year parameter is correct (2026 for 2025-26 season)

**Problem**: Render backend timeout
**Solution**: First request after sleep takes 30-60s (expected behavior)

## Quick Start for New Sessions

1. **Frontend changes**: Edit in GitHub, auto-deploys to Pages
2. **Backend changes**: Push to GitHub, Render auto-deploys (2-3 min)
3. **Test locally**: `npm start` → http://localhost:10000
4. **ML changes**: Edit Kaggle notebook, download CSVs, upload to GitHub

## Useful Commands

```bash
# Run backend locally
npm install
npm start

# Test API endpoint
curl https://kenpom-metrics-viewer.onrender.com/api/ratings/current?y=2026

# Check Render logs
# Go to dashboard.render.com → kenpom-metrics-viewer → Logs
```

## Links

- **Live Site**: https://ttuboat.github.io/kenpom-metrics-viewer/
- **GitHub Repo**: https://github.com/ttuboat/kenpom-metrics-viewer
- **Backend API**: https://kenpom-metrics-viewer.onrender.com
- **Render Dashboard**: https://dashboard.render.com
- **Kaggle Notebook**: [User's Kaggle account - notebook name TBD]

## Contact

**Developer**: Tyson
**AI Assistant**: Swish 🏀

---

**Last Updated**: February 12, 2026
**Version**: 1.0 (Initial release with trends + comparison + basic bracket)
