from pydantic import BaseModel, Field
from datetime import date


class MacroObservation(BaseModel):
    date: date
    value: float | None = Field(
        default=None,
        description="Nilai indikator pada tanggal tersebut. None jika data belum tersedia."
    )


class MacroIndicatorResponse(BaseModel):
    indicator_name: str = Field(..., description="Nama indikator, misal 'GDP' atau 'CPIAUCSL'")
    observations: list[MacroObservation]
    is_stale: bool = Field(
        default=False,
        description="True jika data ini dari cache lama karena API source gagal diakses."
    )
    source: str = Field(default="FRED")