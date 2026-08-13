from dataclasses import dataclass


@dataclass(frozen=True)
class OceanProfile:
    """Synthetic ARGO-like ocean profile used for deterministic tests."""

    profile_id: str
    latitude: float
    longitude: float
    timestamp: str
    depths: tuple[float, ...]
    temperatures: tuple[float | None, ...]
    source: str = "synthetic_test_data"

    def to_dict(self) -> dict:
        return {
            "profile_id": self.profile_id,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "timestamp": self.timestamp,
            "depths": list(self.depths),
            "temperatures": list(self.temperatures),
            "source": self.source,
        }


SYNTHETIC_PROFILES = {
    "SYN-ARABIAN-WARM-001": OceanProfile(
        profile_id="SYN-ARABIAN-WARM-001",
        latitude=15.2,
        longitude=68.4,
        timestamp="2026-07-15T00:00:00Z",
        depths=(0, 10, 25, 50, 75, 100, 150, 200),
        temperatures=(30.6, 30.1, 29.0, 25.2, 21.5, 18.9, 15.2, 12.8),
    ),
    "SYN-ARABIAN-NORMAL-001": OceanProfile(
        profile_id="SYN-ARABIAN-NORMAL-001",
        latitude=14.6,
        longitude=66.9,
        timestamp="2026-07-15T00:00:00Z",
        depths=(0, 10, 25, 50, 75, 100, 150, 200),
        temperatures=(28.4, 28.2, 27.5, 25.9, 23.8, 21.7, 17.4, 14.6),
    ),
    "SYN-BAY-BENGAL-001": OceanProfile(
        profile_id="SYN-BAY-BENGAL-001",
        latitude=12.8,
        longitude=87.2,
        timestamp="2026-07-15T00:00:00Z",
        depths=(0, 10, 20, 40, 60, 100, 150),
        temperatures=(29.3, 29.0, 28.1, 26.0, 23.5, 19.4, 16.1),
    ),
}
