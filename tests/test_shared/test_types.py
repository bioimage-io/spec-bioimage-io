from unittest import TestCase


class TestRelativePath(TestCase):
    def test_eq(self):
        from bioimageio.spec.shared.types import RelativePath

        p = RelativePath(__file__)
        p2 = RelativePath(__file__)
        self.assertEqual(p, p2)
