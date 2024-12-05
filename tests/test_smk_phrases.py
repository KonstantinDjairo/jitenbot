import unittest
from bot.entries.smk8.phrase_entry import parse_phrase


class TestSmk8PhraseParse(unittest.TestCase):
    def test1(self):
        text = "目と鼻の△先（間）"
        exps = parse_phrase(text)
        self.assertEqual(len(exps), 2)
        self.assertIn("目と鼻の先", exps)
        self.assertIn("目と鼻の間", exps)

    def test2(self):
        text = "△金（時間・暇）に飽かして"
        exps = parse_phrase(text)
        self.assertEqual(len(exps), 3)
        self.assertIn("金に飽かして", exps)
        self.assertIn("時間に飽かして", exps)
        self.assertIn("暇に飽かして", exps)
