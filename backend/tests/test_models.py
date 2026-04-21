import pytest
from pydantic import ValidationError

from models import PlantTypeIn


def test_plant_type_in_normalizes_uppercase_colors():
    model = PlantTypeIn(
        name="Kale",
        stage_durations_days=[7, 14, 10],
        stage_colors=["#4da6ff", "#ffffff", "#ff6fa3"],
    )
    assert model.stage_colors == ["#4DA6FF", "#FFFFFF", "#FF6FA3"]


def test_plant_type_in_requires_three_stage_durations():
    with pytest.raises(ValidationError):
        PlantTypeIn(name="Kale", stage_durations_days=[7, 14], stage_colors=["#4DA6FF", "#FFFFFF", "#FF6FA3"])


def test_plant_type_in_rejects_unsupported_colors():
    with pytest.raises(ValidationError):
        PlantTypeIn(
            name="Kale",
            stage_durations_days=[7, 14, 10],
            stage_colors=["#4DA6FF", "#FFFFFF", "#ABCDEF"],
        )
