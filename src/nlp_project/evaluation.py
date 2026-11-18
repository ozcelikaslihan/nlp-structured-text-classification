"""Classification, JSON, schema, and entity metrics."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from typing import Iterable

from .schema import ModelOutput
from .turkish import normalize_entity


def safe_divide(numerator: float, denominator: float) -> float:
    return numerator / denominator if denominator else 0.0


def entity_key(entity: dict[str, str], rule: str = "exact") -> tuple[str, str]:
    """Create a typed key under the stated matching rule."""

    if rule != "exact":
        raise ValueError("This project currently supports only normalized exact matching.")
    return entity["type"], normalize_entity(entity["text"])


def entity_counts(
    gold: Iterable[dict[str, str]],
    predicted: Iterable[dict[str, str]],
    rule: str = "exact",
) -> tuple[int, int, int]:
    """Return multiset TP, FP, FN so duplicate predictions are penalized."""

    gold_counter = Counter(entity_key(item, rule) for item in gold)
    predicted_counter = Counter(entity_key(item, rule) for item in predicted)
    true_positive = sum((gold_counter & predicted_counter).values())
    false_positive = sum((predicted_counter - gold_counter).values())
    false_negative = sum((gold_counter - predicted_counter).values())
    return true_positive, false_positive, false_negative


@dataclass
class MetricAccumulator:
    total: int = 0
    raw_json_success: int = 0
    cleaned_json_success: int = 0
    schema_valid: int = 0
    classification_correct: int = 0
    entity_tp: int = 0
    entity_fp: int = 0
    entity_fn: int = 0
    elapsed_seconds: float = 0.0

    def add(
        self,
        *,
        gold_category: str,
        gold_entities: list[dict[str, str]],
        raw_success: bool,
        clean_success: bool,
        validated: ModelOutput | None,
        elapsed_seconds: float,
        matching_rule: str,
    ) -> None:
        self.total += 1
        self.raw_json_success += int(raw_success)
        self.cleaned_json_success += int(clean_success)
        self.elapsed_seconds += elapsed_seconds
        if validated is None:
            # A failed or invalid output counts as wrong and predicts no entities.
            self.entity_fn += len(gold_entities)
            return
        self.schema_valid += 1
        self.classification_correct += int(validated.category == gold_category)
        predicted = (
            [{"text": text, "type": "PERSON"} for text in validated.entities.persons]
            + [{"text": text, "type": "ORGANIZATION"} for text in validated.entities.organizations]
            + [{"text": text, "type": "LOCATION"} for text in validated.entities.locations]
        )
        tp, fp, fn = entity_counts(gold_entities, predicted, matching_rule)
        self.entity_tp += tp
        self.entity_fp += fp
        self.entity_fn += fn

    def summary(self) -> dict[str, float | int]:
        precision = safe_divide(self.entity_tp, self.entity_tp + self.entity_fp)
        recall = safe_divide(self.entity_tp, self.entity_tp + self.entity_fn)
        f1 = safe_divide(2 * precision * recall, precision + recall)
        return {
            "n_samples": self.total,
            "raw_json_success_rate": safe_divide(self.raw_json_success, self.total),
            "cleaned_json_success_rate": safe_divide(self.cleaned_json_success, self.total),
            "schema_validity_rate": safe_divide(self.schema_valid, self.total),
            "classification_accuracy": safe_divide(self.classification_correct, self.total),
            "entity_precision_micro": precision,
            "entity_recall_micro": recall,
            "entity_f1_micro": f1,
            "entity_tp": self.entity_tp,
            "entity_fp": self.entity_fp,
            "entity_fn": self.entity_fn,
            "mean_response_seconds": safe_divide(self.elapsed_seconds, self.total),
        }

