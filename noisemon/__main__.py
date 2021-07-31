import uvicorn
from settings import settings

uvicorn.run(
    "app:app",
    host=settings.HOST,
    port=settings.PORT,
    reload=settings.ENVIRONMENT != "production"
)