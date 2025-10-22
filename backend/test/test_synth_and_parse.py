import os
import json
from backend.synth.dataset_generator import main as gen_main
from backend.cli.validate_labels import main as validate_main

def test_generate_small_set(tmp_path, monkeypatch):
    # generate 5 PDFs into a temp directory by monkeypatching OUTPUT_DIR
    monkeypatch.setenv("PYTHONPATH", os.getcwd())
    # run generator for 5 files (it writes to synthetic_data/)
    gen_main(5)
    assert os.path.exists("synthetic_data/pdfs")
    labels = json.load(open("synthetic_data/labels.json"))
    assert len(labels) >= 5

def test_validation_runs():
    # run validation (this will create validation_report.json)
    validate_main("synthetic_data/labels.json")
    assert os.path.exists("validation_report.json")
    rep = json.load(open("validation_report.json"))
    assert "details" in rep
