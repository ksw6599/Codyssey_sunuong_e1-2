"""메뉴와 정답 입력에 같은 검증 규칙을 적용한다."""


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


def read_text(prompt):
    """공백뿐인 문제나 선택지가 등록되지 않도록 한다."""
    while True:
        text = input(prompt).strip()
        if text:
            return text
        print("빈 입력은 사용할 수 없습니다. 내용을 입력해 주세요.")
