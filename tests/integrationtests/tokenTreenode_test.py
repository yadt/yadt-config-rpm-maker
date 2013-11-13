#   yadt-config-rpm-maker
#   Copyright (C) 2011-2013 Immobilien Scout GmbH
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.

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
