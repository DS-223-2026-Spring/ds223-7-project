"""
Pulse Backend — FastAPI entry point.

All dashboard reads go through the v_* SQL views (never raw tables).
DB connection: postgresql://pulse_user:pulse_pass@db:5432/pulse
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes import segments, ab_tests, kpis, campaigns, demo

app = FastAPI(
    title="Pulse API",
    description="Free-to-Paid Conversion Platform for Armat",
    version="0.1.0",
)

# --- CORS -----------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Routers ---------------------------------------------------------
app.include_router(segments.router)
app.include_router(ab_tests.router)
app.include_router(kpis.router)
app.include_router(campaigns.router)
app.include_router(demo.router)


# --- Health check ----------------------------------------------------
@app.get("/health", tags=["health"])
def health_check():
    """Simple liveness probe — Docker / PM can hit this to verify the
    container is up."""
    return {"status": "ok", "service": "pulse-backend"}
