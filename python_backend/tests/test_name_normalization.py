from name_normalization import normalize


def test_normalize_removes_punctuation_and_applies_aliases():
    assert normalize("  Bangalore & Urban! ") == "bengaluru urban"
    assert normalize("NCT of Delhi") == "nct of delhi"
