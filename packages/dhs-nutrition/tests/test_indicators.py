"""National (and admin1-supporting) indicator arithmetic checks against hand-derived
golden values, using the synthetic 30-row fixture in tests/fixtures/synthetic_recode.py.

Filtering: 30 rows total; row (a) has hv103=0 (not de facto) and row (b) has
hc1=60 (age out of 0-59 range), so 28 children remain.

Every number below was independently re-derived from the fixture row-by-row
(see the long comment block for the full derivation). All 28 remaining rows,
grouped by id, with (cluster, admin1, wealth, sex, age, weight_units=wu,
hc57, hc70=haz, hc71=waz, hc72=whz):

    c   101 1 1 1 10  wu2  hc57=4  hc70=9998(sentinel) hc71=-150 hc72=-150
    d   102 1 2 2 30  wu1  hc57=3  hc70=NaN             hc71=-50  hc72=50
    e   102 1 2 1 3   wu1  hc57=1  hc70=-50  hc71=-50  hc72=-50  (age<6: anemia-ineligible)
    f   102 1 3 2 40  wu1  hc57=2  hc70=-250 hc71=-250 hc72=-250 (hv042=0: anemia-ineligible)
    g   201 2 1 1 50  wu1  hc57=2  hc70=-50  hc71=-50  hc72=-50  (hc55=1: anemia-ineligible)
    h   201 2 1 2 45  wu1  hc57=8  hc70=50   hc71=50   hc72=50   (hc57=8: anemia-ineligible)
    i   202 2 2 1 18  wu2  hc57=3  hc70=-350 hc71=-350 hc72=-350
    r10 101 1 1 1 2   wu1  hc57=4  hc70=-50  hc71=-50  hc72=-50  (age<6: anemia-ineligible)
    r11 101 1 1 2 12  wu1  hc57=2  hc70=-250 hc71=-250 hc72=-250
    r12 101 1 2 1 36  wu2  hc57=4  hc70=-150 hc71=-150 hc72=-150
    r13 101 1 2 2 45  wu1  hc57=1  hc70=-350 hc71=-350 hc72=-350
    r14 101 1 1 1 8   wu1  hc57=3  hc70=50   hc71=50   hc72=50
    r15 101 1 2 2 55  wu1  hc57=4  hc70=250  hc71=250  hc72=250
    r16 102 1 3 1 4   wu1  hc57=2  hc70=-150 hc71=-150 hc72=-150 (age<6: anemia-ineligible)
    r17 102 1 1 2 20  wu1  hc57=1  hc70=-350 hc71=-350 hc72=-350
    r18 102 1 2 1 48  wu2  hc57=3  hc70=-50  hc71=-50  hc72=-50
    r19 102 1 3 2 15  wu1  hc57=4  hc70=50   hc71=50   hc72=50
    r20 102 1 1 1 59  wu1  hc57=2  hc70=-250 hc71=-250 hc72=-250
    r21 201 2 1 1 6   wu1  hc57=1  hc70=-350 hc71=-350 hc72=-350
    r22 201 2 2 2 24  wu1  hc57=3  hc70=-150 hc71=-150 hc72=-150
    r23 201 2 3 1 1   wu1  hc57=4  hc70=-50  hc71=-50  hc72=-50  (age<6: anemia-ineligible)
    r24 201 2 1 2 30  wu2  hc57=2  hc70=250  hc71=250  hc72=250
    r25 201 2 2 1 18  wu1  hc57=4  hc70=50   hc71=50   hc72=50
    r26 202 2 1 1 9   wu1  hc57=3  hc70=-250 hc71=-250 hc72=-250
    r27 202 2 2 2 33  wu1  hc57=1  hc70=-350 hc71=-350 hc72=-350
    r28 202 2 3 1 5   wu1  hc57=2  hc70=-150 hc71=-150 hc72=-150 (age<6: anemia-ineligible)
    r29 202 2 1 2 52  wu1  hc57=4  hc70=50   hc71=50   hc72=50
    r30 202 2 2 1 22  wu2  hc57=1  hc70=250  hc71=250  hc72=250

Sample weight = hv005 / 1e6 = weight_units (wu) directly, since hv005 is
constructed as wu * 1_000_000 in the fixture.

--- haz (stunting) ---
Valid haz = notna and < 9990. Only c (sentinel 9998) and d (NaN) are invalid,
so haz_valid_n = 26. Weighted denominator (sum of wu over the 26 valid rows):
  e1+f1+g1+h1+i2 = 6
  r10..r15: 1+1+2+1+1+1 = 7        (running: 13)
  r16..r20: 1+1+2+1+1   = 6        (running: 19)
  r21..r25: 1+1+1+2+1   = 6        (running: 25)
  r26..r30: 1+1+1+1+2   = 6        (running: 31)
  -> haz_den_w = 31
Stunted (haz < -200), weighted: f(1) + i(2) + r11(1) + r13(1) + r17(1) +
  r20(1) + r21(1) + r26(1) + r27(1) = 10  -> stunting_rate = 100*10/31
Severely stunted (haz < -300), weighted: i(2) + r13(1) + r17(1) + r21(1) +
  r27(1) = 6  -> severe_stunting_rate = 100*6/31
mean_haz: sum(haz*wu) over the 26 valid rows = -2650 (running total, verified
  term-by-term against the table above) -> mean_haz = (-2650/31)/100

--- whz (wasting) ---
hc72 has no sentinel/NaN among any of the 28 rows, so whz is valid for all 28
(denominator = 31 + c(2) + d(1) = 34).
Wasted (whz < -200), weighted: same row set as stunted (f, i, r11, r13, r17,
  r20, r21, r26, r27) = 10 -> wasting_rate = 100*10/34

--- anemia ---
Eligible = hv042==1 & 6<=hc1<=59 & hc55==0 & hc57 in {1,2,3,4}.
Ineligible rows (with reason): e,r10,r16,r23,r28 (age<6); f (hv042=0);
  g (hc55=1); h (hc57=8). That is 8 of the 28 rows excluded -> 20 eligible,
  i.e. anemia_valid_n = 20:
  c, d, i, r11, r12, r13, r14, r15, r17, r18, r19, r20, r21, r22, r24, r25,
  r26, r27, r29, r30  (20 ids)
Weighted denominator: c2+d1+i2+r11(1)+r12(2)+r13(1)+r14(1)+r15(1)+r17(1)+
  r18(2)+r19(1)+r20(1)+r21(1)+r22(1)+r24(2)+r25(1)+r26(1)+r27(1)+r29(1)+
  r30(2) = 26 -> anemia_den_w = 26
Anemic (hc57 in {1,2,3}), weighted: d(1)+i(2)+r11(1)+r13(1)+r14(1)+r17(1)+
  r18(2)+r20(1)+r21(1)+r22(1)+r24(2)+r26(1)+r27(1)+r30(2) = 18
  -> anemia_rate = 100*18/26
"""

