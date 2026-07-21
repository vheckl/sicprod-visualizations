import streamlit as st
import pandas as pd
import difflib
import networkx as nx
import matplotlib.pyplot as plt

st.set_page_config(page_title="SiCProD Dashboard")

# Cache so the CSV isn't re-read from disk on every interaction
@st.cache_data
def load_marriages():
    return pd.read_csv("table_10.csv")

@st.cache_data
def load_data():
    return pd.read_csv("table_11.csv")

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
    st.caption("Based on {total} person records.")

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

    G = nx.Graph()

    for _, row in merged.iterrows():
        G.add_edge(row["Subj object id"], row["Obj object id"])

    fig, ax = plt.subplots(figsize=(16, 16))
    pos = nx.spring_layout(G, seed=42)

    nx.draw(
    G,
    pos,
    ax=ax,
    node_size=20,
    node_color="steelblue",
    edge_color="lightgray",
    with_labels=False,
)
    st.pyplot(fig)

    components = list(nx.connected_components(G))
        
    st.write(f"Number of components: {len(components)}")
    st.write(f"Component sizes: {sorted([len(c) for c in components], reverse=True)}")




