import streamlit as st
import pandas as pd
import difflib

st.set_page_config(page_title="SiCProD Dashboard")

@# Cache so the CSV isn't re-read from disk on every interaction
@st.cache_data
def load_data():
    return pd.read_csv("table_7.csv")

df = load_data()

section = st.sidebar.radio("View", ["Gender Distribution", "Name Search"])

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

    query = st.text_input("Search for a name (Nachname or Vorname)")

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
                st.write("Did you mean: {', '.join(close_matches)}?")

        else:
            st.write("Found {len(results)} matching record(s):")
            st.dataframe(results)
    
    else:
        st.caption("Type a name above to search.")