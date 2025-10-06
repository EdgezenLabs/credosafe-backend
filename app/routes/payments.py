# app/routes/payments.py

from fastapi import APIRouter

# Create the router instance
router = APIRouter(
    prefix="/payments",
    tags=["Payments"]
)

@router.get("/")
async def read_payments():
    return {"message": "Payments endpoint reached"}

# ... Add your specific payment routes here