"""선택지 네 개를 가진 퀴즈 하나를 표현한다."""


class Quiz:
    """문제, 선택지, 1부터 시작하는 정답 번호를 함께 보관한다."""

    def __init__(self, question, choices, answer):
        if not isinstance(question, str) or not question.strip():
            raise ValueError("문제는 비어 있지 않은 문자열이어야 합니다.")
        if not isinstance(choices, list) or len(choices) != 4:
            raise ValueError("선택지는 정확히 네 개여야 합니다.")
        if any(not isinstance(item, str) or not item.strip() for item in choices):
            raise ValueError("각 선택지는 비어 있지 않은 문자열이어야 합니다.")
        if type(answer) is not int or not 1 <= answer <= 4:
            raise ValueError("정답은 1~4 사이 정수여야 합니다.")
        self.question = question.strip()
        self.choices = [item.strip() for item in choices]
        self.answer = answer

    def display(self, number):
        print(f"\n[문제 {number}] {self.question}")
        for index, choice in enumerate(self.choices, start=1):
            print(f"  {index}. {choice}")

    def is_correct(self, choice):
        return choice == self.answer

    def to_dict(self):
        return {
            "question": self.question,
            "choices": self.choices,
            "answer": self.answer,
        }

    @classmethod
    def from_dict(cls, data):
        if not isinstance(data, dict):
            raise ValueError("퀴즈 한 개는 JSON 객체여야 합니다.")
        return cls(data.get("question"), data.get("choices"), data.get("answer"))
