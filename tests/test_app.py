import pytest
import subprocess
import os
import shutil
from pathlib import Path

PRJ_ROOT = Path(__file__).parent.parent

# Define test parameters for different scenarios
test_cases = [
    ("init", None, None, "music", False, False, "init-defaults"),
    ("burn", "tests/test.db", "tests/collection", "music", 70000000, True, "burn-all-params"),
    ("init", "tests/test.db", None, "music", False, True, "init-debug"),
    ("burn", None, "tests/collection", "music", 70000000, False, "burn-partial"),
    ("init", None, None, "music", False, False, "init-env-vars"),
    ("burn", None, None, "music", None, True, "burn-env-vars"),
]

@pytest.fixture(scope="module", autouse=True)
def setup_music_directory():
    # Arrange: Create a temporary music directory
    music_dir = Path("tests/temp_music")
    music_dir.mkdir(exist_ok=True)

    # Create a .gitignore file with '*' to ignore all files
    with open(music_dir / ".gitignore", "w") as gitignore_file:
        gitignore_file.write("*\n")

    for i in range(3000):
        (music_dir / f"file_{i}.mp3").touch()

    yield music_dir  # Provide the music directory to the tests
    # Act: Cleanup the temporary music directory after tests
    shutil.rmtree(music_dir)
  
@pytest.mark.parametrize("cmd, db_file, col_path, music_dir, cdsize, debug, test_id", test_cases, ids=[tc[-1] for tc in test_cases])
def test_music_cd_burner(cmd, db_file, col_path, music_dir, cdsize, debug, test_id, monkeypatch, setup_music_directory):
    # Arrange
    if db_file:
        monkeypatch.setenv("DBFILE", db_file)
    if col_path:
        monkeypatch.setenv("COL_PATH", col_path)
    if music_dir:
        monkeypatch.setenv("MUSIC_DIR", str(setup_music_directory))
    if cdsize:
        monkeypatch.setenv("CDSIZE", str(cdsize))
    
    args = ["python", str(Path.joinpath(PRJ_ROOT, "sdburn.py")), cmd]
    if db_file:
        args.extend(["-d", db_file])
    if col_path:
        args.extend(["-c", col_path])
    if music_dir:
        args.extend(["-m", str(setup_music_directory)])
    if cdsize:
        args.extend(["-s", str(cdsize)])
    if debug:
        args.append("-v")

    # Act
    print('[[[[[',args,']]]]]')
    result = subprocess.run(args, capture_output=True, text=True)

    # Assert
    assert result.returncode == 0, f"Test {test_id} failed with stderr: {result.stderr}"
    if debug:
        assert "Время исполнения" in result.stdout or "Время исполнения" in result.stderr
    else:
        assert "Запуск MusicCDBurner в режиме" in result.stdout or "Запуск MusicCDBurner в режиме" in result.stderr
