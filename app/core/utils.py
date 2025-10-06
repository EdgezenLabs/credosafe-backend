from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi import status

def add_exception_handlers(app: FastAPI):
    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception):
        # Basic handler — expand for more types
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Internal server error", "error": str(exc)}
        )
