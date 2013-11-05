from config_rpm_maker.exceptions import BaseConfigRpmMakerException

class ContainsCyclesException(BaseConfigRpmMakerException):
  error_info = "Variable cycle detected!"

class TokenCycleChecking(object):
  def __init__(self, edges):
    self.edges = edges
    

  def assert_no_cycles_present(self):
    cycles = []
    components = tarjan_scc(self.edges)
    for component in components:
      if len(component) > 1:
        cycles.append(component)
        #every nontrivial strongly connected component
        #contains at least one directed cycle, so len()>1 is a showstopper
    
    if len(cycles) > 0:
      error_message = "Found cycle(s) in variable declarations :\n"
      for cycle in cycles:
        error_message+="These variables form a cycle : "+str(cycle)+"\n"
      raise ContainsCyclesException(error_message)


#Tarjan's partitioning algorithm for finding strongly connected components in a graph.
def tarjan_scc(graph):
    index_counter = [0]
    stack = []
    lowlinks = {}
    index = {}
    result = []
    
    def strongconnect(node):
        index[node] = index_counter[0]
        lowlinks[node] = index_counter[0]
        index_counter[0] += 1
        stack.append(node)
    
        try:
            successors = graph[node]
        except:
            successors = []
        for successor in successors:
            if successor not in lowlinks:
                strongconnect(successor)
                lowlinks[node] = min(lowlinks[node],lowlinks[successor])
            elif successor in stack:
                lowlinks[node] = min(lowlinks[node],index[successor])
        
        if lowlinks[node] == index[node]:
            connected_component = []
            
            while True:
                successor = stack.pop()
                connected_component.append(successor)
                if successor == node:
                    break
            component = tuple(connected_component)
            result.append(component)
    
    for node in graph:
        if node not in lowlinks:
            strongconnect(node)
    
    return result
