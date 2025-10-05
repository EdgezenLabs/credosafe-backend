from fastapi import FastAPI
from app.routes import (
    auth, users, tenants, loan_products,
    applications, leads, documents, reports
)

app = FastAPI(title="CredoSafe API", version="1.0")

# Register routes
app.include_router(auth.router, prefix="/v1/auth", tags=["Auth"])
app.include_router(users.router, prefix="/v1/users", tags=["Users"])
app.include_router(tenants.router, prefix="/v1/tenants", tags=["Tenants"])
app.include_router(loan_products.router, prefix="/v1/loan-products", tags=["Loan Products"])
app.include_router(applications.router, prefix="/v1/applications", tags=["Applications"])
app.include_router(leads.router, prefix="/v1/leads", tags=["Leads"])
app.include_router(documents.router, prefix="/v1/documents", tags=["Documents"])
app.include_router(reports.router, prefix="/v1/reports", tags=["Reports"])

@app.get("/")
def root():
    return {"message": "Welcome to CredoSafe API"}
