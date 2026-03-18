import pytest
from unittest.mock import patch, MagicMock
import sys
from cli import main

@pytest.fixture
def mock_detector():
    with patch("cli.SecretDetector") as mock:
        yield mock

@pytest.fixture
def mock_format_report():
    with patch("cli.format_report") as mock:
        yield mock

def test_cli_help(capsys):
    with patch.object(sys, 'argv', ['cli.py', '--help']):
        with pytest.raises(SystemExit) as e:
            main()
        assert e.value.code == 0
    out, err = capsys.readouterr()
    assert "LLM Secrets Leak Detector CLI" in out

def test_cli_text_input(mock_detector, mock_format_report):
    mock_instance = mock_detector.return_value
    mock_instance.scan.return_value = []
    mock_format_report.return_value = "Mock Report"
    
    with patch.object(sys, 'argv', ['cli.py', '--text', 'my secret']):
        main()
    
    mock_instance.scan.assert_called_with('my secret')
    mock_format_report.assert_called()

def test_cli_file_input(mock_detector, mock_format_report, tmp_path):
    f = tmp_path / "test.txt"
    f.write_text("file content")
    
    mock_instance = mock_detector.return_value
    mock_instance.scan_stream.return_value = []
    mock_format_report.return_value = "Mock Report"
    
    with patch.object(sys, 'argv', ['cli.py', str(f)]):
        main()
    
    # scan_stream is called with a file object
    args, kwargs = mock_instance.scan_stream.call_args
    assert args[0].name == str(f)

def test_cli_stdin_input(mock_detector, mock_format_report):
    mock_instance = mock_detector.return_value
    mock_instance.scan_stream.return_value = []
    
    with patch.object(sys, 'argv', ['cli.py', '-']):
        with patch('sys.stdin', MagicMock()):
            main()
    
    mock_instance.scan_stream.assert_called()

def test_cli_options_passed(mock_detector, mock_format_report):
    mock_instance = mock_detector.return_value
    mock_instance.scan.return_value = []
    
    with patch.object(sys, 'argv', ['cli.py', '--text', 'secret', '--threshold', '2.5', '--full', '--nocolors']):
        main()
    
    mock_detector.assert_called_with(entropy_threshold=2.5)
    mock_format_report.assert_called_with([], show_full=True, show_short=False, no_colors=True)

def test_cli_short_option(mock_detector, mock_format_report):
    mock_instance = mock_detector.return_value
    mock_instance.scan.return_value = []
    
    with patch.object(sys, 'argv', ['cli.py', '--text', 'secret', '--short']):
        main()
    
    mock_format_report.assert_called_with([], show_full=False, show_short=True, no_colors=False)
