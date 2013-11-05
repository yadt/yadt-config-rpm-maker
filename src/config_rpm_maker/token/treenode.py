"""
Created on Aug 12, 2011

@author: Michael Gruber, Konrad Hosemann
"""

class NameNotAcceptedException(Exception):
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return "name '%s' is not accepted, must not be empty or null" % self.name


class TreeNode:
    def __init__(self, name, children = []):
        if name == None or len(name) == 0:
            raise NameNotAcceptedException(name)
        self.name = name
        self.children = set(children)
