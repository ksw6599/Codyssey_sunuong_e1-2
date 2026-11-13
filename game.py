"""메뉴와 게임의 진행을 담당한다."""

import json
import shutil
import tempfile
import time
from pathlib import Path

from defaults import create_default_quizzes
from inputs import read_number, read_text
from quiz import Quiz

STATE_FILE = Path(__file__).resolve().parent / "state.json"


class QuizGame:
    """사용자가 고른 메뉴에 따라 기능을 실행한다."""

    def __init__(self, state_path=None):
        self.state_path = Path(state_path) if state_path is not None else STATE_FILE
        self.quizzes = create_default_quizzes()
        self.best_score = None
        self.allow_save = True
        self.load_state()

    def load_state(self):
        try:
            with self.state_path.open("r", encoding="utf-8") as file:
                data = json.load(file)
            if (not isinstance(data, dict)
                    or not isinstance(data.get("quizzes"), list)
                    or "best_score" not in data):
                raise ValueError("quizzes는 목록이어야 합니다.")
            quizzes = [Quiz.from_dict(item) for item in data["quizzes"]]
            best_score = data.get("best_score")
            if best_score is not None and (
                    type(best_score) is not int or not 0 <= best_score <= 100):
                raise ValueError("best_score는 null 또는 0~100 정수여야 합니다.")
            self.quizzes = quizzes
            self.best_score = best_score
            print(f"저장된 데이터를 불러왔습니다. (퀴즈 {len(quizzes)}개)")
        except FileNotFoundError:
            print("저장 파일이 없어 기본 퀴즈 6개로 시작합니다.")
        except (UnicodeError, ValueError, TypeError) as error:
            print(f"저장 파일이 손상되어 기본 퀴즈로 복구합니다: {error}")
            backup = self.state_path.with_name(
                f"{self.state_path.name}.broken-{time.time_ns()}.bak")
            try:
                shutil.copy2(self.state_path, backup)
                print(f"원본은 {backup.name}에 백업했습니다.")
            except OSError:
                self.allow_save = False
                print("원본을 백업하지 못해 이번 실행의 파일 저장을 중지합니다.")
        except OSError as error:
            self.allow_save = False
            print(f"저장 파일 읽기 오류입니다. 기본 퀴즈로 시작합니다: {error}")
            print("기존 파일을 보호하기 위해 이번 실행은 파일에 저장하지 않습니다.")

    def save_state(self):
        if not self.allow_save:
            print("파일 저장이 중지된 상태입니다. 이번 변경은 메모리에만 있습니다.")
            return False
        data = {
            "quizzes": [quiz.to_dict() for quiz in self.quizzes],
            "best_score": self.best_score,
        }
        temporary_path = None
        try:
            with tempfile.NamedTemporaryFile(
                    mode="w", encoding="utf-8", dir=self.state_path.parent,
                    prefix=self.state_path.name + ".", suffix=".tmp",
                    delete=False) as file:
                temporary_path = Path(file.name)
                json.dump(data, file, ensure_ascii=False, indent=2)
                file.write("\n")
            temporary_path.replace(self.state_path)
            return True
        except (OSError, UnicodeError) as error:
            print(f"저장하지 못했습니다: {error}")
            return False
        finally:
            if temporary_path is not None:
                try:
                    temporary_path.unlink(missing_ok=True)
                except OSError:
                    pass

    def show_menu(self):
        print("\n========================================")
        print("      개발 작업실 복습 퀴즈 · E1-2")
        print("========================================")
        print("1. 퀴즈 풀기")
        print("2. 퀴즈 추가")
        print("3. 퀴즈 목록")
        print("4. 점수 확인")
        print("5. 종료")

    def play_quiz(self):
        if not self.quizzes:
            print("등록된 퀴즈가 없습니다. 먼저 퀴즈를 추가해 주세요.")
            return
        correct_count = 0
        print(f"\n퀴즈를 시작합니다. (총 {len(self.quizzes)}문제)")
        for number, quiz in enumerate(self.quizzes, start=1):
            quiz.display(number)
            answer = read_number("정답 입력 (1~4): ", 1, 4)
            if quiz.is_correct(answer):
                correct_count += 1
                print("[정답] 맞았습니다!")
            else:
                print(f"[오답] 정답은 {quiz.answer}번입니다.")
        score = correct_count * 100 // len(self.quizzes)
        print(f"결과: {len(self.quizzes)}문제 중 {correct_count}문제 정답! ({score}점)")
        if self.best_score is None or score > self.best_score:
            self.best_score = score
            print("새로운 최고 점수입니다!")
        if not self.save_state():
            print("이번 점수는 메모리에 있지만 파일에 저장되지 않았습니다.")

    def show_score(self):
        if self.best_score is None:
            print("아직 퀴즈를 끝까지 푼 기록이 없습니다.")
        else:
            print(f"최고 점수: {self.best_score}점 (100점 만점)")

    def add_quiz(self):
        print("\n새 퀴즈를 추가합니다.")
        question = read_text("문제: ")
        choices = [read_text(f"선택지 {number}: ") for number in range(1, 5)]
        answer = read_number("정답 번호 (1~4): ", 1, 4)
        self.quizzes.append(Quiz(question, choices, answer))
        if self.save_state():
            print(f"퀴즈가 추가되어 파일에 저장되었습니다. (총 {len(self.quizzes)}개)")
        else:
            print("퀴즈는 이번 실행에 추가됐지만 파일 저장에 실패했습니다.")

    def list_quizzes(self):
        if not self.quizzes:
            print("등록된 퀴즈가 없습니다. 먼저 퀴즈를 추가해 주세요.")
            return
        print(f"\n등록된 퀴즈 목록 (총 {len(self.quizzes)}개)")
        for number, quiz in enumerate(self.quizzes, start=1):
            print(f"[{number}] {quiz.question}")

    def run(self):
        try:
            while True:
                self.show_menu()
                choice = read_number("선택 (1~5): ", 1, 5)
                if choice == 1:
                    self.play_quiz()
                elif choice == 2:
                    self.add_quiz()
                elif choice == 3:
                    self.list_quizzes()
                elif choice == 4:
                    self.show_score()
                elif choice == 5:
                    break
        except EOFError:
            print("\n입력 스트림이 끝났습니다. 가능한 데이터를 저장하고 종료합니다.")
        except KeyboardInterrupt:
            print("\nCtrl+C를 받았습니다. 가능한 데이터를 저장하고 종료합니다.")
        finally:
            if self.save_state():
                print("퀴즈와 최고 점수를 state.json에 저장했습니다.")
        print("퀴즈 게임을 종료합니다.")
