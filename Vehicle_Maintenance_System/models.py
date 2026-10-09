from dataclasses import dataclass

@dataclass
class Vehicle:
    plate: str
    owner: str
    brand: str
    model: str
    year: str
    kind: str
    contact: str

@dataclass
class Service:
    vehicle_id: int
    date: str
    service_type: str
    description: str
    mileage: str
    cost: float
    status: str
    mechanic_name: str = ""