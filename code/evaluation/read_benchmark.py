import streamlit as st
from algbench import describe, read_as_pandas

"""
streamlit run read_benchmark.py
"""

BENCHMARK_PATH = "./benchmark"
# BENCHMARK_PATH = "./eval#8/lokal_benchmark"
if False:
    describe(BENCHMARK_PATH)
else:
    df = read_as_pandas(
        BENCHMARK_PATH,
        lambda result: {
            "host": result["env"]["hostname"],
            "para_host": result["parameters"]["args"].get("host", None),
            "solver": result["parameters"]["args"]["solver_name"],
            "instance": result["parameters"]["args"]["instance_name"],
            "file": result["parameters"]["args"]["file_name"],
            "correct": result["result"]["correct"],
            "args": result["parameters"]["args"]["parameter"].get("args", {}),
            "evaluation": result["result"]["evaluation"],
            "logging": result["logging"],
            "whole_runtime": result["runtime"],
            "timeout": result["parameters"]["args"]["parameter"]["timeout"],
            "time_solver": result["result"].get("time_solver", None),
            "time_pre_solver": result["result"].get("time_pre_solver", None),
            "count": result["result"].get("solution", {}).get("count", None),
            "solution": result["result"].get("solution", None),
            "data": result["timestamp"],
            "run_number": result["parameters"]["args"]["run_number"],
        },
    )
    if df.empty:
        st.error("Die Tabelle ist leer. Bitte überprüfen Sie die Eingabedaten.")
        st.stop()

    df["logging"] = df["logging"].apply(lambda x: str(x))

    # # Filtere nur Zeilen wo "Glucose42" in args enthalten ist
    # df = df[df["args"].astype(str).str.contains("Glucose42", na=False)]

    # df = df[
    #     df["host"].isin(
    #         ["algra01", "algra02", "algra03", "algra04", "algra05", "algra06"]
    #     )
    # ]

    df.sort_values(
        by=["solver", "instance", "file"],
        inplace=True,
    )

    st.dataframe(df)
    # # Als HTML-Tabelle rendern
    # html = df.to_html(escape=False)
    # st.markdown(html, unsafe_allow_html=True)
