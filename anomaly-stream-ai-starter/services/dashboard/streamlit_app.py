
import os, glob, duckdb, pandas as pd, streamlit as st

LAKE_EVENTS = "lake/events/dt=*/part-*.parquet"
LAKE_ANOMS  = "lake/anomalies/dt=*/part-*.parquet"

st.set_page_config(page_title="AI Anomaly Stream", layout="wide")
st.title("🤖 AI Anomaly Stream — Live Dashboard")

con = duckdb.connect(database=":memory:")
con.execute("INSTALL httpfs; LOAD httpfs;")

left, right = st.columns(2)

# Events
event_files = glob.glob(LAKE_EVENTS)
if event_files:
    df_events = con.execute(f"""
      SELECT CAST(ts AS TIMESTAMP) AS ts, user_id,
             metric1, metric2, metric3, feature_a, feature_b, tag
      FROM read_parquet('{LAKE_EVENTS}')
    """).fetchdf()

    with left:
        st.subheader("Event Rate (by minute)")
        rate = (df_events.assign(minute=pd.to_datetime(df_events["ts"]).dt.floor("min"))
                         .groupby("minute", as_index=False)["user_id"].count()
                         .rename(columns={"user_id":"events"}))
        st.line_chart(rate.set_index("minute"))

else:
    st.info("No events parquet yet. Start API, processor, and generator.")

# Anomalies
anom_files = glob.glob(LAKE_ANOMS)
if anom_files:
    df_anom = con.execute(f"""
      SELECT CAST(ts AS TIMESTAMP) AS ts, user_id, score, is_anomaly,
             metric1, metric2, metric3
      FROM read_parquet('{LAKE_ANOMS}')
    """).fetchdf()

    with right:
        st.subheader("Anomaly Count (by minute)")
        ac = (df_anom.assign(minute=pd.to_datetime(df_anom["ts"]).dt.floor("min"))
                      .groupby("minute", as_index=False)["is_anomaly"].sum())
        st.line_chart(ac.set_index("minute"))

    st.subheader("Recent Anomalies")
    st.dataframe(df_anom.sort_values("ts", ascending=False).head(200))
else:
    st.warning("No anomalies yet — generate some load with spikes.")
