import unittest

from mvp.src.events import event_availability, events_for_instrument


class EventTests(unittest.TestCase):
    # Synthetic boundary fixture only: never market evidence.
    def setUp(self):
        self.event = {"event_published_at": "2026-10-21T12:20:00+05:00", "timezone_verified": True,
                      "publication_precision": "MINUTE", "instrument_id": "KZ1", "issuer_id": "ISS",
                      "mapping_scope": "ISSUE", "evidence_status": "VERIFIED"}

    def test_confirmed_publication_boundaries_and_utc_equivalence(self):
        self.assertFalse(event_availability(self.event, "2026-10-21T12:19:59+05:00")["available"])
        self.assertTrue(event_availability(self.event, "2026-10-21T07:20:00+00:00")["available"])
        self.assertTrue(event_availability(self.event, "2026-10-21T12:20:01+05:00")["available"])

    def test_naive_instant_is_rejected(self):
        with self.assertRaises(ValueError): event_availability(self.event, "2026-10-21T12:20:00")

    def test_unverified_timezone_waits_until_next_local_day(self):
        event = dict(self.event, timezone_verified=False)
        self.assertFalse(event_availability(event, "2026-10-21T23:59:59+05:00")["available"])
        self.assertTrue(event_availability(event, "2026-10-22")["available"])

    def test_date_precision_waits_until_next_local_day_even_if_timezone_verified(self):
        event = dict(self.event, publication_precision="DATE")
        self.assertFalse(event_availability(event, "2026-10-21")["available"])
        self.assertTrue(event_availability(event, "2026-10-22T00:00:00+05:00")["available"])

    def test_issue_scope_does_not_leak_to_sibling_bond(self):
        issuer_event = dict(self.event, mapping_scope="ISSUER", instrument_id=None)
        self.assertEqual(len(events_for_instrument([self.event, issuer_event], "KZ2", "ISS", "2026-10-22")), 1)
        self.assertEqual(events_for_instrument([self.event], "KZ2", "ISS", "2026-10-22"), [])
