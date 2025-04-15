from api.v1.routers import conversation, health
from bson.errors import InvalidId
from core.config import settings
from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse

# FastAPI app
app = FastAPI(title=settings.APP_TITLE)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS.split(","),
    allow_credentials=True,
    allow_headers=["*"],
    allow_methods=["*"],
)

app.include_router(router=health.router, prefix=settings.API_V1_STR, tags=["health"])

app.include_router(
    router=conversation.router, prefix=settings.API_V1_STR, tags=["conversation"]
)


@app.get("/", include_in_schema=False)
async def index() -> RedirectResponse:
    return RedirectResponse(url="/docs")


@app.exception_handler(InvalidId)
async def id_exception_handler(request, exc):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": "Invalid ID"},
    )
