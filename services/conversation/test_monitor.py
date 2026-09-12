import unittest
import monitor_public

class MonitorTests(unittest.TestCase):
    def test_sustained_outage_and_recovery(self):
        state = {}
        for count in (1, 2):
            state, event = monitor_public.next_state(state, False)
            self.assertEqual(state["failures"], count)
            self.assertIsNone(event)
        state, event = monitor_public.next_state(state, False)
        self.assertEqual((state["status"], event), ("down", "down"))
        state, event = monitor_public.next_state(state, False)
        self.assertIsNone(event)
        state, event = monitor_public.next_state(state, True)
        self.assertEqual((state["status"], event), ("up", "recovered"))

if __name__ == '__main__':
    unittest.main()
