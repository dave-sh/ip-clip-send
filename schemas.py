from uuid import UUID
from pydantic import BaseModel
from typing import Optional

class Error(BaseModel):
    detail: Optional[str] = None
    
class IPInformationSchema(BaseModel):
    id: UUID
    ip_address: str
    ip_or_subnet: int
    list_id: str
    
class ProviderInformationSchema(BaseModel):
    id: UUID
    name: str
    maintainer: str
    maintainer_url: str
    category: str