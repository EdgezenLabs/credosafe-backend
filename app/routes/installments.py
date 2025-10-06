# app/routes/installments.py

from fastapi import APIRouter

# CRITICAL: Define the APIRouter instance and name it 'router'
router = APIRouter(
    prefix="/installments",  # Optional: Define prefix here or in main.py
    tags=["Installments"]
)

# Example route (you will add your actual endpoints here)
@router.get("/")
async def get_all_installments():
    return {"message": "Installments router is working"}

# ... Add your specific installment routes here