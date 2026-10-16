import unittest
import lab
class ContainmentTests(unittest.TestCase):
    def test_required_application_calls_still_work(self):
        self.assertTrue(lab.evaluate()['assertions']['intended_operations_preserved'])
    def test_unrelated_data_is_denied_after_hardening(self):
        self.assertTrue(lab.evaluate()['assertions']['unrelated_operations_denied'])
    def test_explicit_deny_overrides_allow(self):
        policy={'Statement':[{'Effect':'Allow','Action':'s3:*','Resource':'*'},{'Effect':'Deny','Action':'s3:GetObject','Resource':'*'}]}
        self.assertEqual(lab.decision(policy,'s3:GetObject','arn:test'),'DENY')
    def test_unknown_action_is_implicitly_denied(self):
        self.assertEqual(lab.decision({'Statement':[]},'s3:DeleteObject','arn:test'),'DENY')
    def test_unsupported_policy_features_are_rejected(self):
        with self.assertRaises(ValueError):lab.decision({'Statement':[{'Effect':'Allow','Action':'*','Resource':'*','Condition':{}}]},'s3:GetObject','arn:test')
