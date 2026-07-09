import streamlit as st
from graphviz import Digraph


def draw_architecture(
    workers,
    infra=0,
    storage="OpenShift Data Foundation",
    network="25Gb",
    gpu=False,
):
    """
    Genera un diagrama de arquitectura de OpenShift Virtualization.

    workers : cantidad de Worker Nodes
    infra   : Infra Nodes
    storage : backend de almacenamiento
    network : velocidad de red
    gpu     : True/False
    """

    dot = Digraph("OpenShift")

    dot.attr(rankdir="TB")
    dot.attr(fontsize="12")
    dot.attr("node", shape="box", style="rounded,filled")

    ####################################################
    # Load Balancer
    ####################################################

    dot.node(
        "LB",
        "Load Balancer\nAPI / Ingress",
        fillcolor="lightblue"
    )

    ####################################################
    # Masters
    ####################################################

    dot.node(
        "M1",
        "Master-1",
        fillcolor="lightyellow"
    )

    dot.node(
        "M2",
        "Master-2",
        fillcolor="lightyellow"
    )

    dot.node(
        "M3",
        "Master-3",
        fillcolor="lightyellow"
    )

    dot.edge("LB", "M1")
    dot.edge("LB", "M2")
    dot.edge("LB", "M3")

    ####################################################
    # Infra Nodes
    ####################################################

    previous = "M1"

    for i in range(infra):

        node = f"I{i+1}"

        dot.node(
            node,
            f"Infra-{i+1}",
            fillcolor="khaki"
        )

        dot.edge(previous, node)

    ####################################################
    # Worker Nodes
    ####################################################

    for i in range(workers):

        worker = f"W{i+1}"

        label = f"Worker-{i+1}"

        if gpu:
            label += "\nGPU"

        dot.node(
            worker,
            label,
            fillcolor="palegreen"
        )

        dot.edge("M1", worker)
        dot.edge("M2", worker)
        dot.edge("M3", worker)

    ####################################################
    # Storage
    ####################################################

    dot.node(
        "ST",
        storage,
        shape="cylinder",
        fillcolor="orange"
    )

    for i in range(workers):

        dot.edge(
            f"W{i+1}",
            "ST"
        )

    ####################################################
    # Virtual Machines
    ####################################################

    dot.node(
        "VM",
        "Virtual Machines\nWindows / Linux",
        shape="folder",
        fillcolor="white"
    )

    dot.edge(
        "ST",
        "VM"
    )

    ####################################################
    # Networking
    ####################################################

    dot.node(
        "NET",
        f"Network\n{network}",
        shape="ellipse",
        fillcolor="lightcyan"
    )

    dot.edge(
        "NET",
        "LB"
    )

    ####################################################
    # Cluster Info
    ####################################################

    dot.node(
        "INFO",
        f"""
OpenShift Virtualization

Masters : 3
Workers : {workers}
Infra   : {infra}
Storage : {storage}
Network : {network}
""",
        shape="note",
        fillcolor="white"
    )

    dot.edge(
        "INFO",
        "LB",
        style="dashed"
    )

    ####################################################
    # Mostrar en Streamlit
    ####################################################

    st.graphviz_chart(
        dot,
        use_container_width=True
    )
