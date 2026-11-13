"""실제 임시 파일과 콘솔 입력을 사용해 중요한 실패 경로를 검사한다."""

import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from defaults import create_default_quizzes
from game import QuizGame
from inputs import read_number, read_text
from quiz import Quiz


class QuizTests(unittest.TestCase):
    def test_round_trip_and_one_based_answer(self):
        quiz = Quiz(" 문제 ", [" 가 ", "나", "다", "라"], 2)
        restored = Quiz.from_dict(quiz.to_dict())
        self.assertEqual(restored.question, "문제")
        self.assertEqual(restored.choices[0], "가")
        self.assertTrue(restored.is_correct(2))
        self.assertFalse(restored.is_correct(1))

    def test_reject_invalid_quiz_records(self):
        for question, choices, answer in [
            (" ", ["a", "b", "c", "d"], 1),
            ("q", ["a"], 1),
            ("q", ["a", "b", "", "d"], 1),
            ("q", ["a", "b", "c", 4], 1),
            ("q", ["a", "b", "c", "d"], 0),
            ("q", ["a", "b", "c", "d"], True),
        ]:
            with self.subTest(question=question, answer=answer):
                with self.assertRaises(ValueError):
                    Quiz(question, choices, answer)

    def test_defaults_are_independent(self):
        first, second = create_default_quizzes(), create_default_quizzes()
        self.assertGreaterEqual(len(first), 5)
        first[0].choices[0] = "changed"
        self.assertNotEqual(first[0].choices, second[0].choices)


class InputTests(unittest.TestCase):
    def test_menu_retries_empty_text_and_out_of_range(self):
        output = io.StringIO()
        with patch("builtins.input", side_effect=["", "abc", "9", " 1 "]):
            with contextlib.redirect_stdout(output):
                self.assertEqual(read_number("선택: ", 1, 5), 1)
        self.assertIn("빈 입력", output.getvalue())
        self.assertIn("숫자로", output.getvalue())
        self.assertIn("1~5", output.getvalue())

    def test_answer_rejects_zero_and_accepts_spaces(self):
        with patch("builtins.input", side_effect=["0", " 4 "]):
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(read_number("정답: ", 1, 4), 4)

    def test_required_text_retries_whitespace(self):
        with patch("builtins.input", side_effect=["   ", " 새 문제 "]):
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(read_text("문제: "), "새 문제")


class GameTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.state = Path(self.temporary.name) / "state.json"
        self.output = io.StringIO()
        self.redirect = contextlib.redirect_stdout(self.output)
        self.redirect.__enter__()
        self.addCleanup(self.redirect.__exit__, None, None, None)

    def test_missing_file_uses_defaults(self):
        game = QuizGame(self.state)
        self.assertEqual(len(game.quizzes), 6)
        self.assertIsNone(game.best_score)
        self.assertTrue(game.save_state())
        self.assertEqual(len(json.loads(self.state.read_text("utf-8"))["quizzes"]), 6)

    def test_add_and_reload_preserves_korean(self):
        game = QuizGame(self.state)
        with patch("builtins.input", side_effect=["새 문제", "일", "이", "삼", "사", "2"]):
            game.add_quiz()
        restored = QuizGame(self.state)
        self.assertEqual(len(restored.quizzes), 7)
        self.assertEqual(restored.quizzes[-1].question, "새 문제")
        self.assertNotIn("\\uc0c8", self.state.read_text("utf-8"))

    def test_play_updates_best_and_lower_score_cannot_replace_it(self):
        game = QuizGame(self.state)
        with patch("builtins.input", side_effect=["2", "3", "1", "4", "2", "1"]):
            game.play_quiz()
        self.assertEqual(game.best_score, 83)
        with patch("builtins.input", side_effect=["1"] * 6):
            game.play_quiz()
        self.assertEqual(QuizGame(self.state).best_score, 83)

    def test_empty_library_and_zero_score(self):
        self.state.write_text('{"quizzes": [], "best_score": 0}', encoding="utf-8")
        game = QuizGame(self.state)
        game.play_quiz()
        game.list_quizzes()
        game.show_score()
        self.assertEqual(self.output.getvalue().count("등록된 퀴즈가 없습니다"), 2)
        self.assertIn("최고 점수: 0점", self.output.getvalue())

    def test_unplayed_score_is_distinct_from_zero(self):
        QuizGame(self.state).show_score()
        self.assertIn("아직 퀴즈를", self.output.getvalue())

    def test_corrupt_json_is_backed_up_before_recovery(self):
        self.state.write_text("{broken", encoding="utf-8")
        game = QuizGame(self.state)
        self.assertEqual(len(game.quizzes), 6)
        backups = list(self.state.parent.glob("state.json.broken-*.bak"))
        self.assertEqual(len(backups), 1)
        self.assertEqual(backups[0].read_text("utf-8"), "{broken")
        self.assertTrue(game.save_state())
        self.assertEqual(len(json.loads(self.state.read_text("utf-8"))["quizzes"]), 6)

    def test_invalid_utf8_is_recoverable(self):
        self.state.write_bytes(b"\xff\xfe\xff")
        game = QuizGame(self.state)
        self.assertEqual(len(game.quizzes), 6)
        self.assertTrue(list(self.state.parent.glob("*.bak")))

    def test_invalid_schema_does_not_partially_load(self):
        for bad in [[], {"quizzes": []}, {"quizzes": [], "best_score": True},
                    {"quizzes": [], "best_score": 101},
                    {"quizzes": [{"question": "q"}], "best_score": 0}]:
            with self.subTest(data=bad):
                self.state.write_text(json.dumps(bad), encoding="utf-8")
                game = QuizGame(self.state)
                self.assertEqual(len(game.quizzes), 6)
                self.assertIsNone(game.best_score)

    def test_actual_read_error_protects_existing_path(self):
        self.state.mkdir()
        game = QuizGame(self.state)
        self.assertFalse(game.allow_save)
        self.assertFalse(game.save_state())
        self.assertTrue(self.state.is_dir())

    def test_actual_write_error_is_reported(self):
        game = QuizGame(self.state.parent / "missing" / "state.json")
        self.assertFalse(game.save_state())
        self.assertIn("저장하지 못했습니다", self.output.getvalue())

    def test_failed_atomic_replace_keeps_old_file_and_cleans_temporary(self):
        game = QuizGame(self.state)
        game.save_state()
        original = self.state.read_bytes()
        game.best_score = 99
        with patch("pathlib.Path.replace", side_effect=PermissionError("mocked replace denial")):
            self.assertFalse(game.save_state())
        self.assertEqual(self.state.read_bytes(), original)
        self.assertEqual(list(self.state.parent.glob("*.tmp")), [])

    def test_failed_corrupt_backup_disables_overwrite(self):
        self.state.write_text("broken", encoding="utf-8")
        with patch("game.shutil.copy2", side_effect=PermissionError("mocked backup denial")):
            game = QuizGame(self.state)
        self.assertFalse(game.save_state())
        self.assertEqual(self.state.read_text("utf-8"), "broken")

    def test_interrupt_and_eof_exit_safely(self):
        for exception in (KeyboardInterrupt(), EOFError()):
            with self.subTest(exception=type(exception).__name__):
                game = QuizGame(self.state)
                with patch("builtins.input", side_effect=exception):
                    game.run()
                self.assertTrue(self.state.is_file())
                self.assertIn("종료합니다", self.output.getvalue())


if __name__ == "__main__":
    unittest.main()
