import streamlit as st
import pandas as pd
import difflib
import networkx as nx
import matplotlib.pyplot as plt
import math

st.set_page_config(page_title="SiCProD Dashboard")

# Cache so the CSV isn't re-read from disk on every interaction
@st.cache_data
def load_marriages():
    return pd.read_csv("table_marriages.csv")

@st.cache_data
def load_data():
    return pd.read_csv("table_person_data.csv")

df = load_data()
persons = load_data()
marriages = load_marriages()

section = st.sidebar.radio("View", ["Gender Distribution", "Name Search", "Marriage Distribution"])

if section == "Gender Distribution":
    st.title("SiCProD Persons — Gender Distribution")

    # Counting gender values, including missing ones
    gender_counts = df["Geschlecht"].value_counts(dropna=False)

    # Replacing the NaN label with 'not specified'
    gender_counts.index = gender_counts.index.fillna("not specified")

    st.subheader("Raw counts")
    st.write(gender_counts)

    st.subheader("Bar chart")
    st.bar_chart(gender_counts)

    total = len(df)
    st.caption(f"Based on {total} person records.")

elif section == "Name Search":
    st.title("SiCProD Persons — Name Search")

    query = st.text_input(f"Search for a name (Nachname or Vorname)")

    if query:
        # Search across surname, forename, and known name variants
        mask = (
            df["Name"].str.contains(query, case=False, na=False)
            | df["Vorname"].str.contains(query, case=False, na=False)
            | df["Alternative Namen"].str.contains(query, case=False, na=False)
        )
        results = df[mask]

        if len(results) == 0:
            # If no exact match, suggest similar names (handles typos and
            # the historical spelling variation common in this dataset)
            all_names = pd.concat([df["Name"], df["Vorname"]]).dropna().unique()
            close_matches = difflib.get_close_matches(query, all_names, n=10, cutoff=0.7)

            if len(close_matches) == 0:
                st.write("No results found.")

            else:
                st.write(f"Did you mean: {', '.join(close_matches)}?")

        else:
            st.write(f"Found {len(results)} matching record(s):")
            st.dataframe(results)
    
    else:
        st.caption(f"Type a name above to search.")

elif section == "Marriage Distribution":
    st.title("SicProd Marriage Distribution")

    merged = marriages.merge(persons, left_on="Subj object id", right_on="ID")
    merged = merged.merge(persons, left_on="Obj object id", right_on="ID", suffixes=("_subj", "_obj"))

    merged["FullName_subj"] = merged["Vorname_subj"].fillna("") + " " + merged["Name_subj"]
    merged["FullName_obj"] = merged["Vorname_obj"].fillna("") + " " + merged["Name_obj"]

    G = nx.Graph()

    for _, row in merged.iterrows():
        G.add_edge(row["Subj object id"], row["Obj object id"])
    
    components = list(nx.connected_components(G))
    big_components = [c for c in components if len(c) >= 3]

    col1, col2, col3 = st.columns(3)
    col1.metric("Total marriage records", len(marriages))
    col2.metric("Distinct marriages", G.number_of_edges())
    col3.metric("People who married more than once", len(big_components))   

    # Full graph
    st.subheader("Full network")
    fig1, ax1 = plt.subplots(figsize=(16, 16))
    pos = nx.spring_layout(G, seed=42, k=0.1)
    nx.draw(
    G,
    pos,
    ax=ax1,
    node_size=20,
    node_color="steelblue",
    edge_color="gray",
    with_labels=False,
)
    st.pyplot(fig1)

    # Filtered Graph 
    st.subheader("People who married more than once")

    nodes_to_keep = set()
    for component in big_components:
        nodes_to_keep.update(component)

    G_filtered = G.subgraph(nodes_to_keep)

    # Creating a dict with pairs of IDs and 
    # person names to give the graph as labels 
    subj_names = dict(zip(merged["Subj object id"], merged["FullName_subj"]))
    obj_names = dict(zip(merged["Obj object id"], merged["FullName_obj"]))

    all_names = {}
    all_names.update(subj_names)
    all_names.update(obj_names)

    # Dictionary comprehension to create a dict that only 
    # contains entries for nodes that exist in G_filtered
    filtered_labels = {node: all_names[node] for node in G_filtered.nodes() if node in all_names}

    # Set up grid and empty containers for more structured display
    n_cols = 2
    n_rows = math.ceil(len(big_components) / n_cols)

    spacing_x = 5
    spacing_y = 5

    combined_pos = {}
    combined_labels = {}

    # Looping through each cluster of big_components 
    # to give it's own cell to each 
    for i, component in enumerate(big_components):
        col = i % n_cols
        row = i // n_cols

        # Building each clusters tiny layout
        subgraph = G.subgraph(component)
        sub_pos = nx.spring_layout(subgraph, seed=42)

        for node, (x, y) in sub_pos.items():
            # Moving each cluster and each label into it's cell
            combined_pos[node] = (x + col * spacing_x, -y - row * spacing_y)
            combined_labels[node] = all_names.get(node, "")

    fig2, ax2 = plt.subplots(figsize=(14, 70))
    pos2 = nx.spring_layout(G_filtered, seed=42, k=0.1, scale=3)
    nx.draw(
        G_filtered,
        combined_pos,
        ax=ax2,
        labels=filtered_labels,
        node_size=300,
        node_color="lightsteelblue",
        edge_color="gray",
        with_labels=True,
        font_size=12,
    )

    xs = [p[0] for p in combined_pos.values()]
    ys = [p[1] for p in combined_pos.values()]
    ax2.set_xlim(min(xs) - 1, max(xs) + 1)
    ax2.set_ylim(min(ys) - 1, max(ys) + 1)
    st.pyplot(fig2)
