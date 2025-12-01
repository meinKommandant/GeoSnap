from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class GPSCoordinates:
    """Almacena latitud, longitud y altitud procesadas."""
    latitude: float
    longitude: float
    altitude: Optional[float] = 0.0
    azimuth: Optional[float] = None

    def __str__(self):
        return f"{self.latitude}, {self.longitude}"

@dataclass
class PhotoMetadata:
    """Objeto que representa una foto procesada."""
    filename: str
    filepath: str
    timestamp: Optional[datetime]
    coordinates: Optional[GPSCoordinates]
    description: Optional[str] = ""
    sequence_id: Optional[str] = None

    @property
    def has_gps(self) -> bool:
        return self.coordinates is not None