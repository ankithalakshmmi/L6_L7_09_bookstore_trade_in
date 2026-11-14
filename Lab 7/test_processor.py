from hypothesis import given, settings, strategies as st
from processor import verify_isbn10_format, calculate_depreciation_factor, lookup_condition_multiplier

# Plain random text rarely hits the "interesting" shapes, so each test also mixes in
# near-valid inputs built from the expected format.

isbn_like = st.builds(
    lambda body, sep: sep.join([body[:1], body[1:4], body[4:9], body[9:]]),
    st.text(alphabet="0123456789Xx-²٣ ", min_size=0, max_size=12),
    st.sampled_from(["-", "", " "]),
)

ratio_like = st.builds(
    lambda a, b: f"{a}/{b}",
    st.floats(allow_nan=True, allow_infinity=True) | st.integers(-100, 100),
    st.floats(allow_nan=True, allow_infinity=True) | st.integers(-100, 100),
)

condition_like = st.sampled_from(
    ["MINT", "like_new", " Very_Good ", "GOOD", "poor", "", "FAIR", "LIKE NEW", "ı", "ß"]
)


@settings(max_examples=500)
@given(st.text() | st.none() | isbn_like)
def test_verify_isbn10_format_no_crash(s):
    try:
        result = verify_isbn10_format(s)
    except Exception as e:
        assert False, f"verify_isbn10_format crashed on {s!r} with: {type(e).__name__}: {e}"
    assert result is None or result.startswith("Group ")


@settings(max_examples=500)
@given(st.text() | st.none() | ratio_like)
def test_calculate_depreciation_factor_safe(s):
    try:
        result = calculate_depreciation_factor(s)
    except Exception as e:
        assert False, f"calculate_depreciation_factor crashed on {s!r} with: {type(e).__name__}: {e}"
    # A depreciation factor must be a real number between 0.1 and 1.0 (or None if input invalid)
    assert result is None or 0.1 <= result <= 1.0, f"Out-of-range factor {result!r} for {s!r}"


@settings(max_examples=500)
@given(st.text() | st.none() | condition_like)
def test_lookup_condition_multiplier_safe(s):
    try:
        result = lookup_condition_multiplier(s)
    except Exception as e:
        assert False, f"lookup_condition_multiplier crashed on {s!r} with: {type(e).__name__}: {e}"
    assert result is None or result in {1.25, 1.00, 0.80, 0.60, 0.30}