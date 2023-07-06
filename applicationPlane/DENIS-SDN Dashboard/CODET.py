"""
CODET - Connectivity Detector Algorithm
Is a network administration tool that operates at the SDN Application-layer.
Its primary responsibility is to ensure the minimum connectivity
requirements are met within each slice by verifying that every
node has at least one viable path connecting it to the border
router.

Author: Tryfon Theodorou
Website: www.theodorou.edu.gr
GitHub: tryfonthe

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import queue

def run_CODET(G, tN):  # G Graph, tN Target Node
    dN = [] # disconnected_nodes_list

    for node in G:
        if node != tN:
            visited = []
            pathFound = BFS(node, tN, visited, G)
            if not pathFound:
                dN.append(node)
    return dN

def BFS(start, target, visited, G):
    q = queue.Queue()
    q.put(start)

    while not q.empty(): # while queue is not empty
        current = q.get()
        if current == target:
            return True
        if current not in visited:
            visited.append(current)
            for node in list(G.neighbors(current)):
                q.put(node)
    return False