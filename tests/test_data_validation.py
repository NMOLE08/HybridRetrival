from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path


def test_missing_dataset_is_not_accepted():
    spec = spec_from_file_location("validator", Path(__file__).resolve().parents[1] / "scripts" / "validate_dataset.py")
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    result = module.validate(Path(__file__).parent / "not_a_dataset")
    assert not result["valid"]
    assert len(result["errors"]) == 6
