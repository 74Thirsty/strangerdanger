from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Mapping

from app.models import RiskState


@dataclass(frozen=True, slots=True)
class RiskConfig:
    base_bias: float = -1.0
    w_route_dev: float = 1.2
    w_route_novelty: float = 0.8
    w_stop: float = 1.1
    w_geofence: float = 0.9
    w_tamper: float = 2.2
    w_sensor: float = 0.8
    w_proximity: float = 0.4
    w_checkin: float = 0.9
    w_guardian: float = 1.5
    w_safe_context: float = 1.0
    bonus_route_stop: float = 0.7
    bonus_tamper_after_anomaly: float = 1.2
    penalty_low_gps_confidence: float = 0.7


def _bounded(value: float) -> float:
    return max(0.0, min(1.0, value))


def _quality_adjust(features: Mapping[str, float], quality: Mapping[str, float]) -> dict[str, float]:
    adjusted: dict[str, float] = {}
    for k, v in features.items():
        adjusted[k] = _bounded(v) * _bounded(quality.get(k, 1.0))
    return adjusted


def transition(prev_state: RiskState, risk: float, hard_trigger: bool) -> RiskState:
    if hard_trigger:
        return RiskState.CRITICAL

    if prev_state == RiskState.CRITICAL:
        return RiskState.HIGH if risk < 70 else RiskState.CRITICAL
    if prev_state == RiskState.HIGH:
        if risk >= 85:
            return RiskState.CRITICAL
        if risk < 50:
            return RiskState.ELEVATED
        return RiskState.HIGH
    if prev_state == RiskState.ELEVATED:
        if risk >= 65:
            return RiskState.HIGH
        if risk < 30:
            return RiskState.WATCH
        return RiskState.ELEVATED
    if prev_state == RiskState.WATCH:
        if risk >= 40:
            return RiskState.ELEVATED
        if risk < 15:
            return RiskState.NORMAL
        return RiskState.WATCH

    # NORMAL
    if risk >= 20:
        return RiskState.WATCH
    return RiskState.NORMAL


def compute_risk(
    features: Mapping[str, float | bool],
    quality: Mapping[str, float],
    prev_state: RiskState,
    config: RiskConfig = RiskConfig(),
) -> tuple[float, RiskState]:
    hard_trigger = bool(features.get("panic_triggered", False))

    numeric = {
        "route_dev": float(features.get("route_dev", 0.0)),
        "route_novelty": float(features.get("route_novelty", 0.0)),
        "unplanned_stop": float(features.get("unplanned_stop", 0.0)),
        "geofence_violation": float(features.get("geofence_violation", 0.0)),
        "tamper": float(features.get("tamper", 0.0)),
        "sensor_inconsistency": float(features.get("sensor_inconsistency", 0.0)),
        "unfamiliar_proximity": float(features.get("unfamiliar_proximity", 0.0)),
        "unanswered_checkin": float(features.get("unanswered_checkin", 0.0)),
        "guardian_nearby": float(features.get("guardian_nearby", 0.0)),
        "public_safe_context": float(features.get("public_safe_context", 0.0)),
    }

    adj = _quality_adjust(numeric, quality)

    z = config.base_bias
    z += config.w_route_dev * adj["route_dev"]
    z += config.w_route_novelty * adj["route_novelty"]
    z += config.w_stop * adj["unplanned_stop"]
    z += config.w_geofence * adj["geofence_violation"]
    z += config.w_tamper * adj["tamper"]
    z += config.w_sensor * adj["sensor_inconsistency"]
    z += config.w_proximity * adj["unfamiliar_proximity"]
    z += config.w_checkin * adj["unanswered_checkin"]
    z -= config.w_guardian * adj["guardian_nearby"]
    z -= config.w_safe_context * adj["public_safe_context"]

    if adj["route_dev"] > 0.6 and adj["unplanned_stop"] > 0.5:
        z += config.bonus_route_stop

    if adj["tamper"] > 0.7 and prev_state in {RiskState.ELEVATED, RiskState.HIGH}:
        z += config.bonus_tamper_after_anomaly

    if _bounded(quality.get("gps", 1.0)) < 0.3:
        z -= config.penalty_low_gps_confidence

    risk = 100 / (1 + math.exp(-z))

    if hard_trigger:
        return 100.0, RiskState.CRITICAL

    if adj["tamper"] > 0.8 and prev_state in {RiskState.HIGH, RiskState.ELEVATED}:
        return max(risk, 95.0), RiskState.CRITICAL

    return risk, transition(prev_state, risk, hard_trigger=False)
