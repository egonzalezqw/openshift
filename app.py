import streamlit as st
import pandas as pd

st.set_page_config(page_title="OpenShift Virtualization Sizing", layout="wide")

st.title("🚀 OpenShift Virtualization Sizing Tool")

# -------------------------
# TABS
# -------------------------
tab1, tab2, tab3, tab4 = st.tabs(["General", "Workloads", "Storage", "Resultados"])

# -------------------------
# TAB 1 - GENERAL
# -------------------------
with tab1:
    st.header("Información General")

    clusters = st.number_input("Cantidad de clusters VMware", min_value=1, value=1)
    hosts = st.number_input("Hipervisores por cluster", min_value=1, value=3)
    sockets = st.number_input("Sockets por host", min_value=1, value=2)

    total_vms = st.number_input("Cantidad total de VMs", min_value=1, value=10)
    total_vcpu = st.number_input("Total vCPU asignadas", min_value=1, value=40)
    total_ram = st.number_input("Total RAM (GB)", min_value=1, value=128)

# -------------------------
# TAB 2 - WORKLOADS
# -------------------------
with tab2:
    st.header("Cargas de Trabajo")

    windows_pct = st.slider("% Windows", 0, 100, 50)
    rhel_pct = 100 - windows_pct

    gpu_required = st.selectbox("¿Requiere GPU?", ["No", "Sí"])
    migration_type = st.selectbox("Tipo de migración", ["En frío", "En caliente"])

# -------------------------
# TAB 3 - STORAGE
# -------------------------
with tab3:
    st.header("Almacenamiento")

    storage_total = st.number_input("Storage total (TB)", min_value=1, value=10)
    storage_growth = st.slider("Crecimiento esperado (%)", 0, 100, 20)

    rwx_required = st.selectbox("¿Requiere RWX (Live Migration)?", ["Sí", "No"])

# -------------------------
# TAB 4 - RESULTADOS
# -------------------------
with tab4:
    st.header("Resultados de Sizing")

    if st.button("Calcular"):

        # -------------------------
        # CÁLCULOS
        # -------------------------
        cpu_required = total_vcpu * 1.2
        ram_required = total_ram * 1.3
        storage_required = storage_total * (1 + storage_growth / 100) * 1.2

        # Suposiciones de nodo
        cpu_per_node = 32
        ram_per_node = 128

        nodes_cpu = cpu_required / cpu_per_node
        nodes_ram = ram_required / ram_per_node

        nodes_required = int(max(nodes_cpu, nodes_ram)) + 1

        # -------------------------
        # RESULTADOS
        # -------------------------
        col1, col2, col3 = st.columns(3)

        col1.metric("CPU requerida (vCPU)", round(cpu_required, 2))
        col2.metric("RAM requerida (GB)", round(ram_required, 2))
        col3.metric("Storage requerido (TB)", round(storage_required, 2))

        st.subheader("Infraestructura sugerida")
        st.success(f"🔹 Nodos requeridos: {nodes_required}")

        if gpu_required == "Sí":
            st.warning("⚠️ Considerar nodos con GPU")

        if rwx_required == "Sí":
            st.info("📦 Se requiere almacenamiento RWX (Live Migration)")

        # -------------------------
        # GRÁFICO
        # -------------------------
        st.subheader("Resumen de recursos")

        chart_data = pd.DataFrame({
            "Recurso": ["CPU", "RAM", "Storage"],
            "Cantidad": [cpu_required, ram_required, storage_required]
        })

        st.bar_chart(chart_data.set_index("Recurso"))

        # -------------------------
        # REPORTE DESCARGABLE
        # -------------------------
        st.subheader("Exportar resultados")

        report = pd.DataFrame({
            "Parametro": [
                "Clusters", "Hosts", "VMs", "CPU requerida",
                "RAM requerida", "Storage requerido", "Nodos"
            ],
            "Valor": [
                clusters, hosts, total_vms, cpu_required,
                ram_required, storage_required, nodes_required
            ]
        })

        csv = report.to_csv(index=False).encode('utf-8')

        st.download_button(
            label="📥 Descargar reporte CSV",
            data=csv,
            file_name="openshift_sizing.csv",
            mime="text/csv"
        )
