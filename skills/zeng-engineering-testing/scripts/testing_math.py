"""Original, standard-library-only teaching calculations (not metrology software).

Source locations and conventions: ../references/formula-audit.md.
All frequency arguments use Hz. Responses have normalized static gain 1.
"""
from __future__ import annotations
import cmath
import math
from collections.abc import Iterable


def _finite(value: float, name: str) -> float:
    value = float(value)
    if not math.isfinite(value):
        raise ValueError(f"{name} must be finite")
    return value


def _positive(value: float, name: str) -> float:
    value = _finite(value, name)
    if value <= 0:
        raise ValueError(f"{name} must be positive")
    return value


def _nonnegative(value: float, name: str) -> float:
    value = _finite(value, name)
    if value < 0:
        raise ValueError(f"{name} must be nonnegative")
    return value


def _integer(value: int, name: str, minimum: int) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
        raise ValueError(f"{name} must be an integer >= {minimum}")
    return value


def _samples(values: Iterable[float]) -> list[float]:
    data = [_finite(value, "sample") for value in values]
    if not data:
        raise ValueError("samples must not be empty")
    return data


def signal_statistics(values: Iterable[float]) -> dict[str, float]:
    """Record statistics; population divisor N, no N-1 correction, no detrending."""
    data = _samples(values)
    n = len(data)
    mean = math.fsum(data) / n
    mean_square = math.fsum(x * x for x in data) / n
    variance = math.fsum((x - mean) ** 2 for x in data) / n
    return {"mean": mean, "mean_square": mean_square, "variance": variance,
            "rms": math.sqrt(mean_square), "ac_rms": math.sqrt(variance)}


def linear_calibration(inputs: Iterable[float], outputs: Iterable[float]) -> dict[str, float]:
    """Unweighted least-squares y=slope*x+offset. No accuracy certification."""
    x, y = _samples(inputs), _samples(outputs)
    if len(x) != len(y) or len(x) < 2:
        raise ValueError("equal lengths >= 2 required")
    mx, my = math.fsum(x) / len(x), math.fsum(y) / len(y)
    denom = math.fsum((v - mx) ** 2 for v in x)
    if denom == 0:
        raise ValueError("inputs must vary")
    slope = math.fsum((a - mx) * (b - my) for a, b in zip(x, y)) / denom
    offset = my - slope * mx
    residual = max(abs(b - (slope * a + offset)) for a, b in zip(x, y))
    return {"slope": slope, "offset": offset, "max_abs_residual": residual}


def first_order_response(tau_s: float, frequency_hz: float) -> dict[str, float]:
    tau = _positive(tau_s, "tau_s")
    f = _nonnegative(frequency_hz, "frequency_hz")
    wt = 2 * math.pi * f * tau
    return {"gain": 1 / math.hypot(1, wt),
            "phase_deg": -math.degrees(math.atan(wt))}


def first_order_step(tau_s: float, time_s: float) -> float:
    tau = _positive(tau_s, "tau_s")
    t = _nonnegative(time_s, "time_s")
    return -math.expm1(-t / tau)


def first_order_amplitude_limit(tau_s: float, allowed_loss: float) -> float:
    """Hz limit for amplitude only. Does NOT validate phase distortion."""
    tau = _positive(tau_s, "tau_s")
    loss = _positive(allowed_loss, "allowed_loss")
    if loss >= 1:
        raise ValueError("allowed_loss must be strictly between 0 and 1")
    return math.sqrt((1 - loss) ** -2 - 1) / (2 * math.pi * tau)


def second_order_response(natural_hz: float, damping_ratio: float,
                          frequency_hz: float) -> dict[str, float]:
    """Positive damping, normalized second-order low-pass, atan2 quadrant."""
    fn = _positive(natural_hz, "natural_hz")
    zeta = _positive(damping_ratio, "damping_ratio")
    r = _nonnegative(frequency_hz, "frequency_hz") / fn
    h = 1 / complex(1 - r * r, 2 * zeta * r)
    return {"gain": abs(h), "phase_deg": math.degrees(cmath.phase(h))}


def bridge_output(excitation_v: float, r1: float, r2: float,
                  r3: float, r4: float) -> float:
    """Top-to-bottom supply; left r1/r2 minus right r3/r4 midpoint voltage.

       +V --- r1 --- L --- r2 --- 0
       +V --- r3 --- R --- r4 --- 0
       output = V(L) - V(R)
    """
    v = _finite(excitation_v, "excitation_v")
    a, b, c, d = [_positive(r, "resistance") for r in (r1, r2, r3, r4)]
    return v * (b / (a + b) - d / (c + d))


def adc_lsb(span_v: float, bits: int) -> float:
    """2**bits equal intervals over full input span; ideal round-to-nearest."""
    span = _positive(span_v, "span_v")
    _integer(bits, "bits", 1)
    if bits > 32:
        raise ValueError("teaching model supports at most 32 bits")
    return span / (2 ** bits)


def alias_frequency(frequency_hz: float, sample_rate_hz: float) -> float:
    """Fold frequency into [0, fs/2]; does not recover original frequency/phase."""
    f = _nonnegative(frequency_hz, "frequency_hz")
    fs = _positive(sample_rate_hz, "sample_rate_hz")
    folded = f % fs
    return min(folded, fs - folded)


def rpm_from_counts(count: int, pulses_per_revolution: int, gate_s: float) -> float:
    _integer(count, "count", 0)
    _integer(pulses_per_revolution, "pulses_per_revolution", 1)
    return 60 * count / (pulses_per_revolution * _positive(gate_s, "gate_s"))


def sound_pressure_level(pressure_rms_pa: float, reference_pa: float = 2e-5) -> float:
    p = _positive(pressure_rms_pa, "pressure_rms_pa")
    ref = _positive(reference_pa, "reference_pa")
    return 20 * (math.log10(p) - math.log10(ref))


def combine_uncorrelated_levels(levels_db: Iterable[float]) -> float:
    """Same reference and weighting; incoherent mean-square addition only."""
    levels = _samples(levels_db)
    peak = max(levels)
    return peak + 10 * math.log10(math.fsum(10 ** ((v - peak) / 10) for v in levels))


def one_sided_amplitude_spectrum(values: Iterable[float], sample_rate_hz: float
                                  ) -> list[tuple[float, float]]:
    """Small teaching DFT, rectangular window, peak-amplitude (not RMS/PSD).

    Includes DC and, for even N, Nyquist without doubling those endpoints.
    Intentionally limited to 4096 points: O(N**2), not a production FFT.
    """
    data = _samples(values)
    fs = _positive(sample_rate_hz, "sample_rate_hz")
    n = len(data)
    if not 2 <= n <= 4096:
        raise ValueError("teaching DFT requires 2..4096 samples")
    spectrum = []
    for k in range(n // 2 + 1):
        value = sum(x * cmath.exp(-2j * math.pi * k * i / n)
                    for i, x in enumerate(data)) / n
        scale = 1 if k == 0 or (n % 2 == 0 and k == n // 2) else 2
        spectrum.append((k * fs / n, scale * abs(value)))
    return spectrum
