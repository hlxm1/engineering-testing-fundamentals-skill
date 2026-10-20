"""Run original teaching cases. No files, network, or physical hardware required."""
from pathlib import Path
import json
import math
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] /
                       "skills/zeng-engineering-testing/scripts"))
from testing_math import (adc_lsb, alias_frequency, bridge_output,
                          combine_uncorrelated_levels, first_order_amplitude_limit,
                          first_order_response, one_sided_amplitude_spectrum,
                          rpm_from_counts, signal_statistics, sound_pressure_level)


def main() -> None:
    # 2000-point record: integer periods. DFT uses a smaller 200-point fixture.
    data = [2 + 3 * math.sin(2 * math.pi * 50 * n / 1000) for n in range(2000)]
    spectrum = one_sided_amplitude_spectrum(data[:200], 1000)
    result = {
        "notice": "Original teaching inputs, NOT measured data or safety limits",
        "signal_statistics": signal_statistics(data),
        "first_order_tau_0.1s_at_1Hz": first_order_response(0.1, 1),
        "amplitude_only_5pct_limit_hz": first_order_amplitude_limit(0.1, 0.05),
        "bridge_output_v": bridge_output(5, 120.12, 120, 120, 120),
        "adc_lsb_10Vspan_12bit_v": adc_lsb(10, 12),
        "alias_700Hz_at_1000Hz_hz": alias_frequency(700, 1000),
        "rpm_900counts_60ppr_0.5s": rpm_from_counts(900, 60, 0.5),
        "spl_0.02Pa_db": sound_pressure_level(0.02),
        "two_uncorrelated_60db_sources_db": combine_uncorrelated_levels([60, 60]),
        "dft_200points_1000Hz_peak_amplitude_50Hz": dict(spectrum)[50.0],
        "storage_8ch_20ksps_4bytes_1800s_bytes": 8 * 20000 * 4 * 1800,
    }
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
