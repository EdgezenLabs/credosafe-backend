from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import logging
from app.core.database import Base, engine
from app.routes import (
    auth, users, tenants, loan_products,
    applications, leads, documents, payments,
    installments, followups, reports, loan_management
)
from app.core.utils import add_exception_handlers

# Import ALL models to ensure they are registered with SQLAlchemy
import app.models  # This imports all models through __init__.py

# create tables (for dev/demo). For production, use Alembic migrations.
# Base.metadata.create_all(bind=engine)  # Commented out - tables already exist

# app init
app = FastAPI(title="CredoSafe API", version="1.0")

# Mount static directory
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Serve favicon explicitly
@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return FileResponse("app/static/favicon.ico")

# CORS (adjust origins for production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5000", "http://127.0.0.1:3000", "http://127.0.0.1:5000"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# logging
logging.basicConfig(
    level=logging.DEBUG, 
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
    ]
)

# include routers
app.include_router(auth.router, prefix="/v1/auth", tags=["Auth"])
app.include_router(users.router, prefix="/v1/users", tags=["Users"])
app.include_router(tenants.router, prefix="/v1/tenants", tags=["Tenants"])
app.include_router(loan_products.router, prefix="/v1/loan-products", tags=["LoanProducts"])
app.include_router(leads.router, prefix="/v1/leads", tags=["Leads"])
app.include_router(applications.router, prefix="/v1/applications", tags=["Applications"])
app.include_router(documents.router, prefix="/v1/documents", tags=["Documents"])
app.include_router(payments.router, prefix="/v1/payments", tags=["Payments"])
app.include_router(installments.router, prefix="/v1/installments", tags=["Installments"])
app.include_router(followups.router, prefix="/v1/followups", tags=["Followups"])
app.include_router(reports.router, prefix="/v1/reports", tags=["Reports"])
app.include_router(loan_management.router, prefix="/v1", tags=["Loan Management"])

# global error handlers - temporarily disabled for debugging
# add_exception_handlers(app)

@app.get("/")
def root():
    return {"message": "CredoSafe API (v1)"}
