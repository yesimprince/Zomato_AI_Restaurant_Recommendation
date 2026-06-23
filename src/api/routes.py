from pathlib import Path

from fastapi import APIRouter, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from src.api.schemas import CuisinesResponse, HealthResponse, LocationsResponse
from src.data.repository import RestaurantRepository
from src.models.preferences import UserPreferences
from src.models.recommendation import RecommendationResponse
from src.services.recommendation import RecommendationService

router = APIRouter(prefix="/api/v1")

# We will initialize the repository lazily or eagerly on startup
repo = RestaurantRepository()
recommendation_service = RecommendationService()


@router.get("/health", response_model=HealthResponse)
def health_check():
    """Check API health and dataset status."""
    try:
        # Check if dataset is loaded by checking count
        count = repo.count()
        return HealthResponse(
            status="ok",
            dataset_loaded=True,
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
        locations = repo.get_locations()
        return LocationsResponse(locations=locations)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/cuisines", response_model=CuisinesResponse)
def get_cuisines():
    """Get all unique cuisines from the dataset."""
    try:
        cuisines = repo.get_cuisines()
        return CuisinesResponse(cuisines=cuisines)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/recommend", response_model=RecommendationResponse)
def get_recommendations(prefs: UserPreferences):
    """
    Get LLM-enriched recommendations based on user preferences.
    """
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
