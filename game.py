"""메뉴와 게임의 진행을 담당한다."""


def read_number(prompt, minimum, maximum):
    """공백, 빈 입력, 문자, 범위 밖 숫자를 처리하고 정수를 반환한다."""
    while True:
        text = input(prompt).strip()
        if not text:
            print("빈 입력입니다. 숫자를 입력해 주세요.")
            continue
        try:
            number = int(text)
        except ValueError:
            print("숫자로 입력해 주세요.")
            continue
        if minimum <= number <= maximum:
            return number
        print(f"{minimum}~{maximum} 사이의 숫자를 입력해 주세요.")


class QuizGame:
    """사용자가 고른 메뉴에 따라 기능을 실행한다."""

    def show_menu(self):
        print("\n========================================")
        print("      개발 작업실 복습 퀴즈 · E1-2")
        print("========================================")
        print("1. 퀴즈 풀기")
        print("2. 퀴즈 추가")
        print("3. 퀴즈 목록")
        print("4. 점수 확인")
        print("5. 종료")

    def run(self):
        try:
            while True:
                self.show_menu()
                choice = read_number("선택 (1~5): ", 1, 5)
                if choice == 5:
                    break
                print("이 기능은 다음 개발 단계에서 연결합니다.")
        except (EOFError, KeyboardInterrupt):
            print("\n입력이 중단되어 안전하게 종료합니다.")
        print("퀴즈 게임을 종료합니다.")
