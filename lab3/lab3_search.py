"""
CS351L - Artificial Intelligence Lab
Lab 3 - Week 3: Informed Search - Greedy Best-First Search & A*

Implements greedy_best_first() and a_star() on the Week 2/3 network graph,
plus both Part D mini-cases (cybersecurity attack path and SE grid pathfinding).
"""

import heapq


# ---------------------------------------------------------------------------
# 1. Graph & heuristic representation (given)
# ---------------------------------------------------------------------------
graph = {
    'A': [('B', 1), ('C', 2)],
    'B': [('A', 1), ('G', 9)],
    'C': [('A', 2), ('D', 2)],
    'D': [('C', 2), ('E', 1)],
    'E': [('D', 1), ('F', 1)],
    'F': [('E', 1), ('G', 1)],
    'G': [('B', 9), ('F', 1)],
}

heuristic = {'A': 6, 'B': 3, 'C': 4, 'D': 3, 'E': 2, 'F': 1, 'G': 0}


# ---------------------------------------------------------------------------
# 2. Path reconstruction helper (given, unchanged from Week 2)
# ---------------------------------------------------------------------------
def reconstruct_path(parent, goal):
    path = [goal]
    while path[-1] in parent:
        path.append(parent[path[-1]])
    path.reverse()
    return path


def path_cost(graph, path):
    """Sum the actual edge costs along a path (used to report Greedy's cost)."""
    if not path:
        return float('inf')
    total = 0
    for u, v in zip(path, path[1:]):
        total += dict(graph[u])[v]
    return total


# ---------------------------------------------------------------------------
# 3. Greedy Best-First Search - priority = h(n) only
# ---------------------------------------------------------------------------
def greedy_best_first(graph, heuristic, start, goal):
    frontier = [(heuristic[start], start)]     # (h(n), node) min-heap
    parent = {}
    explored = set()
    queued = {start}                           # nodes already pushed once
    nodes_expanded = 0

    while frontier:
        h, node = heapq.heappop(frontier)
        nodes_expanded += 1
        if node == goal:
            return reconstruct_path(parent, goal), nodes_expanded
        explored.add(node)

        for neighbour, step_cost in graph[node]:
            # Greedy ignores step_cost: its priority depends only on h(n),
            # which never changes, so a node is pushed at most once.
            if neighbour not in explored and neighbour not in queued:
                parent[neighbour] = node
                queued.add(neighbour)
                heapq.heappush(frontier, (heuristic[neighbour], neighbour))

    return None, nodes_expanded


# ---------------------------------------------------------------------------
# 4. A* Search - priority = f(n) = g(n) + h(n)
# ---------------------------------------------------------------------------
def a_star(graph, heuristic, start, goal):
    frontier = [(heuristic[start], 0, start)]   # (f(n), g(n), node) min-heap
    parent = {}
    best_g = {start: 0}
    nodes_expanded = 0

    while frontier:
        f, g, node = heapq.heappop(frontier)
        if g > best_g[node]:
            continue                            # stale entry, a cheaper route was found
        nodes_expanded += 1
        if node == goal:
            return reconstruct_path(parent, goal), g, nodes_expanded

        for neighbour, step_cost in graph[node]:
            new_g = g + step_cost
            if neighbour not in best_g or new_g < best_g[neighbour]:
                best_g[neighbour] = new_g
                parent[neighbour] = node
                new_f = new_g + heuristic[neighbour]
                heapq.heappush(frontier, (new_f, new_g, neighbour))

    return None, float('inf'), nodes_expanded


# ---------------------------------------------------------------------------
# 6. Part D - Cybersecurity mini-case: attack-path investigation
# ---------------------------------------------------------------------------
attack_graph = {
    'Perimeter':   [('Workstation', 1), ('AppServer', 2)],
    'Workstation': [('Perimeter', 1), ('CrownJewel', 9)],
    'AppServer':   [('Perimeter', 2), ('DBGateway', 2)],
    'DBGateway':   [('AppServer', 2), ('BackupSrv', 1)],
    'BackupSrv':   [('DBGateway', 1), ('SIEMRelay', 1)],
    'SIEMRelay':   [('BackupSrv', 1), ('CrownJewel', 1)],
    'CrownJewel':  [('Workstation', 9), ('SIEMRelay', 1)],
}
risk_score = {          # heuristic: estimated remaining risk to CrownJewel
    'Perimeter': 6, 'Workstation': 3, 'AppServer': 4, 'DBGateway': 3,
    'BackupSrv': 2, 'SIEMRelay': 1, 'CrownJewel': 0,
}


