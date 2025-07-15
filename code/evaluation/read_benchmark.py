import streamlit as st
from algbench import describe, read_as_pandas
from dc_triangulation import format_dictionary

"""
streamlit run read_benchmark.py
"""

BENCHMARK_PATH = "./benchmark"
if False:
    describe(BENCHMARK_PATH)
else:
    df = read_as_pandas(
        BENCHMARK_PATH,
        lambda result: {
            "host": result["env"]["hostname"],
            "solver": result["parameters"]["args"]["solver_name"],
            "instance": result["parameters"]["args"]["instance_name"],
            "file": result["parameters"]["args"]["file_name"],
            "correct": result["result"]["correct"],
            "args": result["parameters"]["args"]["parameter"]["args"],
            "evaluation": result["result"]["evaluation"],
            "logging": result["logging"],
            "whole_runtime": result["runtime"],
            "timeout": result["parameters"]["args"]["parameter"]["timeout"],
            "time_solver": result["result"].get("time_solver", None),
            "time_pre_solver": result["result"].get("time_pre_solver", None),
        },
    )

    df["args"] = df["args"].apply(lambda x: format_dictionary(x, new_line=False))
    df["logging"] = df["logging"].apply(lambda x: str(x))
    df.sort_values(
        by=["host", "solver", "instance", "file"],
        inplace=True,
    )

    st.dataframe(df)
    # # Als HTML-Tabelle rendern
    # html = df.to_html(escape=False)
    # st.markdown(html, unsafe_allow_html=True)
