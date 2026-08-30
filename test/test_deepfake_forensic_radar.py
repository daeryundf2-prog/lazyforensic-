import os
import sys
import tempfile
import importlib.util
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = ROOT / 'skills' / 'deepfake-forensic-radar'

def load_module(name, relpath):
    path = ROOT / relpath
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(relpath)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

analyzer = load_module('analyze_deepfake_evidence', 'scripts/analyze_deepfake_evidence.py')

def test_skill_structure_and_references():
    assert (SKILL_ROOT / 'SKILL.md').exists()
    ref_dir = SKILL_ROOT / 'references'
    assert ref_dir.exists()
    
    expected_refs = [
        '01_generation_synthesis.md',
        '02_detection_forensics.md',
        '03_c2pa_watermarks.md',
        '04_legal_and_court.md',
        '05_evasion_and_limits.md'
    ]
    for ref in expected_refs:
        ref_path = ref_dir / ref
        assert ref_path.exists(), f'Missing reference: {ref}'
        with open(ref_path, 'r', encoding='utf-8') as f:
            content = f.read()
            assert len(content) > 100

def test_calculate_hashes():
    with tempfile.NamedTemporaryFile('wb', delete=False) as f:
        f.write(b'Deepfake Forensic Evidence Sample Test Data 2026')
        temp_path = f.name
        
    try:
        hashes = analyzer.calculate_hashes(temp_path)
        assert 'sha256' in hashes
        assert 'sha1' in hashes
        assert 'md5' in hashes
        assert hashes['size_bytes'] == 48
        assert len(hashes['sha256']) == 64
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

def test_c2pa_scanner_and_signatures():
    with tempfile.NamedTemporaryFile('wb', delete=False) as f:
        f.write(b'header_data_sample_c2pa.actions_test_c2pa.hash.data_trailer')
        temp_path = f.name
        
    try:
        res = analyzer.scan_c2pa_jumbf(temp_path)
        assert res['c2pa_detected'] is True
        assert res['manifest_type'] == 'Raw_Manifest_Signature'
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

def test_forensic_report_generation():
    with tempfile.NamedTemporaryFile('wb', delete=False) as f:
        f.write(b'sample image binary dummy')
        temp_path = f.name
        
    try:
        report = analyzer.generate_forensic_report(temp_path)
        assert 'meta' in report
        assert 'integrity_hashes' in report
        assert 'c2pa_provenance' in report
        assert 'spectral_analysis' in report
        
        md = analyzer.format_markdown_report(report)
        assert '# 디지털 미디어 딥페이크 포렌식 감정 보고서' in md
        assert 'SHA-256' in md
        assert '형사소송법' in md
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)
