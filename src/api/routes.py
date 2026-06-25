from pathlib import Path
import threading
import logging

from fastapi import APIRouter, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from src.api.schemas import CuisinesResponse, HealthResponse, LocationsResponse
from src.data.repository import RestaurantRepository
from src.models.preferences import UserPreferences
from src.models.recommendation import RecommendationResponse
from src.services.recommendation import RecommendationService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1")

# We will initialize the repository lazily or eagerly on startup
repo = RestaurantRepository()
recommendation_service = RecommendationService()

# Track whether background loading is in progress
_data_loading = False
_data_loaded = False


def _load_data_background():
    """Load the dataset in a background thread so the server stays responsive."""
    global _data_loading, _data_loaded
    _data_loading = True
    try:
        logger.info("Background data loading started …")
        repo._ensure_loaded()
        _data_loaded = True
        logger.info("Background data loading complete!")
    except Exception as e:
        logger.error("Background data loading failed: %s", e)
    finally:
        _data_loading = False


@router.get("/health", response_model=HealthResponse)
def health_check():
    """Check API health and dataset status."""
    try:
        # Check if dataset is loaded without triggering a blocking download
        is_loaded = repo._df is not None
        count = len(repo._df) if is_loaded else 0
        status = "ok" if is_loaded else "ok - loading data"
        return HealthResponse(
            status=status,
            dataset_loaded=is_loaded,
            restaurant_count=count
        )
    except Exception as e:
        return HealthResponse(
            status=f"error: {str(e)}",
            dataset_loaded=False,
            restaurant_count=0
        )


@router.get("/locations", response_model=LocationsResponse)
def get_locations():
    """Get all unique locations from the dataset."""
    try:
        if repo._df is None:
            # Data is still loading, return empty list instead of blocking
            return LocationsResponse(locations=[])
        locations = repo.get_locations()
        return LocationsResponse(locations=locations)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/cuisines", response_model=CuisinesResponse)
def get_cuisines():
    """Get all unique cuisines from the dataset."""
    try:
        if repo._df is None:
            # Data is still loading, return empty list instead of blocking
            return CuisinesResponse(cuisines=[])
        cuisines = repo.get_cuisines()
        return CuisinesResponse(cuisines=cuisines)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/recommend", response_model=RecommendationResponse)
def get_recommendations(prefs: UserPreferences):
    """
    Get LLM-enriched recommendations based on user preferences.
    """
    if repo._df is None:
        raise HTTPException(
            status_code=503,
            detail="Server is still loading restaurant data. Please try again in a moment."
        )
    try:
        response = recommendation_service.recommend(prefs)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title="Zomato Restaurant Recommendation API",
        version="1.0.0",
        description="Backend API for AI-Powered Restaurant Recommendation System",
    )

    # Configure CORS for frontend access
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Adjust in production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(router)

    @app.on_event("startup")
    def startup_event():
        """Start loading data in a background thread on server startup."""
        thread = threading.Thread(target=_load_data_background, daemon=True)
        thread.start()
        logger.info("Data loading thread started in background.")

    # ── Serve frontend static files ──
    frontend_dir = Path(__file__).resolve().parent.parent.parent / "frontend"
    if frontend_dir.is_dir():
        app.mount("/static", StaticFiles(directory=str(frontend_dir)), name="static")

        @app.get("/", response_class=FileResponse, include_in_schema=False)
        def serve_frontend():
            """Serve the frontend index.html at the root URL."""
            return FileResponse(str(frontend_dir / "index.html"))

    return app

app = create_app()

