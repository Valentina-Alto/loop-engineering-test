"""Acceptance tests for the book launch landing page (issue #4).

Stdlib-only (html.parser) so verification needs no external dependencies and
no network. Each test maps to an acceptance criterion in the issue/PR.

Run: python -m unittest tests.test_landing_page
"""

import os
import unittest
from html.parser import HTMLParser

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INDEX = os.path.join(ROOT, "index.html")


class _Collector(HTMLParser):
    """Collects tags, attributes, and text for assertion."""

    def __init__(self):
        super().__init__()
        self.tags = []  # list of (tag, dict(attrs))
        self.text_parts = []

    def handle_starttag(self, tag, attrs):
        self.tags.append((tag, dict(attrs)))

    def handle_startendtag(self, tag, attrs):
        self.tags.append((tag, dict(attrs)))

    def handle_data(self, data):
        self.text_parts.append(data)

    # Convenience accessors -------------------------------------------------
    def count(self, tag):
        return sum(1 for t, _ in self.tags if t == tag)

    def find(self, tag):
        return [a for t, a in self.tags if t == tag]

    @property
    def text(self):
        return " ".join(self.text_parts)


def _load():
    with open(INDEX, encoding="utf-8") as fh:
        html = fh.read()
    parser = _Collector()
    parser.feed(html)
    return html, parser


class LandingPageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        assert os.path.exists(INDEX), f"index.html not found at {INDEX}"
        cls.html, cls.dom = _load()

    # Criterion 1: happy path — required content present ---------------------
    def test_required_content(self):
        text = self.dom.text
        self.assertIn("Agentic Development in Practice", text, "title missing")
        self.assertRegex(
            self.html, r'class="subtitle"[^>]*>[^<]+<', "subtitle missing"
        )
        self.assertIn("Valentina Alto", text, "author missing")
        self.assertRegex(
            self.html, r'class="blurb"[^>]*>\s*\S', "blurb missing"
        )
        imgs = self.dom.find("img")
        self.assertTrue(imgs, "no <img> cover found")
        self.assertTrue(
            any(a.get("alt", "").strip() for a in imgs),
            "cover <img> has no non-empty alt text",
        )
        anchors = self.dom.find("a")
        ctas = [a for a in anchors if a.get("href", "").strip()]
        self.assertTrue(ctas, "no CTA anchor with href found")
        self.assertIn(
            "get the book",
            self.dom.text.lower(),
            "primary CTA text 'Get the book' missing",
        )

    # Criterion 2: responsive, no horizontal overflow ------------------------
    def test_responsive_markers(self):
        metas = self.dom.find("meta")
        self.assertTrue(
            any(
                m.get("name") == "viewport"
                and "width=device-width" in m.get("content", "")
                for m in metas
            ),
            "responsive viewport meta tag missing",
        )
        self.assertIn(
            "max-width", self.html, "no max-width container rule for responsiveness"
        )
        self.assertRegex(
            self.html,
            r"img\s*\{[^}]*max-width:\s*100%",
            "images not constrained to max-width:100% (risk of overflow)",
        )
        self.assertIn(
            "overflow-x: hidden",
            self.html,
            "no overflow-x guard on body",
        )

    # Criterion 3: accessibility --------------------------------------------
    def test_accessibility(self):
        self.assertEqual(
            self.dom.count("h1"), 1, "there must be exactly one <h1>"
        )
        for landmark in ("header", "main", "footer"):
            self.assertEqual(
                self.dom.count(landmark),
                1,
                f"expected exactly one <{landmark}> landmark",
            )
        for img in self.dom.find("img"):
            self.assertTrue(
                img.get("alt", "").strip(),
                "every <img> must have non-empty alt text",
            )
        self.assertRegex(self.html, r"<html[^>]*\blang=", "<html> missing lang")

    # Contrast is pinned by exact palette hex values (fixture-locked wall).
    def test_contrast_palette_pinned(self):
        # Dark ink on white ~16:1; CTA white on #4b3fa7 ~6.9:1 (both >= 4.5:1).
        for hex_value in ("#1a1a2e", "#4b3fa7", "#ffffff"):
            self.assertIn(
                hex_value,
                self.html.lower(),
                f"expected pinned palette colour {hex_value} for documented contrast",
            )


if __name__ == "__main__":
    unittest.main()
