# CS351L – Lab 3 (Week 3) Submission
## Informed Search: Greedy Best-First Search & A*

Files in this folder:

| File | Contents |
|---|---|
| `lab3_search.py` | `greedy_best_first()`, `a_star()`, driver script, and both Part D mini-cases (cyber + SE grid) |
| `output.txt` | Console output of `python3 lab3_search.py` |
| `Lab3_Submission.md` | This document: Part B pseudocode and table, results, and reflection answers |

---

## Deliverable 1 — Part B: Pseudocode Design

### Completed generic Best-First Search template

```
function BEST-FIRST-SEARCH(start, goal, use_g_and_h):
    frontier ← priority queue ordered by f(n)
               // f(n) = g(n) + h(n) if use_g_and_h (A*), else f(n) = h(n) (Greedy)
    add start to frontier with g = 0, f = h(start)       // g(start) = 0, so f = h(start) for both
    parent ← empty map
    best_g ← { start: 0 }

    while frontier is not empty:
        node ← remove node with lowest f from frontier
        if node == goal:
            return RECONSTRUCT-PATH(node)

        for each (neighbour, step_cost) of node:
            new_g ← best_g[node] + step_cost
            if neighbour not in best_g or new_g < best_g[neighbour]:
                best_g[neighbour] ← new_g
                parent[neighbour] ← node
                if use_g_and_h:  f ← new_g + h(neighbour)   // A*
                else:            f ← h(neighbour)           // Greedy
                push (f, neighbour) onto frontier

    return failure
```

### Greedy Best-First Search (specialised)

```
function GREEDY-BEST-FIRST(start, goal):
    frontier ← priority queue ordered by h(n);  push (h(start), start)
    parent ← empty map;  explored ← ∅;  queued ← { start }
    while frontier is not empty:
        node ← pop lowest h
        if node == goal: return RECONSTRUCT-PATH(node)
        explored ← explored ∪ { node }
        for each (neighbour, step_cost) of node:          // step_cost is not used
            if neighbour ∉ explored and neighbour ∉ queued:
                parent[neighbour] ← node
                queued ← queued ∪ { neighbour }
                push (h(neighbour), neighbour)
    return failure
```

### A* Search (specialised)

```
function A-STAR(start, goal):
    frontier ← priority queue ordered by f(n);  push (h(start), g = 0, start)
    parent ← empty map;  best_g ← { start: 0 }
    while frontier is not empty:
        (f, g, node) ← pop lowest f
        if g > best_g[node]: continue                     // skip a stale, outdated entry
        if node == goal: return RECONSTRUCT-PATH(node), g
        for each (neighbour, step_cost) of node:
            new_g ← g + step_cost
            if neighbour ∉ best_g or new_g < best_g[neighbour]:
                best_g[neighbour] ← new_g
                parent[neighbour] ← node
                push (new_g + h(neighbour), new_g, neighbour)
    return failure
```

### Completed table

| Algorithm | f(n) formula | Does it need g(n)? | Does it need h(n)? |
|---|---|---|---|
| Greedy Best-First | f(n) = h(n) | No | Yes |
| A* | f(n) = g(n) + h(n) | Yes | Yes |

### Part B questions

1. **Why can Greedy use a simpler frontier update rule?** Greedy's priority is h(n), which is fixed for each node and does not depend on the path taken to reach it. A node's priority never changes after it is first discovered, so Greedy pushes each node once and never revises it. A*'s priority includes g(n), which can drop when a cheaper path is found, so A* must re-push the node with its new, lower f-value.
2. **Hand-trace of A\*:** Yes. The trace expands A(f=6), B(4), C(6), D(7), E(7), F(7), G(7). At F, G's entry improves from f=10 (via B) to f=7. The path found is A–C–D–E–F–G with cost 7, which matches Part A. The program's output confirms it.
3. **If every h(n) = 0:** f(n) = g(n), so A* orders the frontier purely by path cost so far. It becomes **Uniform Cost Search** from Week 2.

---

## Deliverables 2 & 3 — Implementation and Console Output

Run with `python3 lab3_search.py` (Python 3.8+, standard library only). Output, also in `output.txt`:

```
=== Part C: Network graph, A -> G ===
Greedy: ['A', 'B', 'G'] | cost: 10 | nodes expanded: 3
A*    : ['A', 'C', 'D', 'E', 'F', 'G'] | cost: 7 | nodes expanded: 7
```

