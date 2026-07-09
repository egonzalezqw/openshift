import streamlit as st
import pandas as pd

from calculations import calculate_sizing
from architecture import draw_architecture
from recommendations import generate_recommendations

st.set_page_config(
    page_title="OpenShift Virtualization Assessment",
    page_icon="🚀",
    layout="wide"
)

st.title("🚀 OpenShift Virtualization Assessment & Sizing Tool")

st.sidebar.image(
    "https://www.redhat.com/profiles/rh/themes/redhatdotcom/img/logo.svg",
    width=180,
)

st.sidebar.header("Assessment")

customer = st.sidebar.text_input("Cliente")

project = st.sidebar.text_input("Proyecto")

environment = st.sidebar.selectbox(
    "Ambiente",
    [
        "Development",
        "Testing",
        "Production"
    ]
)

architecture = st.sidebar.selectbox(
    "Arquitectura",
    [
        "Compact",
        "Standard",
        "Enterprise"
    ]
)

criticality = st.sidebar.selectbox(
    "Criticidad",
    [
        "Media",
        "Alta",
        "Mission Critical"
    ]
)

growth = st.sidebar.slider(
    "Crecimiento esperado (%)",
    0,
    100,
    20
)

tabs = st.tabs([
    "Assessment",
    "Compute",
    "Storage",
    "Networking",
    "Resultados"
])

#######################################################
# TAB 1
#######################################################

with tabs[0]:

    st.header("Assessment")

    col1,col2 = st.columns(2)

    with col1:

        clusters = st.number_input(
            "Clusters VMware",
            1,
            100,
            1
        )

        hosts = st.number_input(
            "Hosts por Cluster",
            1,
            128,
            3
        )

        vms = st.number_input(
            "Cantidad de VMs",
            1,
            100000,
            150
        )

    with col2:

        windows = st.slider(
            "Windows %",
            0,
            100,
            50
        )

        linux = 100-windows

        st.metric(
            "Linux %",
            linux
        )

        gpu = st.checkbox(
            "GPU Required"
        )

#######################################################
# TAB 2
#######################################################

with tabs[1]:

    st.header("Compute")

    col1,col2,col3 = st.columns(3)

    with col1:

        total_vcpu = st.number_input(
            "Total vCPU",
            1,
            500000,
            400
        )

    with col2:

        total_ram = st.number_input(
            "RAM Total (GB)",
            1,
            100000,
            1024
        )

    with col3:

        cores = st.number_input(
            "Cores por Nodo",
            8,
            256,
            64
        )

#######################################################
# TAB 3
#######################################################

with tabs[2]:

    st.header("Storage")

    storage = st.number_input(
        "Capacidad (TB)",
        1,
        5000,
        50
    )

    storage_type = st.selectbox(
        "Tipo",
        [
            "OpenShift Data Foundation",
            "NetApp",
            "Dell PowerFlex",
            "Pure Storage",
            "NFS"
        ]
    )

    rwx = st.checkbox(
        "Live Migration (RWX)"
    )

#######################################################
# TAB 4
#######################################################

with tabs[3]:

    st.header("Networking")

    network_speed = st.selectbox(
        "Velocidad",
        [
            "10Gb",
            "25Gb",
            "40Gb",
            "100Gb"
        ]
    )

    multus = st.checkbox("Multus")

    sriov = st.checkbox("SR-IOV")

#######################################################
# TAB 5
#######################################################

with tabs[4]:

    st.header("Resultados")

    if st.button("🚀 Calcular Infraestructura"):

        result = calculate_sizing(
            total_vcpu,
            total_ram,
            storage,
            growth,
            cores
        )

        c1,c2,c3,c4 = st.columns(4)

        c1.metric(
            "Workers",
            result["workers"]
        )

        c2.metric(
            "Masters",
            result["masters"]
        )

        c3.metric(
            "CPU",
            result["cpu"]
        )

        c4.metric(
            "RAM",
            result["ram"]
        )

        st.divider()

        st.subheader("Arquitectura")

        draw_architecture(
            result["workers"]
        )

        st.divider()

        st.subheader("Assessment Score")

        score = result["score"]

        st.progress(score/100)

        st.metric(
            "Infrastructure Ready",
            f"{score}%"
        )

        st.divider()

        st.subheader("Recomendaciones")

        rec = generate_recommendations(
            result,
            gpu,
            rwx,
            network_speed,
            storage_type
        )

        for r in rec:
            st.success(r)

        st.divider()

        st.subheader("Sizing")

        df = pd.DataFrame({

            "Recurso":[
                "CPU",
                "RAM",
                "Storage"
            ],

            "Cantidad":[
                result["cpu"],
                result["ram"],
                result["storage"]
            ]

        })

        st.bar_chart(
            df.set_index("Recurso")
        )

        csv = df.to_csv(index=False).encode()

        st.download_button(
            "📥 Descargar Reporte",
            csv,
            "Sizing.csv",
            "text/csv"
        )
