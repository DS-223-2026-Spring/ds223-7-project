# Frontend Changelog

## Milestone 2 — Streamlit Dashboard (`pulse/app/app.py`)

### Features delivered
- 5-page Streamlit dashboard: Segments, A/B Tests, KPIs, User Demo, Campaign Editor
- Full API integration with FastAPI backend (GET, PUT, POST, DELETE)
- Custom CSS theme matching HTML prototype (Syne + DM Sans fonts, segment colors)
- Live campaign message editing with template-variable preview
- A/B test launch / reset controls per campaign
- User Demo simulation with session-state response log
- KPI summary with results table and conversion predictor chart

### Refactoring (issue #53)
- Extracted 8 reusable UI helper functions:
  - `page_header()`, `panel_header()`, `panel_close()`
    - `kpi_card()`, `seg_tag()`, `status_badge()`
      - `render_preview()`, `get_global_params()` (cached)
      - Removed all duplicate HTML/logic patterns across pages

      ### Docker
      - `Dockerfile` and `requirements.txt` verified; container starts on port 8501
      