# ---------------------------------------------------------------------------
# 7. Part D - Software engineering mini-case: A* on a 2D grid
# ---------------------------------------------------------------------------
def manhattan(a, b):
    # Straight-line grid distance heuristic - admissible for 4-directional movement
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def grid_neighbours(pos, walls, width, height):
    x, y = pos
    candidates = [(x+1, y), (x-1, y), (x, y+1), (x, y-1)]
    result = []
    for cx, cy in candidates:
        if 0 <= cx < width and 0 <= cy < height and (cx, cy) not in walls:
            result.append(((cx, cy), 1))   # every grid step costs 1
    return result


def a_star_grid(walls, width, height, start, goal):
    """Same A* loop as a_star(); only the neighbour lookup and heuristic differ."""
    frontier = [(manhattan(start, goal), 0, start)]
    parent = {}
    best_g = {start: 0}
    nodes_expanded = 0

    while frontier:
        f, g, node = heapq.heappop(frontier)
        if g > best_g[node]:
            continue
        nodes_expanded += 1
        if node == goal:
            return reconstruct_path(parent, goal), g, nodes_expanded

        for neighbour, step_cost in grid_neighbours(node, walls, width, height):
            new_g = g + step_cost
            if neighbour not in best_g or new_g < best_g[neighbour]:
                best_g[neighbour] = new_g
                parent[neighbour] = node
                new_f = new_g + manhattan(neighbour, goal)
                heapq.heappush(frontier, (new_f, new_g, neighbour))

    return None, float('inf'), nodes_expanded


def render_grid(walls, width, height, start, goal, path):
    """Draw the grid: # wall, S start, G goal, * path, . free cell."""
    on_path = set(path or [])
    rows = []
    for y in range(height):
        row = []
        for x in range(width):
            cell = (x, y)
            if cell == start:
                row.append('S')
            elif cell == goal:
                row.append('G')
            elif cell in walls:
                row.append('#')
            elif cell in on_path:
                row.append('*')
            else:
                row.append('.')
        rows.append(' '.join(row))
    return '\n'.join(rows)


# ---------------------------------------------------------------------------
# 5. Driver / test script
# ---------------------------------------------------------------------------
if __name__ == '__main__':
    print('=== Part C: Network graph, A -> G ===')
    g_path, g_n = greedy_best_first(graph, heuristic, 'A', 'G')
    a_path, a_cost, a_n = a_star(graph, heuristic, 'A', 'G')

    print('Greedy:', g_path, '| cost:', path_cost(graph, g_path), '| nodes expanded:', g_n)
    print('A*    :', a_path, '| cost:', a_cost, '| nodes expanded:', a_n)

    print('\n=== Part D (Cyber): Attack-path investigation ===')
    path, cost, expanded = a_star(attack_graph, risk_score, 'Perimeter', 'CrownJewel')
    print('Most likely attack path:', path, '| estimated total risk:', cost,
          '| nodes expanded:', expanded)
    gp, gn = greedy_best_first(attack_graph, risk_score, 'Perimeter', 'CrownJewel')
    print('(Greedy for comparison) :', gp, '| risk:', path_cost(attack_graph, gp),
          '| nodes expanded:', gn)

    print('\n=== Part D (SE): A* grid pathfinding (4-directional, step cost 1) ===')
    width, height = 8, 6
    walls = {(3, 0), (3, 1), (3, 2), (3, 3), (5, 2), (5, 3), (5, 4), (5, 5)}
    start, goal = (0, 0), (7, 5)
    path, cost, expanded = a_star_grid(walls, width, height, start, goal)
    print('Path:', path)
    print('Cost:', cost, '| nodes expanded:', expanded)
    print(render_grid(walls, width, height, start, goal, path))

    print('\n=== Reflection Q2 check: h(B) = 8 ===')
    h_modified = dict(heuristic, B=8)
    gp, gn = greedy_best_first(graph, h_modified, 'A', 'G')
    print('Greedy:', gp, '| cost:', path_cost(graph, gp), '| nodes expanded:', gn)
