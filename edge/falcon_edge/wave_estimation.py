"""Pressure-window conversion used by the FALCON edge service."""

from __future__ import annotations

import statistics
from typing import Any


DEFAULT_SEAWATER_DENSITY_KG_M3 = 1025.0
STANDARD_GRAVITY_M_S2 = 9.80665


def _median_filter(values: list[float], radius: int = 1) -> list[float]:
    """Remove isolated ADC spikes without shifting the pressure scale."""
    return [statistics.median(values[max(0, index - radius):index + radius + 1])
            for index in range(len(values))]


def pressure_to_displacement(pressure_kpa: float, baseline_kpa: float,
                             density_kg_m3: float = DEFAULT_SEAWATER_DENSITY_KG_M3,
                             gravity_m_s2: float = STANDARD_GRAVITY_M_S2,
                             pressure_response_factor: float = 1.0) -> float:
    """Convert one pressure sample to surface displacement in metres.

    ``pressure_response_factor`` is the site/depth calibration factor Kp.  A
    value of 1.0 is the hydrostatic controlled-test approximation.  Field use
    must supply a validated factor instead of silently claiming correction.
    """
    if density_kg_m3 <= 0 or gravity_m_s2 <= 0:
        raise ValueError("Density and gravity must be positive")
    if not 0 < pressure_response_factor <= 1:
        raise ValueError("Pressure response factor must be greater than 0 and at most 1")
    delta_pressure_pa = (pressure_kpa - baseline_kpa) * 1000.0
    return delta_pressure_pa / (density_kg_m3 * gravity_m_s2 * pressure_response_factor)


def estimate_wave_window(pressure_samples_kpa: list[float], baseline_kpa: float | None = None,
                         density_kg_m3: float = DEFAULT_SEAWATER_DENSITY_KG_M3,
                         gravity_m_s2: float = STANDARD_GRAVITY_M_S2,
                         pressure_response_factor: float = 1.0) -> dict[str, Any]:
    """Compute one pressure-derived wave-height summary from a sample window."""
    samples = [float(value) for value in pressure_samples_kpa]
    if len(samples) < 8:
        raise ValueError("At least eight pressure samples are required")
    filtered = _median_filter(samples)
    baseline = float(baseline_kpa) if baseline_kpa is not None else statistics.fmean(filtered)
    displacements = [pressure_to_displacement(value, baseline, density_kg_m3, gravity_m_s2,
                                               pressure_response_factor) for value in filtered]
    wave_height = max(displacements) - min(displacements)
    noise_rms_kpa = (statistics.fmean((raw - clean) ** 2 for raw, clean in zip(samples, filtered))) ** 0.5
    return {
        "waveHeightMeters": wave_height,
        "baselinePressureKpa": baseline,
        "rawPressureKpa": samples[-1],
        "filteredPressureKpa": filtered[-1],
        "minimumDisplacementMeters": min(displacements),
        "maximumDisplacementMeters": max(displacements),
        "sampleCount": len(samples),
        "noiseRmsKpa": noise_rms_kpa,
        "pressureResponseFactor": pressure_response_factor,
        "densityKgM3": density_kg_m3,
        "gravityMS2": gravity_m_s2,
    }


def apply_pressure_window(payload: dict[str, Any]) -> None:
    """Add a wave summary when an ESP32 frame includes a completed window."""
    raw = payload.get("pressureSamplesKpa")
    if not isinstance(raw, list) or not raw:
        return
    response = payload.get("pressureResponseFactor")
    calibrated = isinstance(response, (int, float)) and not isinstance(response, bool)
    result = estimate_wave_window(
        raw,
        payload.get("pressureBaselineKpa", payload.get("pressureBaseline")),
        float(payload.get("seawaterDensityKgM3", DEFAULT_SEAWATER_DENSITY_KG_M3)),
        float(payload.get("gravityMS2", STANDARD_GRAVITY_M_S2)),
        float(response) if calibrated else 1.0,
    )
    payload.update({
        "waveLevel": round(result["waveHeightMeters"], 3),
        "waterPressure": round(result["rawPressureKpa"], 4),
        "filteredPressure": round(result["filteredPressureKpa"], 4),
        "pressureBaseline": round(result["baselinePressureKpa"], 4),
        "waveSampleCount": result["sampleCount"],
        "pressureNoiseRmsKpa": round(result["noiseRmsKpa"], 6),
        "pressureResponseFactor": result["pressureResponseFactor"],
        "waveHeightState": "PRESSURE_DERIVED",
        "pressureCalibration": "CALIBRATED" if calibrated else "CALIBRATION REQUIRED",
    })
