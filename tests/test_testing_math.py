from pathlib import Path
import math
import sys
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] /
                       "skills/zeng-engineering-testing/scripts"))
import testing_math as m


class StatisticsTests(unittest.TestCase):
    def test_dc_sine(self):
        x = [2 + 3 * math.sin(2 * math.pi * 50 * i / 1000) for i in range(2000)]
        a = m.signal_statistics(x)
        for key, value in {"mean": 2, "variance": 4.5, "mean_square": 8.5,
                           "rms": math.sqrt(8.5), "ac_rms": 3 / math.sqrt(2)}.items():
            self.assertAlmostEqual(a[key], value, places=11)
        self.assertAlmostEqual(a["mean_square"], a["variance"] + a["mean"] ** 2)

    def test_constant(self):
        a = m.signal_statistics([-3] * 5)
        self.assertEqual(a["rms"], 3)
        self.assertEqual(a["variance"], 0)

    def test_calibration(self):
        a = m.linear_calibration([0, 1, 2, 3], [1, 3, 5, 7])
        self.assertEqual(a, {"slope": 2, "offset": 1, "max_abs_residual": 0})

    def test_calibration_invalid(self):
        for x, y in [([1, 1], [0, 1]), ([1], [2]), ([1, 2], [2, 3, 4])]:
            with self.assertRaises(ValueError):
                m.linear_calibration(x, y)

    def test_bad_samples(self):
        for x in [[], [float("nan")], [float("inf")]]:
            with self.assertRaises(ValueError):
                m.signal_statistics(x)


class ResponseTests(unittest.TestCase):
    def test_first_order_cutoff(self):
        a = m.first_order_response(0.1, 1 / (2 * math.pi * 0.1))
        self.assertAlmostEqual(a["gain"], 1 / math.sqrt(2))
        self.assertAlmostEqual(a["phase_deg"], -45)

    def test_first_order_step(self):
        self.assertEqual(m.first_order_step(1, 0), 0)
        self.assertAlmostEqual(m.first_order_step(1, 1), 1 - math.exp(-1))
        self.assertAlmostEqual(m.first_order_step(1, 4), 0.9816843611112658)

    def test_amplitude_limit(self):
        f = m.first_order_amplitude_limit(0.1, 0.05)
        self.assertAlmostEqual(m.first_order_response(0.1, f)["gain"], 0.95)

    def test_second_order_resonance(self):
        a = m.second_order_response(100, 0.5, 100)
        self.assertAlmostEqual(a["gain"], 1)
        self.assertAlmostEqual(a["phase_deg"], -90)

    def test_second_order_quadrant(self):
        self.assertLess(m.second_order_response(100, 0.7, 200)["phase_deg"], -90)
        self.assertEqual(m.second_order_response(100, 0.7, 0)["gain"], 1)

    def test_invalid_parameters(self):
        calls = [(m.first_order_response, (0, 1)),
                 (m.first_order_response, (1, -1)),
                 (m.first_order_step, (1, -1)),
                 (m.first_order_amplitude_limit, (1, 0)),
                 (m.first_order_amplitude_limit, (1, 1)),
                 (m.second_order_response, (100, 0, 1))]
        for fn, args in calls:
            with self.subTest(function=fn.__name__, args=args):
                with self.assertRaises(ValueError):
                    fn(*args)


class InstrumentTests(unittest.TestCase):
    def test_bridge(self):
        self.assertEqual(m.bridge_output(5, 120, 120, 120, 120), 0)
        exact = -5 * 0.12 / (2 * (240 + 0.12))
        self.assertAlmostEqual(m.bridge_output(5, 120.12, 120, 120, 120), exact)
        self.assertAlmostEqual(m.bridge_output(5, 121, 120, 120, 121),
                               -m.bridge_output(5, 120, 121, 121, 120))

    def test_adc(self):
        self.assertEqual(m.adc_lsb(10, 12), 10 / 4096)
        for bits in [0, 33, 3.5, True]:
            with self.assertRaises(ValueError):
                m.adc_lsb(10, bits)

    def test_alias(self):
        for f, expected in [(0, 0), (700, 300), (1300, 300), (500, 500), (1000, 0)]:
            self.assertEqual(m.alias_frequency(f, 1000), expected)

    def test_rpm(self):
        self.assertEqual(m.rpm_from_counts(900, 60, 0.5), 1800)
        self.assertEqual(m.rpm_from_counts(0, 60, 1), 0)
        for args in [(-1, 60, 1), (1, 0, 1), (1, 60, 0), (1.5, 60, 1)]:
            with self.assertRaises(ValueError):
                m.rpm_from_counts(*args)

    def test_acoustic(self):
        self.assertAlmostEqual(m.sound_pressure_level(2e-5), 0)
        self.assertAlmostEqual(m.sound_pressure_level(0.02), 60)
        self.assertAlmostEqual(m.combine_uncorrelated_levels([60, 60]),
                               60 + 10 * math.log10(2))
        self.assertEqual(m.combine_uncorrelated_levels([60]), 60)
        # Stable even for large offsets; does not exponentiate absolute dB.
        self.assertAlmostEqual(m.combine_uncorrelated_levels([3000, 3000]),
                               3000 + 10 * math.log10(2))

    def test_invalid_inputs(self):
        for fn, args in [(m.bridge_output, (5, 0, 1, 1, 1)),
                         (m.alias_frequency, (1, 0)),
                         (m.sound_pressure_level, (0,)),
                         (m.combine_uncorrelated_levels, ([],))]:
            with self.assertRaises(ValueError):
                fn(*args)


class SpectrumTests(unittest.TestCase):
    def test_dc_and_sine(self):
        x = [2 + 3 * math.sin(2 * math.pi * 5 * i / 100) for i in range(100)]
        a = dict(m.one_sided_amplitude_spectrum(x, 100))
        self.assertAlmostEqual(a[0], 2)
        self.assertAlmostEqual(a[5], 3)
        self.assertLess(a[10], 1e-12)

    def test_nyquist_not_doubled(self):
        a = dict(m.one_sided_amplitude_spectrum([(-1) ** i for i in range(100)], 100))
        self.assertAlmostEqual(a[50], 1)

    def test_odd_length_last_bin_doubled(self):
        x = [2 * math.cos(2 * math.pi * 4 * i / 9) for i in range(9)]
        a = m.one_sided_amplitude_spectrum(x, 9)
        self.assertAlmostEqual(a[-1][1], 2)

    def test_input_validation(self):
        for values, fs in [([1], 100), ([1, 2], 0), ([1, float("nan")], 1)]:
            with self.assertRaises(ValueError):
                m.one_sided_amplitude_spectrum(values, fs)


if __name__ == "__main__":
    unittest.main()