| Algorithm | Path | Cost | Nodes expanded |
|---|---|---|---|
| Greedy Best-First | A → B → G | 10 | 3 |
| A* | A → C → D → E → F → G | 7 (optimal) | 7 |

Implementation notes:
- **Greedy** keeps a `queued` set so each node is pushed at most once, and its priority is `heuristic[neighbour]` only. `step_cost` is never used in the priority.
- **A\*** updates `best_g` and `parent` and re-pushes a neighbour whenever a cheaper `new_g` is found. This is what lets G improve from f=10 to f=7. A stale heap entry (`g > best_g[node]`) is skipped rather than expanded, so the expansion count stays accurate.

---

## Deliverable 4 — Part D Mini-Cases (both completed)

### Cybersecurity: attack-path investigation

`a_star()` is reused **unchanged** on `attack_graph` with `risk_score` as the heuristic:

```
Most likely attack path: ['Perimeter', 'AppServer', 'DBGateway', 'BackupSrv', 'SIEMRelay', 'CrownJewel'] | estimated total risk: 7 | nodes expanded: 7
(Greedy for comparison) : ['Perimeter', 'Workstation', 'CrownJewel'] | risk: 10 | nodes expanded: 3
```

A* avoids the tempting but costly Workstation → CrownJewel hop (difficulty 9). It returns the true lowest-difficulty route with total risk 7. Greedy is fooled in exactly the way it was in Part A.

### Software engineering: A* grid pathfinding

`a_star_grid()` uses the same core loop as `a_star()`. The only changes are that `graph[node]` becomes `grid_neighbours(node, walls, width, height)` and `heuristic[node]` becomes `manhattan(node, goal)`. The test is an 8×6 grid with two wall segments, running from (0,0) to (7,5):

```
Cost: 18 | nodes expanded: 36
S . . # . . . .
* . . # * * * .
* . . # * # * .
* . . # * # * .
* * * * * # * .
. . . . . # * G
```

Legend: `#` wall, `S` start, `G` goal, `*` path. Cost 18 is optimal. The route must pass below the first wall (x=3), go back up over the second wall (x=5), then come down to the goal. Checking by hand: 7 + 1 + 3 + 1 + 6 = 18.

---

## Deliverable 5 — Reflection & Discussion Answers

**1. Greedy vs A\* results, compared with Part A.**
Greedy returned A–B–G with cost 10 after 3 expansions. A* returned A–C–D–E–F–G with cost 7 after 7 expansions. This matches the Part A hand-traces exactly. Greedy is faster because it expands fewer nodes, but it is suboptimal because it was lured by h(B)=3. A* does more work but finds the optimal cost-7 path, the same one UCS found in Week 2.

**2. What if h(B) = 8?**
Greedy would **not** be fooled. After expanding A, the frontier would be {B:8, C:4}, so Greedy picks C. From there D(3), E(2), F(1) and G(0) always have a lower h than B(8). B is never expanded, and Greedy follows A–C–D–E–F–G with cost 7. The program's check confirms this: `Greedy: ['A','C','D','E','F','G'] | cost: 7 | nodes expanded: 6`. Greedy is only as good as its heuristic. Here h(B)=8 is exact (h = h\*), so it points the right way, but Greedy still gives no general optimality guarantee.

**3. Why would an incident-response team prefer A\* over Greedy?**
In security, a wrong answer costs more than a slightly slower one. Greedy picked the Workstation → CrownJewel path, which is actually the hardest route (risk 10). If the team hardened that path, they would leave the real easiest route (Perimeter → AppServer → … → SIEMRelay → CrownJewel, risk 7) open. With an admissible risk score, A* is guaranteed to find the true most-likely (lowest-cost) attack path, so defensive effort goes where it matters. The extra few node expansions cost almost nothing next to a missed attack path.

**4. What happens with an inadmissible heuristic on the grid?**
A* would still run and still terminate on a finite grid, and it would still return *a* valid path. However, the path is **no longer guaranteed optimal**. An overestimating h can make a node on the true shortest route look worse than it is. A* may then reach the goal through a longer route before it ever expands the better one. On a game map or warehouse floor, this means characters or robots sometimes take visibly longer detours. The usual trade-off is that an overestimating heuristic often expands fewer nodes, so it runs faster at the cost of path quality.

**5. Relationship between A\* and UCS.**
A* is UCS with a heuristic added to the priority: UCS orders by g(n), and A* orders by g(n) + h(n). A* behaves exactly like UCS when **h(n) = 0 for every node** (more generally, when h is a constant for all nodes), because the ordering then depends only on g(n).
