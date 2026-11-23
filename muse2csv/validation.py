"""
muse2csv.validation
-------------------
Validate the generated CSV file.

Author: Levente Nagy
License: MIT
"""

import numpy as np
import pandas as pd

DERIVED_LEADS = {"III", "aVR", "aVL", "aVF"}
TIME_COL = "Time"
CSV_SEP = ";"


def verify_waveforms(waveform: dict, lead_waveforms) -> None:
    """Validate sample counts, recorded/derived leads, and finite values against XML metadata."""
    lead_entries = waveform["LeadData"]
    if isinstance(lead_entries, dict):
        lead_entries = [lead_entries]

    recorded_leads = {entry["LeadID"] for entry in lead_entries}
    expected_leads = recorded_leads | (DERIVED_LEADS if {"I", "II"} <= recorded_leads else set())
    available_leads = set(lead_waveforms.keys())

    if missing := expected_leads - available_leads:
        raise ValueError(f"Missing ECG leads: {sorted(missing)}")

    expected_counts = {int(entry["LeadSampleCountTotal"]) for entry in lead_entries}
    if len(expected_counts) != 1:
        raise ValueError(f"Inconsistent LeadSampleCountTotal across leads: {expected_counts}")
    expected_samples = expected_counts.pop()

    for lead in expected_leads:
        values = np.asarray(lead_waveforms[lead], dtype=float)
        if len(values) != expected_samples:
            raise ValueError(f"Lead '{lead}' sample count mismatch: expected {expected_samples}, got {len(values)}")
        if not np.all(np.isfinite(values)):
            raise ValueError(f"Lead '{lead}' contains NaN or infinite values")


def verify_csv_roundtrip(
    csv_path: str,
    lead_waveforms,
    frequency: int,
    atol_mv: float = 5.1e-4,
    atol_ms: float = 1e-6,
) -> None:
    """Read back the exported semicolon-separated CSV and verify time axis (s) and 3-decimal lead amplitudes (mV)."""
    reloaded = pd.read_csv(csv_path, sep=CSV_SEP)
    lead_names = list(lead_waveforms.keys())

    if not lead_names:
        raise ValueError("CSV round-trip failed: no leads to verify")

    if missing := set(lead_names) - set(reloaded.columns):
        raise ValueError(
            f"CSV round-trip failed: missing lead columns {sorted(missing)} "
            f"(got {list(reloaded.columns)})"
        )

    if TIME_COL not in reloaded.columns:
        raise ValueError(f"CSV round-trip failed: missing time column '{TIME_COL}'")

    expected_samples = len(np.asarray(lead_waveforms[lead_names[0]]))
    if len(reloaded) != expected_samples:
        raise ValueError(
            f"CSV round-trip failed: expected {expected_samples} rows, got {len(reloaded)}"
        )

    actual_time = reloaded[TIME_COL].to_numpy(dtype=float)
    expected_time = np.arange(expected_samples, dtype=float) * (1000.0 / float(frequency))
    if not np.allclose(actual_time, expected_time, rtol=0.0, atol=atol_ms, equal_nan=False):
        max_diff = float(np.max(np.abs(actual_time - expected_time)))
        raise ValueError(
            f"CSV round-trip failed: time axis does not match {frequency} Hz "
            f"(got {actual_time[:3].tolist()}..{actual_time[-1]}, "
            f"expected {expected_time[:3].tolist()}..{expected_time[-1]}, "
            f"max diff: {max_diff:.6g})"
        )

    for lead in lead_names:
        orig = np.asarray(lead_waveforms[lead], dtype=float)
        back = reloaded[lead].to_numpy(dtype=float)
        if not np.allclose(orig, back, rtol=0.0, atol=atol_mv, equal_nan=False):
            max_diff = float(np.max(np.abs(orig - back)))
            raise ValueError(
                f"CSV round-trip failed: values diverged for lead '{lead}' "
                f"(max diff: {max_diff:.6f} mV)"
            )
