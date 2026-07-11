import dhs_nutrition


def test_version():
    assert dhs_nutrition.__version__ == "0.1.0"


def test_top_level_exports():
    assert hasattr(dhs_nutrition, "VariableMap")
    assert hasattr(dhs_nutrition, "load_pr_recode")
    assert hasattr(dhs_nutrition, "compute_indicators")
    assert hasattr(dhs_nutrition, "IndicatorResult")
    assert hasattr(dhs_nutrition, "validate_against_factsheet")
