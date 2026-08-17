from CosRayModifiedISO import CosRayModifiedISO
import numpy as np
import pandas as pd
import datetime as dt
from CosRayModifiedISO.internalFunctions.pythonModifiedISO import getAtomicMass
from CosRayModifiedISO.internalFunctions.rigidityEnergyConversionFunctions import (
    convertParticleEnergyToRigidity,
    convertParticleRigiditySpecToEnergySpec,
    convertParticleRigidityToEnergy,
    convertPerNucleonEnergyToTotalRigidity,
)
"""Unit tests for CosRayModifiedISO public functions against known-good outputs."""

import datetime as dt
import logging

import numpy as np
import pandas as pd
import pytest

from CosRayModifiedISO import CosRayModifiedISO


SPECTRUM_COLUMNS = [
    "Energy (MeV/n)",
    "d_Flux / d_E (cm-2 s-1 sr-1 (MeV/n)-1)",
    "Rigidity (GV/n)",
    "d_Flux / d_R (cm-2 s-1 sr-1 (GV/n)-1)",
]

TIMESTAMP_2001 = dt.datetime(2001, 10, 27, 0, 10, 35, tzinfo=dt.timezone.utc)
TIMESTAMP_2001_NAIVE = dt.datetime(2001, 10, 27, 0, 10, 35)
TIMESTAMP_1989 = dt.datetime(1989, 10, 27, tzinfo=dt.timezone.utc)

SOLAR_MODULATION_W = 19.25
SOLAR_MODULATION_W_HIGH = 111.3
PROTON_Z = 1
HELIUM_Z = 2
NITROGEN_Z = 7
SINGLE_ENERGY_MEV = 945.2
SINGLE_RIGIDITY_GV = 100.0
OULU_COUNT_RATE_PER_SECOND = 97.1
OULU_COUNT_RATE_PER_SECOND_LOW = 89.7


def assert_spectrum_rows_match_kgo(spectrum_df, kgo_rows, rtol=1e-7, atol=1e-16):
    assert list(spectrum_df.columns) == SPECTRUM_COLUMNS
    for row_index, expected_values in kgo_rows.items():
        np.testing.assert_allclose(
            spectrum_df.iloc[row_index].to_numpy(dtype=float),
            expected_values,
            rtol=rtol,
            atol=atol,
        )


class TestGetEnergyFluxesFromEnergies:
    def test_single_proton_energy_matches_kgo(self):
        flux = CosRayModifiedISO.getEnergyFluxesFromEnergies(
            SOLAR_MODULATION_W, PROTON_Z, SINGLE_ENERGY_MEV
        )

        np.testing.assert_allclose(flux, [0.00012418718988920136], rtol=1e-7)

    def test_energy_list_matches_kgo(self):
        flux = CosRayModifiedISO.getEnergyFluxesFromEnergies(
            SOLAR_MODULATION_W, PROTON_Z, [100.0, SINGLE_ENERGY_MEV, 10000.0]
        )

        np.testing.assert_allclose(
            flux,
            [1.4279244900684913e-4, 1.2418718988920136e-4, 2.2074683783856464e-6],
            rtol=1e-7,
        )

    def test_helium_energy_matches_kgo(self):
        flux = CosRayModifiedISO.getEnergyFluxesFromEnergies(
            SOLAR_MODULATION_W, HELIUM_Z, SINGLE_ENERGY_MEV
        )

        np.testing.assert_allclose(flux, [1.1540997102282939e-5], rtol=1e-7)


class TestGetRigidityFluxesFromRigidities:
    def test_single_proton_rigidity_matches_kgo(self):
        flux = CosRayModifiedISO.getRigidityFluxesFromRigidities(
            20.7, PROTON_Z, SINGLE_RIGIDITY_GV
        )

        np.testing.assert_allclose(flux, [6.003171442890822e-6], rtol=1e-7)

    def test_rigidity_list_matches_kgo(self):
        flux = CosRayModifiedISO.getRigidityFluxesFromRigidities(
            20.7, PROTON_Z, [1.0, 10.0, SINGLE_RIGIDITY_GV]
        )

        np.testing.assert_allclose(
            flux,
            [0.13749995510744167, 2.7282841756380797e-3, 6.003171442890822e-6],
            rtol=1e-7,
        )


