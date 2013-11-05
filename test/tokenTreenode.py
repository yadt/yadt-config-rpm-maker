'''
Created on Aug 12, 2011

@author: Michael Gruber, Konrad Hosemann
'''
import unittest
from config_rpm_maker.token.treenode import TreeNode, NameNotAcceptedException


class TreeNodeTest(unittest.TestCase):

    def test_should_have_a_name(self):
        self.assertTrue(TreeNode("spam").name == "spam")

    def test_should_initially_have_no_child(self):
        self.assertTrue(len(TreeNode("egg").children) == 0)

    def test_should_have_a_child_when_child_is_added(self):
        child = TreeNode("child")
        parent = TreeNode("parent", [child])

        self.assertTrue(child in parent.children)

    def test_should_not_accept_an_empty_name(self):
        self.assertRaises(NameNotAcceptedException, TreeNode, "")

    def test_should_not_accept_no_name(self):
        self.assertRaises(NameNotAcceptedException, TreeNode, None)
