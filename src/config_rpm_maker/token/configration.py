"""
Created on Aug 12, 2011

@author: Michael Gruber, Konrad Hosemann
"""
class IllegalArgumentException(Exception):
    def __init__ (self, argument_name):
        self.argument_name = argument_name
        
    def __str__ (self):
        return "argument '%s' is invalid, must not be null" % self.argument_name

def affected_nodes(root, changed_paths):
    if root == None:
        raise IllegalArgumentException("root")
    if changed_paths == None:
        raise IllegalArgumentException("changed_path")
      
    nodes = []

# initial idea how to traverse the tree        
#      
#    for path in changed_paths:
#        if root.name == path:
#            nodes.add(root)
#            
#    if len(root.children) > 0:
#        for child in root.children:
#            nodes.add(affected_nodes(child, changed_paths))
#       
    return nodes
