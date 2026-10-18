from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path


def test_source_urls_are_revision_pinned():
    path = Path(__file__).resolve().parents[1] / "scripts" / "collect_technical_corpus.py"
    spec = spec_from_file_location("collect_technical_corpus", path)
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    assert module.source_url("CVE-2017-0144").endswith("/cves/2017/0xxx/CVE-2017-0144.json")
    assert module.REVISION in module.source_url("CVE-2024-3094")
