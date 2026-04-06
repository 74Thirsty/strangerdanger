from app.models import RiskState
from app.risk import compute_risk


def test_panic_always_critical() -> None:
    risk, state = compute_risk({"panic_triggered": True}, {}, RiskState.NORMAL)
    assert risk == 100.0
    assert state == RiskState.CRITICAL


def test_tamper_after_anomaly_forces_critical() -> None:
    risk, state = compute_risk({"tamper": 0.95}, {"tamper": 1.0}, RiskState.ELEVATED)
    assert risk >= 95.0
    assert state == RiskState.CRITICAL


def test_gps_quality_downweights_noise() -> None:
    risk_good, _ = compute_risk(
        {
            "route_dev": 0.9,
            "route_novelty": 0.8,
            "sensor_inconsistency": 0.7,
        },
        {"gps": 1.0},
        RiskState.NORMAL,
    )
    risk_poor, _ = compute_risk(
        {
            "route_dev": 0.9,
            "route_novelty": 0.8,
            "sensor_inconsistency": 0.7,
        },
        {"gps": 0.1},
        RiskState.NORMAL,
    )
    assert risk_poor < risk_good


def test_guardian_nearby_suppresses_score() -> None:
    risk_no_guardian, _ = compute_risk({"geofence_violation": 0.8}, {}, RiskState.NORMAL)
    risk_guardian, _ = compute_risk(
        {"geofence_violation": 0.8, "guardian_nearby": 1.0}, {}, RiskState.NORMAL
    )
    assert risk_guardian < risk_no_guardian
