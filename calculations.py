import math


def calculate_sizing(
    total_vcpu,
    total_ram,
    storage_tb,
    growth,
    cores_per_node,
    ram_per_node=256,
    cpu_overcommit=4,
    ram_reservation=0.15,
):
    """
    Motor de sizing para OpenShift Virtualization

    Parámetros
    ----------
    total_vcpu : int
    total_ram : int (GB)
    storage_tb : int (TB)
    growth : %
    cores_per_node : cores físicos
    ram_per_node : GB
    cpu_overcommit : relación vCPU/Core
    ram_reservation : reserva para OpenShift

    Retorna un diccionario con el sizing completo.
    """

    ##################################################
    # FACTORES DE CRECIMIENTO
    ##################################################

    cpu_required = total_vcpu * 1.20
    ram_required = total_ram * 1.30
    storage_required = storage_tb * (1 + growth / 100)

    ##################################################
    # RESERVA PARA OPENSHIFT
    ##################################################

    usable_ram = ram_per_node * (1 - ram_reservation)

    ##################################################
    # CAPACIDAD POR WORKER
    ##################################################

    cpu_capacity_node = cores_per_node * cpu_overcommit
    ram_capacity_node = usable_ram

    ##################################################
    # WORKERS POR CPU
    ##################################################

    workers_cpu = math.ceil(
        cpu_required / cpu_capacity_node
    )

    ##################################################
    # WORKERS POR RAM
    ##################################################

    workers_ram = math.ceil(
        ram_required / ram_capacity_node
    )

    workers = max(workers_cpu, workers_ram)

    ##################################################
    # MINIMO RECOMENDADO
    ##################################################

    if workers < 3:
        workers = 3

    ##################################################
    # MASTERS
    ##################################################

    masters = 3

    ##################################################
    # INFRA NODES
    ##################################################

    infra = 0

    if workers >= 8:
        infra = 2

    if workers >= 20:
        infra = 3

    ##################################################
    # LICENCIAMIENTO
    ##################################################

    total_nodes = masters + workers + infra

    subscriptions = math.ceil(
        (cores_per_node * total_nodes) / 128
    )

    ##################################################
    # SCORE
    ##################################################

    score = 100

    if workers < 3:
        score -= 20

    if cpu_overcommit > 6:
        score -= 15

    if ram_reservation < 0.10:
        score -= 10

    if growth < 15:
        score -= 10

    ##################################################
    # NIVEL DE ARQUITECTURA
    ##################################################

    if workers <= 5:
        architecture = "Compact"

    elif workers <= 15:
        architecture = "Standard"

    else:
        architecture = "Enterprise"

    ##################################################
    # RESULTADO
    ##################################################

    return {

        "cpu": round(cpu_required),

        "ram": round(ram_required),

        "storage": round(storage_required, 2),

        "workers": workers,

        "masters": masters,

        "infra": infra,

        "total_nodes": total_nodes,

        "subscriptions": subscriptions,

        "score": score,

        "architecture": architecture,

        "cpu_capacity_node": cpu_capacity_node,

        "ram_capacity_node": round(ram_capacity_node),

        "growth": growth

    }
