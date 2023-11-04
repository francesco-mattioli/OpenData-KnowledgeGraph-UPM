from pydantic import BaseModel, HttpUrl

from typing import Sequence


class ChargingStation(BaseModel):
    id: int
    name: str
    city: str
    dbpedia_city: HttpUrl


class StationSearchResults(BaseModel):
    results: Sequence[ChargingStation]
