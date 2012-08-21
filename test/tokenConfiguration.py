"""
Created on Aug 12, 2011

@author: Michael Gruber, Konrad Hosemann
"""
import unittest
from config_rpm_maker.token.configration import affected_nodes, IllegalArgumentException
from config_rpm_maker.token.treenode import TreeNode

class ConfigurationTest(unittest.TestCase):

    def test_should_not_return_an_afftected_node_when_changed_paths_are_empty (self):
        self.assertTrue(affected_nodes(TreeNode("root"), []) == [])
        
    def test_should_raise_exception_when_changed_paths_are_not_provided (self):
        self.assertRaises(IllegalArgumentException, affected_nodes, TreeNode("root"), None) 

    def test_should_raise_exception_when_changed_root_is_not_provided (self):
        self.assertRaises(IllegalArgumentException, affected_nodes, None, [])