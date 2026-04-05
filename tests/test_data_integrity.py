"""Validate all YAML ingredient files conform to the schema."""

from pathlib import Path

import yaml

DATA_DIR = Path(__file__).parent.parent / "data"
INGREDIENTS_DIR = DATA_DIR / "ingredients"

VALID_RATINGS = {"safe", "caution", "avoid", "insufficient_data"}
VALID_CONFIDENCE = {"high", "moderate", "low", "insufficient"}
VALID_EVIDENCE_STRENGTH = {"definitive", "strong", "moderate", "limited"}
VALID_EXPOSURE_ROUTES = {"topical", "oral", "inhalation", "multiple"}
REQUIRED_FIELDS = {"id", "name", "category", "product_types", "safety", "sources"}
REQUIRED_STAGE_FIELDS = {"rating", "summary"}


def _load_all_ingredients() -> list[tuple[Path, dict]]:
    results = []
    for yaml_path in sorted(INGREDIENTS_DIR.rglob("*.yaml")):
        with open(yaml_path) as f:
            data = yaml.safe_load(f)
        if data:
            results.append((yaml_path, data))
    return results


def _load_source_refs() -> set[str]:
    sources_path = DATA_DIR / "sources.yaml"
    if sources_path.exists():
        with open(sources_path) as f:
            data = yaml.safe_load(f)
        return set(data.keys()) if data else set()
    return set()


class TestDataIntegrity:
    """Validate all ingredient YAML files."""

    def setup_method(self):
        self.ingredients = _load_all_ingredients()
        self.source_refs = _load_source_refs()

    def test_at_least_one_ingredient_exists(self):
        assert len(self.ingredients) > 0, "No ingredient YAML files found"

    def test_required_fields_present(self):
        for path, data in self.ingredients:
            for field in REQUIRED_FIELDS:
                assert field in data, f"{path.name}: missing required field '{field}'"

    def test_id_matches_filename(self):
        for path, data in self.ingredients:
            expected_id = path.stem
            assert data["id"] == expected_id, (
                f"{path.name}: id '{data['id']}' doesn't match filename '{expected_id}'"
            )

    def test_valid_ratings(self):
        for path, data in self.ingredients:
            for stage_name in ("pregnancy", "nursing", "baby"):
                if stage_name in data.get("safety", {}):
                    stage = data["safety"][stage_name]
                    assert stage["rating"] in VALID_RATINGS, (
                        f"{path.name}/{stage_name}: invalid rating '{stage['rating']}'"
                    )

    def test_valid_rating_confidence(self):
        """rating_confidence (or legacy `confidence`) must be a valid enum value."""
        for path, data in self.ingredients:
            value = data.get("rating_confidence", data.get("confidence"))
            if value is not None:
                assert value in VALID_CONFIDENCE, (
                    f"{path.name}: invalid rating_confidence '{value}'"
                )

    def test_valid_evidence_strength(self):
        """evidence_strength on each stage must be a valid enum value if set."""
        for path, data in self.ingredients:
            for stage_name in ("pregnancy", "nursing", "baby"):
                if stage_name in data.get("safety", {}):
                    stage = data["safety"][stage_name]
                    if "evidence_strength" in stage:
                        assert stage["evidence_strength"] in VALID_EVIDENCE_STRENGTH, (
                            f"{path.name}/{stage_name}: invalid evidence_strength "
                            f"'{stage['evidence_strength']}'"
                        )

    def test_valid_exposure_routes(self):
        for path, data in self.ingredients:
            for stage_name in ("pregnancy", "nursing", "baby"):
                if stage_name in data.get("safety", {}):
                    stage = data["safety"][stage_name]
                    if "exposure_route" in stage:
                        assert stage["exposure_route"] in VALID_EXPOSURE_ROUTES, (
                            f"{path.name}/{stage_name}: invalid exposure_route"
                        )

    def test_stage_safety_has_required_fields(self):
        for path, data in self.ingredients:
            for stage_name in ("pregnancy", "nursing", "baby"):
                if stage_name in data.get("safety", {}):
                    stage = data["safety"][stage_name]
                    for field in REQUIRED_STAGE_FIELDS:
                        assert field in stage, (
                            f"{path.name}/{stage_name}: missing required field '{field}'"
                        )

    def test_source_refs_resolve(self):
        for path, data in self.ingredients:
            for source in data.get("sources", []):
                if "ref" in source:
                    assert source["ref"] in self.source_refs, (
                        f"{path.name}: source ref '{source['ref']}' not found in sources.yaml"
                    )

    def test_no_duplicate_ids(self):
        ids = [data["id"] for _, data in self.ingredients]
        assert len(ids) == len(set(ids)), f"Duplicate ingredient IDs found: {ids}"

    def test_no_alias_conflicts(self):
        alias_map: dict[str, str] = {}
        for path, data in self.ingredients:
            all_names = [data["name"]] + data.get("aliases", [])
            for name in all_names:
                lower = name.lower()
                if lower in alias_map:
                    assert alias_map[lower] == data["id"], (
                        f"Alias conflict: '{name}' claimed by both "
                        f"'{alias_map[lower]}' and '{data['id']}'"
                    )
                alias_map[lower] = data["id"]

    def test_aliases_is_list(self):
        for path, data in self.ingredients:
            if "aliases" in data:
                assert isinstance(data["aliases"], list), (
                    f"{path.name}: aliases should be a list"
                )

    def test_product_types_is_list(self):
        for path, data in self.ingredients:
            assert isinstance(data["product_types"], list), (
                f"{path.name}: product_types should be a list"
            )
