import streamlit as st
import heapq
import networkx as nx
import matplotlib.pyplot as plt

# --- Set up Streamlit Page ---
st.set_page_config(page_title="MST Visualizer (DAA Experiment)", layout="wide")
st.title("🔀 Minimum Spanning Tree Visualizer")
st.markdown("### Design and Analysis of Algorithms Experiment")
st.write("Compare **Kruskal's Algorithm** (Edge-based using Union-Find) and **Prim's Algorithm** (Vertex-based using Min-Priority Queue).")

# --- Union-Find for Kruskal ---
class UnionFind:
    def __init__(self, n):
        self.parent = list(range(n))
        self.rank   = [0] * n

    def find(self, x):
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])  # Path compression
        return self.parent[x]

    def union(self, x, y):
        rx, ry = self.find(x), self.find(y)
        if rx == ry: return False
        if self.rank[rx] < self.rank[ry]: rx, ry = ry, rx
        self.parent[ry] = rx
        if self.rank[rx] == self.rank[ry]: self.rank[rx] += 1
        return True

def kruskal(n, edges):
    """edges: list of (weight, u, v)"""
    edges.sort()  
    uf   = UnionFind(n)
    mst  = []
    cost = 0
    for w, u, v in edges:
        if uf.union(u, v):
            mst.append((u, v, w))
            cost += w
            if len(mst) == n - 1:
                break
    return mst, cost

def prim(n, adj, start=0):
    """adj: adjacency list {u: [(v, w), ...]}"""
    INF    = float('inf')
    key    = [INF] * n
    parent = [-1]  * n
    inMST  = [False] * n
    key[start] = 0
    pq = [(0, start)]
    mst = []
    cost = 0
    while pq:
        w, u = heapq.heappop(pq)
        if inMST[u]: continue
        inMST[u] = True
        if parent[u] != -1:
            mst.append((parent[u], u, w))
            cost += w
        for v, wt in adj.get(u, []):
            if not inMST[v] and wt < key[v]:
                key[v] = wt
                parent[v] = u
                heapq.heappush(pq, (wt, v))
    return mst, cost

# --- Graph Definition ---
n = 7
edges = [
    (7, 0, 1), (5, 0, 3), (8, 1, 2), (9, 1, 3),
    (7, 1, 4), (5, 2, 4), (15, 3, 4), (6, 3, 5),
    (8, 4, 5), (9, 4, 6), (11, 5, 6)
]
adj = {}
for w, u, v in edges:
    adj.setdefault(u, []).append((v, w))
    adj.setdefault(v, []).append((u, w))

# --- Graph Visualization Helper ---
def draw_graph(mst_edges=None, title="Graph"):
    G = nx.Graph()
    for w, u, v in edges:
        G.add_edge(u, v, weight=w)
    
    # Static layout so nodes don't move around when switching tabs
    pos = nx.spring_layout(G, seed=42) 
    
    fig, ax = plt.subplots(figsize=(6, 4))
    
    # Base graph drawing
    nx.draw_networkx_nodes(G, pos, node_color="#1f77b4", node_size=500, ax=ax)
    nx.draw_networkx_labels(G, pos, font_color="white", font_weight="bold", ax=ax)
    
    # Edge logic
    if mst_edges:
        # Format input tracking format to set pairs
        mst_set = set((u, v) for u, v, w in mst_edges)
        mst_set.update((v, u) for u, v, w in mst_edges)
        
        normal_edges = [e for e in G.edges() if e not in mst_set]
        highlighted_edges = [e for e in G.edges() if e in mst_set]
        
        nx.draw_networkx_edges(G, pos, edgelist=normal_edges, width=1.5, alpha=0.3, edge_color="gray", ax=ax)
        nx.draw_networkx_edges(G, pos, edgelist=highlighted_edges, width=3.0, edge_color="#d62728", ax=ax)
    else:
        nx.draw_networkx_edges(G, pos, width=1.5, edge_color="gray", ax=ax)
        
    labels = nx.get_edge_attributes(G, 'weight')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=labels, ax=ax, font_size=10)
    
    plt.title(title, fontsize=14)
    plt.axis('off')
    return fig

# --- Sidebar / Controls ---
st.sidebar.header("Configuration")
algo_choice = st.sidebar.radio("Select Algorithm to Visualise:", ["Original Graph Only", "Kruskal's Algorithm", "Prim's Algorithm"])

# --- Main Interface Logic ---
col1, col2 = st.columns([3, 2])

with col1:
    if algo_choice == "Original Graph Only":
        st.subheader("Input Graph Visualization")
        fig = draw_graph(title="Original Undirected Weighted Graph")
        st.pyplot(fig)
        
    elif algo_choice == "Kruskal's Algorithm":
        k_mst, k_cost = kruskal(n, edges[:])
        st.subheader("Kruskal's Minimum Spanning Tree (MST)")
        fig = draw_graph(mst_edges=k_mst, title=f"Kruskal's MST (Total Cost: {k_cost})")
        st.pyplot(fig)
        
    elif algo_choice == "Prim's Algorithm":
        p_mst, p_cost = prim(n, adj)
        st.subheader("Prim's Minimum Spanning Tree (MST)")
        fig = draw_graph(mst_edges=p_mst, title=f"Prim's MST (Total Cost: {p_cost})")
        st.pyplot(fig)

with col2:
    st.subheader("Execution Outputs")
    if algo_choice == "Original Graph Only":
        st.info("Select an algorithm from the sidebar to view the parsed output metrics.")
        st.markdown("**Input Edge List Layout:**")
        st.write(f"Total Nodes: `{n}`")
        st.write("Edges (Weight, U, V):", edges)
        
    elif algo_choice == "Kruskal's Algorithm":
        k_mst, k_cost = kruskal(n, edges[:])
        st.success(f"**Total MST Cost:** {k_cost}")
        st.markdown("#### Selected Tree Edges:")
        for u, v, w in k_mst:
            st.markdown(f"- 🟢 Edge **({u} - {v})** | Weight: `{w}`")
            
    elif algo_choice == "Prim's Algorithm":
        p_mst, p_cost = prim(n, adj)
        st.success(f"**Total MST Cost:** {p_cost}")
        st.markdown("#### Selected Tree Edges:")
        for u, v, w in p_mst:
            st.markdown(f"- 🔵 Edge **({u} - {v})** | Weight: `{w}`")
