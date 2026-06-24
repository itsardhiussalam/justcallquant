from fastapi import APIRouter
from services.macro import fetch_macro_indicator
from schemas.macro import MacroIndicatorResponse

router = APIRouter(prefix="/api/macro", tags=["Macro"])


@router.get("/indicators/{indicator_name}", response_model=MacroIndicatorResponse)
def get_macro_indicator(indicator_name: str, limit: int = 6):
    """Mengambil tren indikator makroekonomi global dari FRED Service."""
    return fetch_macro_indicator(indicator_name, limit)