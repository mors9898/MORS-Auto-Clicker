import unittest
from unittest.mock import patch
import mors_app as app

class LogicTests(unittest.TestCase):
    def test_alpha(self):
        self.assertEqual(app.parse_key("a"), 65)
    def test_digit(self):
        self.assertEqual(app.parse_key("9"), 57)
    def test_special_key(self):
        self.assertEqual(app.parse_key("space"), 32)
    def test_function_key(self):
        self.assertEqual(app.parse_key("F6"), 117)
    def test_combo(self):
        self.assertEqual(app.parse_sequence("CTRL+S"), [[17, 83]])
    def test_multiple_keys(self):
        self.assertEqual(app.parse_sequence("A,B,C"), [[65],[66],[67]])
    def test_reject_unknown(self):
        with self.assertRaises(ValueError):
            app.parse_sequence("NOT_A_KEY")
    def test_reject_empty_sequence(self):
        with self.assertRaises(ValueError):
            app.parse_sequence("A,,B")
    def test_valid_mouse(self):
        settings={"interval":"1000","delay":"0","cycles":"10","x":"-10","y":"50",
            "button":"Left","page":"mouse","keys":"SPACE"}
        self.assertEqual(app.validate(settings)[:5],(1000,0,10,-10,50))
    def test_valid_keyboard(self):
        settings={"interval":"250","delay":"0","cycles":"10","x":"0","y":"0",
            "button":"Left","page":"keyboard","keys":"CTRL+S,ENTER"}
        self.assertEqual(app.validate(settings)[-1],[[17,83],[13]])
    def test_reject_fast_interval(self):
        settings={"interval":"1","delay":"0","cycles":"10","x":"0","y":"0",
            "button":"Left","page":"mouse","keys":"SPACE"}
        with self.assertRaises(ValueError):
            app.validate(settings)
    def test_languages_and_themes(self):
        self.assertEqual(set(app.WORDS), {"English","العربية"})
        self.assertEqual(set(app.COLORS), {"Dark","Light"})
    def test_links(self):
        self.assertEqual(app.DISCORD, "https://discord.gg/ANHebepXT9")
        self.assertEqual(app.TIKTOK, "https://www.tiktok.com/@m_9gc")

if __name__=="__main__":
    unittest.main()
