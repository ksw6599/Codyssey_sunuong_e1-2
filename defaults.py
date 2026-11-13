"""E1-1에서 직접 사용한 터미널·Docker·Git 개념을 복습한다."""

from quiz import Quiz


def create_default_quizzes():
    """호출할 때마다 독립된 Quiz 객체 여섯 개를 만든다."""
    return [
        Quiz("Ubuntu에서 현재 작업 경로를 출력하는 명령은?",
             ["ls", "pwd", "cd", "mkdir"], 2),
        Quiz("파일 권한 644에서 소유자가 가진 권한은?",
             ["읽기만", "읽기와 실행", "읽기와 쓰기", "읽기·쓰기·실행"], 3),
        Quiz("Dockerfile에서 호스트 파일을 이미지에 넣는 지시는?",
             ["COPY", "RUN", "EXPOSE", "LABEL"], 1),
        Quiz("-p 8781:80으로 실행한 웹 서버의 호스트 포트는?",
             ["컨테이너의 8781", "호스트의 80", "Docker의 고정 포트 80", "호스트의 8781"], 4),
        Quiz("바인드 마운트한 index.html을 호스트에서 수정하면?",
             ["이미지가 자동으로 다시 빌드된다", "컨테이너에서 변경된 파일을 읽는다",
              "Git이 자동으로 커밋한다", "Docker 볼륨이 삭제된다"], 2),
        Quiz("원격 변경을 기존 로컬 브랜치에 가져와 반영하는 명령은?",
             ["git init", "git clone", "git pull", "git status"], 3),
    ]
