import json

from nlp_project.parsing import parse_raw_and_cleaned, validate_schema


VALID = {
    "category": "spor",
    "entities": {"persons": [], "organizations": ["Fenerbahçe"], "locations": []},
}


def test_raw_json_success() -> None:
    result = parse_raw_and_cleaned(json.dumps(VALID, ensure_ascii=False))
    assert result.raw_success is True
    assert result.clean_success is True
    assert validate_schema(result.parsed)[0] is True


def test_fenced_json_only_succeeds_after_cleaning() -> None:
    raw = "```json\n" + json.dumps(VALID, ensure_ascii=False) + "\n```"
    result = parse_raw_and_cleaned(raw)
    assert result.raw_success is False
    assert result.clean_success is True


def test_conversational_wrapper_is_removed() -> None:
    raw = "İşte JSON çıktısı: " + json.dumps(VALID, ensure_ascii=False) + " Teşekkürler."
    result = parse_raw_and_cleaned(raw)
    assert result.raw_success is False
    assert result.clean_success is True


def test_single_quotes_are_not_silently_repaired() -> None:
    result = parse_raw_and_cleaned("{'category': 'spor', 'entities': []}")
    assert result.clean_success is False


def test_extra_field_fails_schema() -> None:
    invalid = {**VALID, "explanation": "extra"}
    assert validate_schema(invalid)[0] is False


def test_missing_entity_type_list_fails_schema() -> None:
    invalid = {"category": "spor", "entities": {"persons": [], "organizations": []}}
    assert validate_schema(invalid)[0] is False

