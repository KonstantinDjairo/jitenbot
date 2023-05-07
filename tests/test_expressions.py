import unittest
import bot.entries.expressions as Expressions


class TestExpressions(unittest.TestCase):
    def test_kata_to_hira(self):
        hira = "Abc5゠ぁゖずほヷヸヹヺ・ーゝゞヿ"
        kata = "Abc5゠ァヶズホヷヸヹヺ・ーヽヾヿ"
        transformed = Expressions.kata_to_hira(kata)
        self.assertEqual(transformed, hira)

    def test_add_fullwidth(self):
        exps = ["Abc059!~{}あア日本語Ａｂｃ０５９！～｛｝"]
        Expressions.add_fullwidth(exps)
        self.assertEqual(len(exps), 2)
        self.assertIn("Abc059!~{}あア日本語Ａｂｃ０５９！～｛｝", exps)
        self.assertIn("Ａｂｃ０５９！～｛｝あア日本語Ａｂｃ０５９！～｛｝", exps)

    def test_add_iteration_mark(self):
        exps = ["禍禍しい", "凶々しい", "凶凶しい"]
        Expressions.add_iteration_mark(exps)
        self.assertEqual(len(exps), 4)
        self.assertIn("禍々しい", exps)
        self.assertIn("禍禍しい", exps)
        self.assertIn("凶々しい", exps)
        self.assertIn("凶凶しい", exps)

    def test_remove_iteration_mark(self):
        exps = ["禍々しい", "凶々しい", "凶凶しい"]
        Expressions.remove_iteration_mark(exps)
        self.assertEqual(len(exps), 4)
        self.assertIn("禍々しい", exps)
        self.assertIn("禍禍しい", exps)
        self.assertIn("凶々しい", exps)
        self.assertIn("凶凶しい", exps)

    def test_add_variant_kanji(self):
        exps = ["剝く", "掴む", "摑む"]
        Expressions.add_variant_kanji(exps)
        self.assertEqual(len(exps), 4)
        self.assertIn("剥く", exps)
        self.assertIn("剝く", exps)
        self.assertIn("掴む", exps)
        self.assertIn("摑む", exps)

    def test_add_variant_kanji2(self):
        exps = ["剝摑"]
        Expressions.add_variant_kanji(exps)
        self.assertEqual(len(exps), 4)
        self.assertIn("剝摑", exps)
        self.assertIn("剝掴", exps)
        self.assertIn("剥掴", exps)
        self.assertIn("剥摑", exps)

    def test_expand_abbreviation(self):
        text = "有（り）合（わ）せ"
        abbrs = Expressions.expand_abbreviation(text)
        self.assertEqual(len(abbrs), 4)
        self.assertIn("有り合わせ", abbrs)
        self.assertIn("有合わせ", abbrs)
        self.assertIn("有り合せ", abbrs)
        self.assertIn("有合せ", abbrs)

    def test_expand_abbreviation_list(self):
        texts = ["有（り）合わせ", "有り合（わ）せ", "有合せ"]
        abbrs = Expressions.expand_abbreviation_list(texts)
        self.assertEqual(len(abbrs), 4)
        self.assertIn("有り合わせ", abbrs)
        self.assertIn("有合わせ", abbrs)
        self.assertIn("有り合せ", abbrs)
        self.assertIn("有合せ", abbrs)

    def test_smk_expand_alternatives(self):
        text = "△金（時間・暇）に飽かして"
        exps = Expressions.expand_smk_alternatives(text)
        self.assertEqual(len(exps), 3)
        self.assertIn("金に飽かして", exps)
        self.assertIn("時間に飽かして", exps)
        self.assertIn("暇に飽かして", exps)

    def test_daijirin_expand_alternatives(self):
        text = "同じ穴の＝狢（＝狐・狸）"
        exps = Expressions.expand_daijirin_alternatives(text)
        self.assertEqual(len(exps), 3)
        self.assertIn("同じ穴の狢", exps)
        self.assertIn("同じ穴の狐", exps)
        self.assertIn("同じ穴の狸", exps)

    def test_daijirin_expand_alternatives2(self):
        text = "聞くは＝一時（＝一旦）の恥、聞かぬは＝末代（＝一生）の恥"
        exps = Expressions.expand_daijirin_alternatives(text)
        self.assertEqual(len(exps), 4)
        self.assertIn("聞くは一時の恥、聞かぬは末代の恥", exps)
        self.assertIn("聞くは一時の恥、聞かぬは一生の恥", exps)
        self.assertIn("聞くは一旦の恥、聞かぬは末代の恥", exps)
        self.assertIn("聞くは一旦の恥、聞かぬは一生の恥", exps)
