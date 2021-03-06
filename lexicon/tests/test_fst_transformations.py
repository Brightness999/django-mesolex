import re
import unittest
from django.test import TestCase
from lexicon.transformations.transducers.fst_handler import FSTHandler, get_nahuat_att_file

class FSTTransformTestCase(TestCase):
    vln_fst = FSTHandler(get_nahuat_att_file(flex=False,
                                             isoglosses=False,
                                             vln=True))

    iso_fst = FSTHandler(get_nahuat_att_file(flex=False,
                                             isoglosses=True,
                                             vln=False))

    all_fst = FSTHandler(get_nahuat_att_file(flex=True,
                                             isoglosses=True,
                                             vln=True))

    def test_vln(self):
        """
        Test that vowel-length (or lack thereof) is normalized.
        """
        inword = "takat"
        outword = 'ta:kat'
        self.assertTrue(self.vln_fst.match(inword, outword))

    @unittest.expectedFailure
    def test_isoglosses(self):
        """
        Test alternations based on common isoglosses (#e vs. #ye, t vs. tl,
        etc.)
        """
        inword = 'yehecatl'
        outword = 'ehecat'
        self.assertTrue(self.iso_fst.match(inword, outword))

    def test_composed_fst(self):
        """
        Test the composition of all individual FSTs.
        """
        inwords = ["tlacatl", "huecapantic", "panowa"]
        outwords = ["ta:kat", "wehkapantik", "panoa"]
        for in_word, out_word in zip(inwords, outwords):
            with self.subTest(in_word=in_word, out_word=out_word):
                self.assertTrue(self.all_fst.match(in_word, out_word))

    def test_regex_matches(self):
        """
        Test that the generated regex does in fact match all forms.
        """
        inword = "tzincalaqui"
        forms = self.all_fst.generate_forms(inword)
        pattern = re.compile(self.all_fst.get_pattern(inword))
        for form in forms:
            with self.subTest(form=form):
                self.assertTrue(re.match(pattern, form))
