import unittest
from bot.entries.sankoku8.parse import parse_hyouki_pattern


class TestSankoku8PhraseParse(unittest.TestCase):
    def test1(self):
        pattern = '耳にたこ（ができる）'
        exps = parse_hyouki_pattern(pattern)
        self.assertEqual(len(exps), 2)
        self.assertIn("耳にたこ", exps)
        self.assertIn("耳にたこができる", exps)

    def test2(self):
        pattern = '一斑を〈見て／もって〉全豹を〈卜す／推す〉'
        exps = parse_hyouki_pattern(pattern)
        self.assertEqual(len(exps), 4)
        self.assertIn("一斑を見て全豹を卜す", exps)
        self.assertIn("一斑を見て全豹を推す", exps)
        self.assertIn("一斑をもって全豹を卜す", exps)
        self.assertIn("一斑をもって全豹を推す", exps)

    def test3(self):
        pattern = '｛かじ・舵｝を切る'
        exps = parse_hyouki_pattern(pattern)
        self.assertEqual(len(exps), 2)
        self.assertIn("かじを切る", exps)
        self.assertIn("舵を切る", exps)

    def test4(self):
        pattern = '重箱の隅を（⦅ようじ＼楊枝⦆で）〈つつく／ほじくる〉'
        exps = parse_hyouki_pattern(pattern)
        self.assertEqual(len(exps), 6)
        self.assertIn("重箱の隅をつつく", exps)
        self.assertIn("重箱の隅をようじでつつく", exps)
        self.assertIn("重箱の隅を楊枝でつつく", exps)
        self.assertIn("重箱の隅をほじくる", exps)
        self.assertIn("重箱の隅をようじでほじくる", exps)
        self.assertIn("重箱の隅を楊枝でほじくる", exps)

    def test5(self):
        pattern = '群盲象を〈｛な・撫｝でる／評する〉'
        exps = parse_hyouki_pattern(pattern)
        self.assertEqual(len(exps), 3)
        self.assertIn("群盲象をなでる", exps)
        self.assertIn("群盲象を撫でる", exps)
        self.assertIn("群盲象を評する", exps)
