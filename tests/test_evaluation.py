from nlp_project.evaluation import entity_counts
from nlp_project.turkish import normalize_entity, turkish_lower


def test_turkish_i_lowercase() -> None:
    assert turkish_lower("İSTANBUL") == "istanbul"
    assert turkish_lower("IŞIK") == "ışık"


def test_normalized_exact_entity_match() -> None:
    gold = [{"text": "İSTANBUL", "type": "LOCATION"}]
    predicted = [{"text": "istanbul", "type": "LOCATION"}]
    assert entity_counts(gold, predicted) == (1, 0, 0)


def test_wrong_type_does_not_match() -> None:
    gold = [{"text": "Ankara", "type": "LOCATION"}]
    predicted = [{"text": "Ankara", "type": "ORGANIZATION"}]
    assert entity_counts(gold, predicted) == (0, 1, 1)


def test_combining_dot_is_avoided() -> None:
    assert normalize_entity("İSTANBUL") == "istanbul"
