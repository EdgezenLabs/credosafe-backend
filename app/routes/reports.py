from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.crud import crud
from sqlalchemy import func

router = APIRouter()

@router.get("/applications-summary")
def applications_summary(tenant_id: str = None, db: Session = Depends(get_db)):
    rows = crud.applications_summary(db, tenant_id=tenant_id)
    return {"totals": rows}

@router.get("/agent-performance")
def agent_performance(tenant_id: str = None, db: Session = Depends(get_db)):
    # Basic aggregated report
    leads = db.query(crud.lead_model.Lead.agent_id, func.count(crud.lead_model.Lead.id)).group_by(crud.lead_model.Lead.agent_id)
    apps = db.query(crud.app_model.Application.agent_id, func.count(crud.app_model.Application.id)).group_by(crud.app_model.Application.agent_id)
    lead_map = {str(r[0]): r[1] for r in leads.all()}
    app_map = {str(r[0]): r[1] for r in apps.all()}
    agents = set(list(lead_map.keys()) + list(app_map.keys()))
    result = []
    for a in agents:
        result.append({
            "agent_id": a,
            "total_leads": lead_map.get(a, 0),
            "applications_submitted": app_map.get(a, 0),
            "approved_count": 0,
            "conversion_rate": 0.0
        })
    return result
