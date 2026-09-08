#!/usr/bin/env python3
"""Local source-fixture regression; no network, CAD kernel or output writes."""
import json
from pathlib import Path
import re
import unittest

from reconcile import PCB_PATH, ROOT, robot_hat_mounting


class OfficialHatMounting(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = (Path(ROOT) / PCB_PATH).read_bytes()
        cls.audit = json.loads((Path(ROOT) / 'research/official-hat-audit-2026-09-08.json').read_text())

    def test_holes_are_inside_connector_without_mountinghole_footprints(self):
        self.assertFalse(re.search(rb'\(footprint "[^"]*MountingHole', self.raw))
        result = robot_hat_mounting(self.raw, self.audit)
        self.assertEqual(result['count'], 4)
        self.assertEqual({h['footprint_reference'] for h in result['holes']}, {'J4'})
        self.assertEqual({h['diameter_mm'] for h in result['holes']}, {2.7})
        self.assertEqual(result['pattern_footprint_local_xy_mm'], [23.0, 58.0])

    def test_removed_drill_is_rejected(self):
        broken = self.raw.replace(b'(drill 2.7)', b'(drill 2.6)', 1)
        self.assertNotEqual(broken, self.raw)
        with self.assertRaisesRegex(ValueError, 'four 2.7 mm holes'):
            robot_hat_mounting(broken, self.audit)

    def test_unpinned_source_is_rejected(self):
        with self.assertRaisesRegex(ValueError, 'sha256'):
            robot_hat_mounting(self.raw + b'\n', self.audit)


if __name__ == '__main__':
    unittest.main()
