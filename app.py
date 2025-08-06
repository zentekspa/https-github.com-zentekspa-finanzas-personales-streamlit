import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.title("App de Finanzas Personales")

menu = st.sidebar.selectbox("Selecciona una vista", ["Ingresos", "Egresos", "Presupuestos", "Dashboard"])

if "ingresos" not in st.session_state:
    st.session_state["ingresos"] = pd.DataFrame(columns=["Fecha", "Categoría", "Monto", "Descripción", "Medio de Pago", "Responsable"])
if "egresos" not in st.session_state:
    st.session_state["egresos"] = pd.DataFrame(columns=["Fecha", "Categoría", "Monto", "Descripción", "Medio de Pago", "Responsable"])
if "presupuestos" not in st.session_state:
    st.session_state["presupuestos"] = pd.DataFrame(columns=["Mes", "Año", "Categoría", "Monto Presupuestado"])

def ingreso_form(tipo):
    st.subheader(f"Agregar {tipo}")
    with st.form(key=f"{tipo}_form"):
        fecha = st.date_input("Fecha")
        categoria = st.text_input("Categoría")
        monto = st.number_input("Monto", min_value=0.0)
        descripcion = st.text_input("Descripción")
        medio = st.selectbox("Medio de Pago", ["Efectivo", "Tarjeta", "Transferencia"])
        responsable = st.text_input("Responsable")
        submit = st.form_submit_button("Guardar")
        if submit:
            nuevo = {
                "Fecha": fecha,
                "Categoría": categoria,
                "Monto": monto,
                "Descripción": descripcion,
                "Medio de Pago": medio,
                "Responsable": responsable
            }
            if tipo == "Ingreso":
                st.session_state["ingresos"] = pd.concat([st.session_state["ingresos"], pd.DataFrame([nuevo])], ignore_index=True)
            else:
                st.session_state["egresos"] = pd.concat([st.session_state["egresos"], pd.DataFrame([nuevo])], ignore_index=True)
            st.success(f"{tipo} guardado correctamente.")

def presupuesto_form():
    st.subheader("Agregar Presupuesto")
    with st.form(key="presupuesto_form"):
        mes = st.selectbox("Mes", list(range(1, 13)))
        año = st.number_input("Año", min_value=2000, max_value=2100, value=2024)
        categoria = st.text_input("Categoría")
        monto = st.number_input("Monto Presupuestado", min_value=0.0)
        submit = st.form_submit_button("Guardar")
        if submit:
            nuevo = {
                "Mes": mes,
                "Año": año,
                "Categoría": categoria,
                "Monto Presupuestado": monto
            }
            st.session_state["presupuestos"] = pd.concat([st.session_state["presupuestos"], pd.DataFrame([nuevo])], ignore_index=True)
            st.success("Presupuesto guardado correctamente.")

def dashboard():
    st.subheader("Dashboard Financiero")
    ingresos = st.session_state["ingresos"]
    egresos = st.session_state["egresos"]
    presupuestos = st.session_state["presupuestos"]

    total_ingresos = ingresos["Monto"].sum()
    total_egresos = egresos["Monto"].sum()
    resultado = total_ingresos - total_egresos

    st.metric("Total Ingresos", f"${total_ingresos:,.2f}")
    st.metric("Total Egresos", f"${total_egresos:,.2f}")
    st.metric("Resultado", f"${resultado:,.2f}")

    fig, ax = plt.subplots()
    ingresos_por_categoria = ingresos.groupby("Categoría")["Monto"].sum()
    egresos_por_categoria = egresos.groupby("Categoría")["Monto"].sum()
    categorias = list(set(ingresos_por_categoria.index).union(set(egresos_por_categoria.index)))
    ingresos_valores = [ingresos_por_categoria.get(cat, 0) for cat in categorias]
    egresos_valores = [egresos_por_categoria.get(cat, 0) for cat in categorias]
    ax.bar(categorias, ingresos_valores, label="Ingresos")
    ax.bar(categorias, egresos_valores, bottom=ingresos_valores, label="Egresos")
    ax.set_ylabel("Monto")
    ax.set_title("Ingresos vs Egresos por Categoría")
    ax.legend()
    st.pyplot(fig)

    if not presupuestos.empty:
        comparativo = presupuestos.copy()
        comparativo["Gasto Real"] = comparativo.apply(
            lambda row: egresos[(egresos["Categoría"] == row["Categoría"]) &
                                (pd.to_datetime(egresos["Fecha"]).dt.month == row["Mes"]) &
                                (pd.to_datetime(egresos["Fecha"]).dt.year == row["Año"])]["Monto"].sum(), axis=1)
        st.dataframe(comparativo)

if menu == "Ingresos":
    ingreso_form("Ingreso")
    st.dataframe(st.session_state["ingresos"])
elif menu == "Egresos":
    ingreso_form("Egreso")
    st.dataframe(st.session_state["egresos"])
elif menu == "Presupuestos":
    presupuesto_form()
    st.dataframe(st.session_state["presupuestos"])
elif menu == "Dashboard":
    dashboard()
