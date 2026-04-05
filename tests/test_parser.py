"""Tests for ingredient list parsing."""

from babysafety.parser import parse_ingredient_list


def test_basic_comma_separated():
    result = parse_ingredient_list("Water, Glycerin, Retinol")
    assert len(result) == 3
    assert result[0].name == "Water"
    assert result[1].name == "Glycerin"
    assert result[2].name == "Retinol"


def test_strips_section_header():
    result = parse_ingredient_list("Ingredients: Water, Glycerin")
    assert len(result) == 2
    assert result[0].name == "Water"


def test_active_inactive_sections():
    text = "Active Ingredients: Zinc Oxide 14.5%, Inactive Ingredients: Water, Glycerin"
    result = parse_ingredient_list(text)
    assert result[0].name == "Zinc Oxide"
    assert result[0].section == "active"
    assert result[0].concentration == "14.5%"
    assert result[1].section == "inactive"


def test_parenthetical_synonyms():
    result = parse_ingredient_list("Niacinamide (Vitamin B3), Tocopherol (Vitamin E)")
    assert result[0].name == "Niacinamide"
    assert "Vitamin B3" in result[0].secondary_names
    assert result[1].name == "Tocopherol"
    assert "Vitamin E" in result[1].secondary_names


def test_slash_names():
    result = parse_ingredient_list("Aqua/Water/Eau, Glycerin")
    assert result[0].name == "Aqua"
    assert "Water" in result[0].secondary_names
    assert "Eau" in result[0].secondary_names


def test_concentration_extraction():
    result = parse_ingredient_list("Zinc Oxide (15%), Titanium Dioxide (5%)")
    assert result[0].name == "Zinc Oxide"
    assert result[0].concentration == "15%"
    assert result[1].concentration == "5%"


def test_and_connector():
    result = parse_ingredient_list("Methylisothiazolinone (and) Methylchloroisothiazolinone")
    assert len(result) == 2
    assert result[0].name == "Methylisothiazolinone"
    assert result[1].name == "Methylchloroisothiazolinone"


def test_newline_separated():
    text = "Water\nGlycerin\nRetinol"
    result = parse_ingredient_list(text)
    assert len(result) == 3


def test_may_contain_section():
    text = "Water, Glycerin, May Contain: Red 40, Yellow 5"
    result = parse_ingredient_list(text)
    assert result[2].section == "may_contain"


def test_less_than_prefix():
    text = "Less than 2% of: Phenoxyethanol, Citric Acid"
    result = parse_ingredient_list(text)
    assert len(result) == 2
    assert result[0].name == "Phenoxyethanol"


def test_semicolon_separator():
    result = parse_ingredient_list("Water; Glycerin; Retinol")
    assert len(result) == 3


def test_empty_input():
    result = parse_ingredient_list("")
    assert result == []


def test_preserves_position_order():
    result = parse_ingredient_list("A, B, C, D")
    positions = [r.position for r in result]
    assert positions == [0, 1, 2, 3]


def test_real_aveeno_snippet():
    """Test with a real-world ingredient list snippet."""
    text = (
        "Active Ingredients: Avobenzone (3%), Octisalate (5%), Octocrylene (7%), "
        "Inactive Ingredients: Water, Glycerin, Dimethicone, Isohexadecane, "
        "Cetyl Alcohol, Benzyl Alcohol"
    )
    result = parse_ingredient_list(text)
    assert result[0].section == "active"
    assert result[0].name == "Avobenzone"
    assert result[0].concentration == "3%"
    assert any(r.section == "inactive" for r in result)
