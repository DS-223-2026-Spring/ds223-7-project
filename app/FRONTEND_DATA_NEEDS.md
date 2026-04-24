# Frontend Data Requirements

This document describes the data the frontend will eventually need from the backend API.

---

## 🏠 Home Page

### Metrics
| Data | Endpoint | Description |
|------|----------|-------------|
| Total Users | `GET /api/users/count` | Total number of users in the system |
| Converted Users | `GET /api/users/converted/count` | Number of users who converted to paid |
| Conversion Rate | `GET /api/users/conversion-rate` | Percentage of converted users |

### Charts
| Data | Endpoint | Description |
|------|----------|-------------|
| Conversion Trend | `GET /api/metrics/conversion-trend` | Time series data of conversions over time |
| Recent Campaigns | `GET /api/campaigns/recent` | List of most recently created campaigns |

### Model Output
| Data | Endpoint | Description |
|------|----------|-------------|
| Model Predictions | `GET /api/model/predictions` | Overall conversion predictions from DS model |

---

## 📊 Segment Overview Page

### Filters
| Data | Endpoint | Description |
|------|----------|-------------|
| Segment Types | `GET /api/segments/types` | List of available segment types |
| Segment Statuses | `GET /api/segments/statuses` | List of available statuses |

### Table
| Data | Endpoint | Description |
|------|----------|-------------|
| Segment Table | `GET /api/segments` | Full list of segments with details |

### Charts
| Data | Endpoint | Description |
|------|----------|-------------|
| Segment Distribution | `GET /api/segments/distribution` | Distribution of users across segments |

### Model Output
| Data | Endpoint | Description |
|------|----------|-------------|
| Segment Scores | `GET /api/model/segment-scores` | Predicted scores per segment from DS model |

---

## 📣 Campaign Editor Page

### Filters
| Data | Endpoint | Description |
|------|----------|-------------|
| Segments for Filter | `GET /api/segments` | List of segments to filter campaigns by |
| Campaign Statuses | `GET /api/campaigns/statuses` | List of available campaign statuses |

### Table
| Data | Endpoint | Description |
|------|----------|-------------|
| Existing Campaigns | `GET /api/campaigns` | Full list of campaigns with details |

### Form
| Data | Endpoint | Description |
|------|----------|-------------|
| Target Segments | `GET /api/segments` | List of segments to target in a campaign |
| Create Campaign | `POST /api/campaigns` | Submit a new campaign to the backend |

### Model Output
| Data | Endpoint | Description |
|------|----------|-------------|
| Campaign Predictions | `GET /api/model/campaign-performance` | Predicted performance of campaigns |

---

## 🔌 API Connection
- Backend base URL is set via environment variable: `API_URL`
- Default value for local development: `http://localhost:8008`
- Inside Docker: `http://back:8000`