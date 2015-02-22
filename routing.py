#! /usr/bin/env python2

from __future__ import division

import pygame
import math
import sys
import time
import random

from tsp_greedy import solve_tsp

MAX=9999.0

N=30

WIDTH=640
HEIGHT=480
white = (255,255,255)
node_color = (240, 50, 60)
edge_color = (180, 180, 250)

min_x = MAX
min_y = MAX
max_x = -MAX
max_y = -MAX

def norm(n):
    global min_x, min_y, max_x, max_y
    m = 20
    n1 = ((n[0] - min_x) / (max_x - min_x), (n[1] - min_y) / (max_y - min_y))
    n1 = (n1[0] * (WIDTH - 2 * m) + m, n1[1] * (HEIGHT - 2 * m) + m)
    n1 = (int(n1[0]), int(n1[1]))
    return n1

def draw_node(screen, n):
    pygame.draw.circle(screen, node_color, norm(n), 4, 4)

def draw_edge(screen, n1, n2):
    pygame.draw.line(screen, edge_color, norm(n1), norm(n2), 2)

def draw_graph(g):
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    screen.fill(white)
    for n in g:
        for n1 in g[n]:
            draw_edge(screen, n, n1)
    for n in g:
        draw_node(screen, n)

    pygame.display.update()

def find_edges(g):
    global min_x, min_y, max_x, max_y
    for n in g:
        if n[0] < min_x:
            min_x = n[0]
        if n[1] < min_y:
            min_y = n[1]
        if n[0] > max_x:
            max_x = n[0]
        if n[1] > max_y:
            max_y = n[1]

def gen_random_cycle():
    g = {}
    n0 = (random.uniform(0, 40), random.uniform(0, 40))
    n = (random.uniform(0, 40), random.uniform(0, 40))
    g[n0] = [n]
    for i in range(N):
        n1 = (random.uniform(0, 40), random.uniform(0, 40))
        g[n] = [n1]
        n = n1
    g[n] = [n0]
    return g

def gen_random_points():
    ns = []
    for i in range(N):
        ns.append((random.uniform(0, 40), random.uniform(0, 40)))
    return ns

def gen_graph(ns):
    g = {}
    for n in ns:
        g[n] = ns
    return g

def dist(n1, n2):
    return math.sqrt((n1[0] - n2[0])**2 + (n1[1] - n2[1])**2)

def gen_mat(ns):
    m = []
    for i in range(len(ns)):
        m.append([])
        for j in range(len(ns)):
            m[i].append(dist(ns[i], ns[j]))
    return m

def gen_graph_from_path(p, ns):
    g = {}
    for i in range(len(p) - 1):
        g[ns[p[i]]] = [ns[p[i+1]]]
    g[ns[p[len(p)-1]]] = []#[ns[p[0]]]
    return g

if __name__ == "__main__":
    #g = { (0, 0) : [(0, 1)] , (0, 1) : [(2, 3)] , (2, 3) : [(-1, 1)] , (-1, 1): [(3, -2)] , (3, -2) : [(0, 0)] }
    #g = gen_random_cycle()
    ns = gen_random_points()
    m = gen_mat(ns)
    p = solve_tsp(m)
    print(p)
    #g = gen_graph(ns)
    g = gen_graph_from_path(p, ns)
    find_edges(g)
    draw_graph(g)
    raw_input("Press Enter to continue...")