class TestGetSpectrumUsingSolarModulation:
    KGO_NITROGEN_ROWS = {
        0: [11.294627058970837, 1.899594204175842e-8, 0.07783495116549362, 5.510632880080903e-6],
        4: [28.370820458389794, 5.782005269637756e-8, 0.12340015168771055, 2.6558065814862043e-5],
    }

    @pytest.mark.parametrize(
        "solar_modulation_w, kgo_rows",
        [
            (
                SOLAR_MODULATION_W,
                {
                    0: [11.294627058970837, 1.4894186545984357e-5, 0.14602203682248496, 2.2903914182920543e-3],
                    4: [28.370820458389794, 4.7508921433941104e-5, 0.23247365738420114, 1.1425700868993163e-2],
                },
            ),
            (
                SOLAR_MODULATION_W_HIGH,
                {
                    0: [11.294627058970837, 9.071339696106846e-8, 0.14602203682248496, 1.3949683340025622e-5],
                    4: [28.370820458389794, 7.106230880874699e-7, 0.23247365738420114, 1.7090193988885232e-4],
                },
            ),
        ],
        ids=["W=19.25", "W=111.3"],
    )
    def test_proton_spectrum_matches_kgo(self, solar_modulation_w, kgo_rows):
        spectrum = CosRayModifiedISO.getSpectrumUsingSolarModulation(
            solar_modulation_w, PROTON_Z
        )

        assert len(spectrum) == 50
        assert_spectrum_rows_match_kgo(spectrum, kgo_rows)

    def test_nitrogen_spectrum_matches_kgo(self):
        spectrum = CosRayModifiedISO.getSpectrumUsingSolarModulation(
            SOLAR_MODULATION_W, NITROGEN_Z
        )

        assert_spectrum_rows_match_kgo(spectrum, self.KGO_NITROGEN_ROWS)

    def test_ssn_alias_matches_solar_modulation_spectrum(self):
        from_w = CosRayModifiedISO.getSpectrumUsingSolarModulation(
            SOLAR_MODULATION_W, PROTON_Z
        )
        from_ssn = CosRayModifiedISO.getSpectrumUsingSSN(SOLAR_MODULATION_W, PROTON_Z)

        pd.testing.assert_frame_equal(from_w, from_ssn)


class TestGetSpectrumUsingTimestamp:
    KGO_2001_PROTON_ROWS = {
        0: [11.294627058970837, 2.2908350489336754e-7, 0.14602203682248496, 3.522789862072042e-5],
        4: [28.370820458389794, 1.5467880437852272e-6, 0.23247365738420114, 3.719961843503175e-4],
    }
    KGO_1989_PROTON_ROWS = {
        0: [11.294627058970837, 1.9323156312451008e-9, 0.14602203682248496, 2.971467508864127e-7],
        4: [28.370820458389794, 2.6872869897917297e-8, 0.23247365738420114, 6.462815060365037e-6],
    }

    @pytest.mark.parametrize(
        "timestamp, kgo_rows",
        [
            (TIMESTAMP_2001, KGO_2001_PROTON_ROWS),
            (TIMESTAMP_2001_NAIVE, KGO_2001_PROTON_ROWS),
            (TIMESTAMP_1989, KGO_1989_PROTON_ROWS),
        ],
        ids=["2001-utc", "2001-naive", "1989-utc"],
    )
    def test_proton_spectrum_matches_kgo(self, timestamp, kgo_rows):
        spectrum = CosRayModifiedISO.getSpectrumUsingTimestamp(
            timestamp, atomicNumber=PROTON_Z
        )

        assert len(spectrum) == 50
        assert_spectrum_rows_match_kgo(spectrum, kgo_rows)

    def test_naive_timestamp_logs_utc_assumption(self, caplog):
        with caplog.at_level(logging.WARNING):
            CosRayModifiedISO.getSpectrumUsingTimestamp(
                TIMESTAMP_2001_NAIVE, atomicNumber=PROTON_Z
            )

        assert "does not have timezone info" in caplog.text
        assert "Assuming UTC" in caplog.text


class TestGetSpectrumUsingOULUcountRate:
    @pytest.mark.parametrize(
        "oulu_count_rate, kgo_rows",
        [
            (
                OULU_COUNT_RATE_PER_SECOND,
                {
                    0: [11.294627058970837, 2.2908350489336754e-7, 0.14602203682248496, 3.522789862072042e-5],
                    4: [28.370820458389794, 1.5467880437852272e-6, 0.23247365738420114, 3.719961843503175e-4],
                },
            ),
            (
                OULU_COUNT_RATE_PER_SECOND_LOW,
                {
                    0: [11.294627058970837, 1.4750494967144138e-8, 0.14602203682248496, 2.268294880287755e-6],
                    4: [28.370820458389794, 1.5267904588779325e-7, 0.23247365738420114, 3.67186847148867e-5],
                },
            ),
        ],
        ids=["97.1_s-1", "89.7_s-1"],
    )
    def test_proton_spectrum_matches_kgo(self, oulu_count_rate, kgo_rows):
        spectrum = CosRayModifiedISO.getSpectrumUsingOULUcountRate(
            oulu_count_rate, PROTON_Z
        )

        assert len(spectrum) == 50
        assert_spectrum_rows_match_kgo(spectrum, kgo_rows)

    @pytest.mark.parametrize(
        "timestamp",
        [TIMESTAMP_2001, TIMESTAMP_1989],
        ids=["2001", "1989"],
    )
    def test_matches_timestamp_spectrum_for_same_count_rate(self, timestamp):
        oulu_count_rate = CosRayModifiedISO.getOULUcountRateForTimestamp(timestamp)
        from_oulu = CosRayModifiedISO.getSpectrumUsingOULUcountRate(
            oulu_count_rate, PROTON_Z
        )
        from_timestamp = CosRayModifiedISO.getSpectrumUsingTimestamp(
            timestamp, atomicNumber=PROTON_Z
        )

        pd.testing.assert_frame_equal(from_oulu, from_timestamp)