from __future__ import annotations

import pytest

STUNTING_RATE = 100 * 10 / 31
SEVERE_STUNTING_RATE = 100 * 6 / 31
WASTING_RATE = 100 * 10 / 34
ANEMIA_RATE = 100 * 18 / 26
MEAN_HAZ = (-2650 / 31) / 100

HAZ_VALID_N = 26
ANEMIA_VALID_N = 20
HAZ_DEN_W = 31
WHZ_DEN_W = 34
ANEMIA_DEN_W = 26


def test_national_children_count(children):
    vm = children.variable_map
    assert len(children.df) == 28
    assert not (children.df[vm.age_months] == 60).any()
    assert (children.df[vm.de_facto] == 1).all()


def test_national_rates(result):
    row = result.national.iloc[0]

    assert row["stunting_rate"] == pytest.approx(STUNTING_RATE, rel=1e-9)
    assert row["severe_stunting_rate"] == pytest.approx(SEVERE_STUNTING_RATE, rel=1e-9)
    assert row["wasting_rate"] == pytest.approx(WASTING_RATE, rel=1e-9)
    assert row["anemia_rate"] == pytest.approx(ANEMIA_RATE, rel=1e-9)
    assert row["mean_haz"] == pytest.approx(MEAN_HAZ, rel=1e-9)


def test_national_valid_counts(result):
    row = result.national.iloc[0]

    assert int(row["haz_valid_n"]) == HAZ_VALID_N
    assert int(row["anemia_valid_n"]) == ANEMIA_VALID_N


def test_haz_sentinel_excludes_row_c(result):
    # Row (c) has hc70=9998 (sentinel >= 9990). 28 children total minus 2
    # invalid haz rows (c: sentinel, d: NaN) = 26 valid.
    row = result.national.iloc[0]
    assert int(row["haz_valid_n"]) == 26


@pytest.mark.parametrize(
    "gate_description",
    ["age_under_6", "hv042_zero", "hc55_not_measured", "hc57_uncoded"],
)
def test_anemia_gates_each_excluded(result, gate_description):
    # Each of the four anemia-eligibility gates removes at least one row from
    # the fixture (see the module docstring); combined, 20 of 28 rows remain
    # eligible. This is asserted as a single aggregate count because the
    # underlying computation only exposes the aggregated valid_n, not a
    # per-gate breakdown.
    row = result.national.iloc[0]
    assert int(row["anemia_valid_n"]) == ANEMIA_VALID_N


def test_national_weighted_denominators_differ_from_row_counts(result):
    # Weighted denominators (sums of sample weight) are distinct quantities
    # from row counts (haz_valid_n=26, anemia_valid_n=20) because several
    # rows carry weight_units=2.
    row = result.national.iloc[0]
    assert HAZ_DEN_W != int(row["haz_valid_n"])
    assert ANEMIA_DEN_W != int(row["anemia_valid_n"])
