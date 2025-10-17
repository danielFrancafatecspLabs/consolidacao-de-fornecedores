from pydantic import BaseModel, Field
from typing import List, Optional
from uuid import uuid4


class ItemDetail(BaseModel):
    perfil: Optional[str]
    hora: Optional[float]
    hh: Optional[float]
    qtde_recursos: Optional[int]
    alocacao_meses: Optional[int]
    valor_total: Optional[float]


class SupplierRecord(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    fornecedor: str
    total: float
    detalhes: List[ItemDetail] = []


class UploadRecord(BaseModel):
    upload_id: str = Field(default_factory=lambda: str(uuid4()))
    filename: Optional[str]
    timestamp: Optional[str]
    rows: Optional[int]