class TestGetOULUcountRateForTimestamp:
    @pytest.mark.parametrize(
        "timestamp, expected_count_rate",
        [
            (TIMESTAMP_2001, OULU_COUNT_RATE_PER_SECOND),
            (TIMESTAMP_1989, 84.6),
        ],
        ids=["2001", "1989"],
    )
    def test_count_rate_matches_kgo(self, timestamp, expected_count_rate):
        count_rate = CosRayModifiedISO.getOULUcountRateForTimestamp(timestamp)

        assert count_rate == pytest.approx(expected_count_rate)


class TestGetWparameterFromOULUcountRate:
    @pytest.mark.parametrize(
        "oulu_count_rate, expected_w",
        [
            (OULU_COUNT_RATE_PER_SECOND, 96.882),
            (OULU_COUNT_RATE_PER_SECOND_LOW, 138.174),
        ],
        ids=["97.1_s-1", "89.7_s-1"],
    )
    def test_matches_published_linear_relation(self, oulu_count_rate, expected_w):
        w_parameter = CosRayModifiedISO.getWparameterFromOULUcountRate(oulu_count_rate)
        expected_from_formula = (-0.093 * oulu_count_rate * 60) + 638.7

        assert w_parameter == pytest.approx(expected_from_formula)
        assert w_parameter == pytest.approx(expected_w)


class TestGetModifiedISO_GCR_Flux_Single:
    def test_matches_energy_flux_wrapper(self):
        single_flux = CosRayModifiedISO.getModifiedISO_GCR_Flux_Single(
            SOLAR_MODULATION_W, PROTON_Z, SINGLE_ENERGY_MEV
        )
        wrapped_flux = CosRayModifiedISO.getEnergyFluxesFromEnergies(
            SOLAR_MODULATION_W, PROTON_Z, SINGLE_ENERGY_MEV
        )

        assert single_flux == pytest.approx(wrapped_flux[0])
        assert single_flux == pytest.approx(0.00012418718988920136)


class TestQuantityConversions:
    def test_atomic_masses_match_kgo(self):
        assert CosRayModifiedISO.getAtomicMass(PROTON_Z) == pytest.approx(1.0)
        assert CosRayModifiedISO.getAtomicMass(HELIUM_Z) == pytest.approx(4.0)
        assert CosRayModifiedISO.getAtomicMass(NITROGEN_Z) == pytest.approx(14.0)

    def test_energy_rigidity_roundtrip_matches_kgo(self):
        energies = pd.Series([100.0, SINGLE_ENERGY_MEV, 10000.0])
        rigidities = CosRayModifiedISO.convertParticleEnergyToRigidity(
            energies, particleMassAU=1.0, particleChargeAU=PROTON_Z
        )
        recovered_energies = CosRayModifiedISO.convertParticleRigidityToEnergy(
            rigidities, particleMassAU=1.0, particleChargeAU=PROTON_Z
        )

        np.testing.assert_allclose(
            rigidities.to_numpy(dtype=float),
            [0.4445834203910546, 1.6331296935558517, 10.897955852757935],
            rtol=1e-7,
        )
        np.testing.assert_allclose(
            recovered_energies.to_numpy(dtype=float),
            energies.to_numpy(dtype=float),
            rtol=1e-12,
        )

    def test_energy_and_rigidity_spectra_roundtrip_matches_kgo(self):
        energies = pd.Series([100.0, SINGLE_ENERGY_MEV, 10000.0])
        energy_flux = pd.Series(
            CosRayModifiedISO.getEnergyFluxesFromEnergies(
                SOLAR_MODULATION_W, PROTON_Z, energies.tolist()
            )
        )
        rigidity = CosRayModifiedISO.convertParticleEnergyToRigidity(
            energies, particleMassAU=1.0, particleChargeAU=PROTON_Z
        )
        rigidity_flux = CosRayModifiedISO.convertParticleEnergySpecToRigiditySpec(
            energies, energy_flux, particleMassAU=1.0, particleChargeAU=PROTON_Z
        )
        recovered_energy_flux = CosRayModifiedISO.convertParticleRigiditySpecToEnergySpec(
            rigidity, rigidity_flux, particleMassAU=1.0, particleChargeAU=PROTON_Z
        )

        np.testing.assert_allclose(
            rigidity_flux.to_numpy(dtype=float),
            [0.06114308194616754, 0.10768080324250766, 2.199332101040483e-3],
            rtol=1e-7,
        )
        np.testing.assert_allclose(
            recovered_energy_flux.to_numpy(dtype=float),
            energy_flux.to_numpy(dtype=float),
            rtol=1e-12,
        )
