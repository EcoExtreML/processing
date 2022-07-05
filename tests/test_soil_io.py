from pathlib import Path
import numpy as np
import pytest
from PyStemmusScope import soil_io
from . import soil_data_folder


@pytest.fixture(autouse=True)
def coordinates():
    # Random location where data was available.
    lat, lon = 37.933802, -107.807522 #Lat, lon of Telluride, CO
    return (lat, lon)


@pytest.fixture(autouse=True)
def lat(coordinates):
    return coordinates[0]


@pytest.fixture(autouse=True)
def lon(coordinates):
    return coordinates[1]


@pytest.fixture(autouse=True)
def expected_values():
    """This function will return the values that were generated by the Matlab code,
    based on the coordinates (37.933802, -107.807522).
    This location was picked as a random site where data was available.

    The values determined by the Python code should be in agreement with these
    values.
    """
    expected_value_dict = {
        'Ks0': 75.9877,
        'FOC': np.array([0.1500, 0.1500, 0.2100, 0.2500, 0.2000, 0.1600]),
        'FOS': np.array([0.5500, 0.5700, 0.5500, 0.5100, 0.5500, 0.5700]),
        'MSOC': np.array([0.0079, 0.0090, 0.0056, 0.0020, 0.0017, 0.0017]),
        'fmax': 0.4028,
        'theta_s0': 0.4705,
        'SaturatedK': 1.0e-03 * np.array([0.8795, 0.7264, 0.2297, 0.1503, 0.1284, 0.1263]),
        'SaturatedMC': np.array([0.4705, 0.4572, 0.3999, 0.3769, 0.3659, 0.3546]),
        'ResidualMC': np.array([0.0637, 0.0617, 0.0562, 0.0536, 0.0516, 0.0485]),
        'Coefficient_n': np.array([1.5825, 1.6008, 1.5169, 1.4369, 1.4008, 1.4005]),
        'Coefficient_Alpha': np.array([0.0071, 0.0073, 0.0106, 0.0146, 0.0168, 0.0181]),
        'Coef_Lamda': np.array([0.1880, 0.1870, 0.1570, 0.1450, 0.1620, 0.1810]),
        'porosity': np.array([0.4705, 0.4572, 0.3999, 0.3769, 0.3659, 0.3546]),
        'fieldMC': ([0.2876, 0.2734, 0.2252, 0.2094, 0.2041, 0.1930]),
    }
    return expected_value_dict


def test_full_routine(tmp_path, coordinates):
    lat, lon = coordinates

    write_path = Path(tmp_path)
    matfile_path = write_path / 'soil_parameters.mat'
    soil_io.prepare_soil_data(soil_data_folder, write_path, lat, lon)

    assert matfile_path.exists()


def test_data_collection(lat, lon, expected_values):
    #pylint: disable=protected-access
    matfiledata = soil_io._collect_soil_data(soil_data_folder, lat, lon)

    assert sorted(matfiledata.keys()) == sorted(expected_values.keys())


def test_soil_composition_vars(lat, lon, expected_values):
    #pylint: disable=protected-access
    soil_composition_dict = soil_io._read_soil_composition(soil_data_folder, lat, lon)

    expected_vars = ['FOS', 'FOC', 'MSOC']

    for key in expected_vars:
        np.testing.assert_array_almost_equal(
            soil_composition_dict[key], expected_values[key]
        )


def test_hydraulic_vars(lat, lon, expected_values):
    #pylint: disable=protected-access
    hydraulic_dict = soil_io._read_hydraulic_parameters(
        soil_data_folder, lat, lon)

    expected_vars = ['Ks0','SaturatedMC', 'ResidualMC', 'Coefficient_n',
                     'Coefficient_Alpha', 'porosity', 'SaturatedK', 'fieldMC']

    for key in expected_vars:
        np.testing.assert_array_almost_equal(
            hydraulic_dict[key], expected_values[key], decimal=3
        )


def test_lambda_var(lat, lon, expected_values):
    #pylint: disable=protected-access
    lambda_dict = soil_io._read_lambda_coef(soil_data_folder / 'lambda', lat, lon)

    np.testing.assert_array_almost_equal(
        lambda_dict['Coef_Lamda'], expected_values['Coef_Lamda']
    )


def test_surf_var(lat, lon, expected_values):
    #pylint: disable=protected-access
    surf_dict = soil_io._read_surface_data(soil_data_folder, lat, lon)

    np.testing.assert_almost_equal(
        surf_dict['fmax'], expected_values['fmax'], decimal=4
    )
