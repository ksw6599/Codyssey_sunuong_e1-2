"""프로젝트를 임시 복제하고 실제 main.py를 실행해 증거를 남긴다."""

import json
import os
from pathlib import Path
import select
import shutil
import signal
import subprocess
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parents[1]
LOG = ROOT / "docs" / "evidence" / "verification.log"
lines = ["E1-2 actual execution verification", f"Python: {sys.version}", ""]


def run_case(project, outside, name, inputs, expected):
    command = [sys.executable, str(project / "main.py")]
    result = subprocess.run(command, input=inputs, cwd=outside,
                            capture_output=True, text=True, timeout=10,
                            encoding="utf-8")
    lines.extend([f"=== {name} ===", "Command: " + " ".join(command),
                  "Input: " + repr(inputs), result.stdout, result.stderr,
                  f"Exit code: {result.returncode}", ""])
    assert result.returncode == 0, name + " exited unsuccessfully"
    assert "Traceback" not in result.stderr, name + " traceback"
    for message in expected:
        assert message in result.stdout, name + ": missing " + message
    print("PASS:", name)


def verify_real_interrupt(project, outside):
    command = [sys.executable, "-u", str(project / "main.py")]
    process = subprocess.Popen(command, cwd=outside, stdin=subprocess.PIPE,
                               stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                               start_new_session=True)
    output = b""
    try:
        deadline = time.monotonic() + 10
        while "선택 (1~5):".encode() not in output:
            remaining = deadline - time.monotonic()
            assert remaining > 0, "menu prompt timeout"
            ready, _, _ = select.select([process.stdout], [], [], remaining)
            assert ready, "no console output"
            chunk = os.read(process.stdout.fileno(), 4096)
            assert chunk, "console closed before prompt"
            output += chunk
        os.killpg(process.pid, signal.SIGINT)
        rest, _ = process.communicate(timeout=10)
        text = (output + rest).decode("utf-8")
        lines.extend(["=== real SIGINT at menu ===", "Command: " + " ".join(command),
                      "Signal: SIGINT sent to the running process group", text,
                      f"Exit code: {process.returncode}", ""])
        assert process.returncode == 0
        assert "Ctrl+C를 받았습니다" in text
        assert "Traceback" not in text
        print("PASS: real SIGINT at menu")
    finally:
        if process.poll() is None:
            process.kill()
            process.communicate()


def verify():
    with tempfile.TemporaryDirectory(prefix="codyssey-e12-") as temporary:
        base = Path(temporary)
        project, outside = base / "project", base / "outside"
        project.mkdir()
        outside.mkdir()
        for name in ["main.py", "game.py", "quiz.py", "defaults.py", "inputs.py"]:
            shutil.copy2(ROOT / name, project / name)
        state = project / "state.json"
        run_case(project, outside, "first run and unplayed score", "4\n5\n",
                 ["기본 퀴즈 6개", "아직 퀴즈를", "저장했습니다"])
        assert not (outside / "state.json").exists()
        run_case(project, outside, "invalid menu input and whitespace",
                 "\nabc\n9\n 3 \n5\n",
                 ["빈 입력", "숫자로", "1~5", "총 6개"])
        addition = ["2", "", "Git에서 현재 작업 상태를 확인하는 명령은?", "",
                    "git status", "git init", "git push", "git clone",
                    "", "abc", "0", " 1 ", "3", "5"]
        run_case(project, outside, "register quiz with invalid inputs",
                 "\n".join(addition) + "\n",
                 ["빈 입력", "숫자로", "1~4", "총 7개", "Git"])
        data = json.loads(state.read_text("utf-8"))
        assert len(data["quizzes"]) == 7
        assert data["quizzes"][-1]["answer"] == 1
        run_case(project, outside, "play seven questions and record high score",
                 "1\n\nabc\n0\n 2 \n3\n1\n4\n2\n3\n1\n4\n5\n",
                 ["[정답]", "7문제 중 7문제 정답! (100점)", "최고 점수: 100점"])
        run_case(project, outside, "lower score keeps previous high score",
                 "1\n1\n1\n1\n1\n1\n1\n1\n4\n5\n",
                 ["[오답]", "7문제 중 2문제 정답! (28점)", "최고 점수: 100점"])
        run_case(project, outside, "restart restores quiz and score", "3\n4\n5\n",
                 ["퀴즈 7개", "현재 작업 상태", "최고 점수: 100점"])
        data = json.loads(state.read_text("utf-8"))
        assert data["best_score"] == 100
        assert len(data["quizzes"]) == 7
        state.write_text('{"quizzes": [], "best_score": null}', encoding="utf-8")
        run_case(project, outside, "empty library", "1\n3\n4\n5\n",
                 ["등록된 퀴즈가 없습니다", "아직 퀴즈를"])
        state.write_text("{broken", encoding="utf-8")
        run_case(project, outside, "corrupt JSON recovery", "3\n5\n",
                 ["손상되어", "백업했습니다", "총 6개"])
        assert any(p.read_text("utf-8") == "{broken" for p in project.glob("*.bak"))
        run_case(project, outside, "EOF at menu", "",
                 ["입력 스트림이 끝났습니다", "종료합니다"])
        run_case(project, outside, "EOF during partial registration", "2\n미완성\n선택지 하나\n",
                 ["입력 스트림이 끝났습니다", "저장했습니다"])
        assert len(json.loads(state.read_text("utf-8"))["quizzes"]) == 6
        verify_real_interrupt(project, outside)
        state.unlink()
        state.mkdir()
        run_case(project, outside, "actual filesystem read error", "3\n5\n",
                 ["읽기 오류", "총 6개", "파일 저장이 중지"])
        lines.append("Write denial and replacement denial are additionally covered by unit tests.")
    unit = subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"],
                          cwd=ROOT, capture_output=True, text=True, encoding="utf-8")
    lines.extend(["=== unit tests ===", unit.stdout, unit.stderr,
                  f"Exit code: {unit.returncode}"])
    assert unit.returncode == 0
    print("PASS: 19 unit tests")
    print("ALL CHECKS PASSED (12 entrypoint scenarios + 19 unit tests)")


if __name__ == "__main__":
    try:
        verify()
        lines.append("ALL CHECKS PASSED (12 entrypoint scenarios + 19 unit tests)")
    finally:
        LOG.parent.mkdir(parents=True, exist_ok=True)
        LOG.write_text("\n".join(lines) + "\n", encoding="utf-8")
