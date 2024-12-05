import unittest
from bot.entries.daijirin2.phrase_entry import parse_phrase


class TestDaijirin2PhraseParse(unittest.TestCase):
    def test1(self):
        text = "同じ穴の＝狢（＝狐・狸）"
        exps = parse_phrase(text)
        self.assertEqual(len(exps), 3)
        self.assertIn("同じ穴の狢", exps)
        self.assertIn("同じ穴の狐", exps)
        self.assertIn("同じ穴の狸", exps)

    def test2(self):
        text = "聞くは＝一時（＝一旦）の恥、聞かぬは＝末代（＝一生）の恥"
        exps = parse_phrase(text)
        self.assertEqual(len(exps), 4)
        self.assertIn("聞くは一時の恥、聞かぬは末代の恥", exps)
        self.assertIn("聞くは一時の恥、聞かぬは一生の恥", exps)
        self.assertIn("聞くは一旦の恥、聞かぬは末代の恥", exps)
        self.assertIn("聞くは一旦の恥、聞かぬは一生の恥", exps)
