from pydantic import BaseModel, Field


class Location(BaseModel):
    lat: float = Field(..., ge=-90, le=90)
    lng: float = Field(..., ge=-180, le=180)


class Place(BaseModel):
    name: str = Field(..., min_length=1)
    type: str = Field(..., min_length=1)
    location: Location


class HighRiskAreas(BaseModel):
    spread_radius: int = Field(..., gt=0)
    high_risk_areas: list[Place]


class SafeZones(BaseModel):
    safe_zones: list[Place]


class Route(BaseModel):
    origin: Place
    destination: Place
    duration: str
    distance_meters: int


class Routes(BaseModel):
    routes: list[Route]

    