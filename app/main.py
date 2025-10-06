from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import logging
from app.core.database import Base, engine
from app.routes import (
    auth, users, tenants, loan_products,
    applications, leads, documents, payments,
    installments, followups, reports
)
from app.core.utils import add_exception_handlers

# create tables (for dev/demo). For production, use Alembic migrations.
Base.metadata.create_all(bind=engine)

# app init
app = FastAPI(title="CredoSafe API", version="1.0")

# CORS (adjust origins for production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

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

# global error handlers
add_exception_handlers(app)

@app.get("/")
def root():
    return {"message": "CredoSafe API (v1)"}
