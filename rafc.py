import streamlit as st
import streamlit.components.v1 as components
from datetime import date
from html import escape

# ============================================================
# RAFC 2026 - SISTEMA DE LIQUIDACION DE ARROZ
# Version Streamlit: interfaz y liquidacion
# ============================================================

st.set_page_config(
    page_title="RAFC 2026 - Liquidacion de Arroz",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded",
)

TARA_FIJA = 0.50
AUTOR = "Created by RAFC 2026"

# --------------------------- ESTILOS -------------------------
st.markdown(
    """
    <style>
    :root { --rafc-green:#07552b; --rafc-green2:#16813b; --rafc-gold:#e5b332; }
    .stApp { background:#f5f8f4; }
    [data-testid="stSidebar"] { background:linear-gradient(180deg,#064d28,#022f19); }
    [data-testid="stSidebar"] * { color:white !important; }
    .rafc-brand { text-align:center; padding:12px 4px 18px; }
    .rafc-brand .grain { font-size:62px; line-height:1.1; }
    .rafc-brand .name { color:#f1c64d; font-size:42px; font-weight:900; letter-spacing:2px; }
    .rafc-brand .tag { font-size:14px; font-weight:600; }
    .main-banner { background:linear-gradient(100deg,#fff 0%,#f4f8ef 50%,#fff 100%); border:2px solid #d8e5d5; border-radius:16px; padding:16px 20px; text-align:center; margin-bottom:18px; }
    .main-banner .grain { font-size:48px; }
    .main-banner .brand { font-size:46px; line-height:1; font-weight:900; color:#07552b; letter-spacing:3px; }
    .main-banner .subtitle { color:#176b37; font-size:20px; font-weight:700; }
    .section-card { background:white; border:1px solid #d9e4d7; border-radius:13px; padding:14px 16px; }
    div[data-testid="stMetric"] { background:#e6f4df; border:1px solid #82bd73; padding:14px; border-radius:12px; }
    .total-panel { background:#e5f5dc; border:2px solid #65ad54; border-radius:14px; padding:20px; text-align:center; }
    .total-panel .label { color:#07552b; font-weight:800; font-size:20px; }
    .total-panel .amount { color:#064b22; font-weight:900; font-size:34px; }
    .small-note { color:#607264; font-size:13px; }
    .stButton > button { border-radius:9px; font-weight:700; min-height:42px; }
    @media print { [data-testid="stSidebar"], header, footer {display:none !important;} }
    </style>
    """,
    unsafe_allow_html=True,
)

# ------------------------ ESTADO DE APP ----------------------
if "pagina" not in st.session_state:
    st.session_state.pagina = "liquidacion"
if "resultado_liquidacion" not in st.session_state:
    st.session_state.resultado_liquidacion = None

# --------------------- FUNCIONES DE APOYO --------------------
def formato_rd(valor):
    return f"RD$ {valor:,.2f}"


def banner_principal():
    st.markdown(
        """
        <div class="main-banner">
            <div class="grain">🌾 🌾</div>
            <div class="brand">RAFC</div>
            <div class="subtitle">Liquidación de Arroz</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def crear_recibo_html(datos):
    productor = escape(datos["productor"] or "No especificado")
    comprador = escape(datos["comprador"] or "No especificado")
    variedad = escape(datos["variedad"] or "No especificada")
    anio = escape(datos["anio"] or "No especificado")
    fecha_txt = datos["fecha"].strftime("%d/%m/%Y") if datos["mostrar_fecha"] else "No especificada"

    filas = [
        ("Total de sacos", f'{datos["sacos"]:,}'),
        ("Peso bruto", f'{datos["bruto"]:,.2f} kg'),
        ("Descuento por saco (0.50 kg)", "0.50 kg"),
        ("Descuento total", f'{datos["descuento"]:,.2f} kg'),
        ("Peso neto", f'{datos["neto"]:,.2f} kg'),
        ("Humedad", f'{datos["humedad"]}%'),
        ("Divisor aplicado", f'{datos["divisor"]}'),
        ("Rendimiento", f'{datos["rendimiento"]:,.4f} fanegas'),
        ("Precio por fanega", formato_rd(datos["precio"])),
        ("Precio por saco", formato_rd(datos["precio_saco"])),
    ]
    filas_html = "".join(
        f"<tr><td>{escape(concepto)}</td><td class='right'>{escape(resultado)}</td></tr>"
        for concepto, resultado in filas
    )

    return f"""<!DOCTYPE html>
<html lang="es"><head><meta charset="UTF-8">
<script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js"></script>
<style>
*{{box-sizing:border-box}} body{{font-family:Arial,sans-serif;margin:0;padding:12px;background:#fff;color:#17251a}}
.receipt{{border:3px solid #07552b;border-radius:12px;padding:16px;background:white;max-width:900px;margin:auto}}
.head{{text-align:center;border-bottom:2px solid #d7ad36;padding:5px 5px 13px;position:relative}}
.rice{{font-size:54px;line-height:1.1;color:#bd8a12}}
.logo{{font-size:48px;font-weight:900;letter-spacing:3px;color:#07552b;line-height:1.05}}
.title{{font-family:Georgia,serif;font-size:22px;font-weight:bold;color:#152319;margin-top:5px}}
.subtitle{{font-size:13px;font-weight:bold;letter-spacing:1px;margin-top:4px}}
.meta{{display:grid;grid-template-columns:1fr 1fr;gap:7px;margin:15px 0}}
.meta div{{border:1px solid #cad8ca;border-radius:5px;padding:8px;font-size:13px;min-height:34px}}
.section{{color:#07552b;font-weight:bold;margin:14px 0 7px;font-size:15px}}
table{{width:100%;border-collapse:collapse;font-size:13px}} th{{background:#e4efe1;color:#07552b;text-align:left}}
td,th{{border:1px solid #aebfae;padding:7px}} .right{{text-align:right}}
.total{{border:2px solid #68a94e;background:#e5f5dc;text-align:center;border-radius:9px;padding:13px;margin-top:13px;color:#07552b}}
.total strong{{font-size:17px}} .amount{{font-size:30px;font-weight:900;margin-top:4px}}
.signatures{{display:flex;justify-content:space-around;gap:35px;margin:38px 8px 14px;text-align:center;font-size:12px}}
.sign{{width:44%;border-top:1px solid #333;padding-top:7px}}
.footer{{text-align:right;font-family:Georgia,serif;font-style:italic;font-weight:bold;color:#07552b;margin-top:12px}}
.actions{{display:flex;gap:10px;margin:12px auto;max-width:900px}}
.actions button{{flex:1;border:0;border-radius:8px;padding:12px;color:white;background:#087b35;font-size:15px;font-weight:bold;cursor:pointer}}
.actions button:last-child{{background:#1769aa}}
@page{{size:A4 portrait;margin:8mm}}
@media print{{body{{padding:0}}.receipt{{border:2px solid #07552b;padding:10px}}.actions{{display:none!important}}*{{print-color-adjust:exact;-webkit-print-color-adjust:exact}}}}
</style></head><body>
<div class="receipt" id="rafc-receipt">
 <div class="head"><div class="rice">🌾 🌾 🌾</div><div class="logo">RAFC</div><div class="title">LIQUIDACIÓN DE ARROZ</div><div class="subtitle">RECIBO DE COMPRA Y RECEPCIÓN</div></div>
 <div class="section">DATOS GENERALES</div>
 <div class="meta">
  <div><b>Productor:</b> {productor}</div><div><b>Comprador:</b> {comprador}</div>
  <div><b>Variedad:</b> {variedad}</div><div><b>Año de cosecha:</b> {anio}</div>
  <div style="grid-column:1 / -1"><b>Fecha de liquidación:</b> {fecha_txt}</div>
 </div>
 <div class="section">DETALLES DE LIQUIDACIÓN</div>
 <table><thead><tr><th>Concepto</th><th class="right">Resultado</th></tr></thead><tbody>{filas_html}</tbody></table>
 <div class="total"><strong>TOTAL A PAGAR</strong><div class="amount">{escape(formato_rd(datos['total']))}</div></div>
 <div class="signatures"><div class="sign">Firma del Productor</div><div class="sign">Firma del Comprador</div></div>
 <div class="footer">Created by RAFC 2026</div>
</div>
<div class="actions"><button onclick="window.print()">🖨 Imprimir recibo</button><button onclick="descargarPNG()">⬇ Descargar PNG</button></div>
<script>
function descargarPNG(){{
 const el=document.getElementById('rafc-receipt');
 if(typeof html2canvas==='undefined'){{alert('No se pudo cargar la herramienta de imagen. Verifica tu conexion a Internet.');return;}}
 html2canvas(el,{{scale:2,backgroundColor:'#ffffff'}}).then(canvas=>{{
  const a=document.createElement('a');a.download='liquidacion_RAFC.png';a.href=canvas.toDataURL('image/png');a.click();
 }}).catch(()=>alert('No se pudo generar la imagen del recibo.'));
}}
</script></body></html>"""

# --------------------------- SIDEBAR -------------------------
with st.sidebar:
    st.markdown(
        """
        <div class="rafc-brand">
            <div class="grain">🌾</div>
            <div class="name">RAFC</div>
            <div class="tag">Sistema de<br>Liquidación de Arroz</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("---")
    if st.button("🌾  Nueva Liquidación", use_container_width=True):
        st.session_state.pagina = "liquidacion"
        st.rerun()
    if st.button("ⓘ  Acerca de RAFC", use_container_width=True):
        st.session_state.pagina = "acerca"
        st.rerun()
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    st.caption(AUTOR)

# ---------------------- PAGINA LIQUIDACION -------------------
if st.session_state.pagina == "liquidacion":
    banner_principal()
    st.markdown("## Nueva liquidación")
    st.caption("Los datos del productor y de la cosecha son opcionales. Solo necesitas completar los datos de cálculo.")

    izquierda, derecha = st.columns([1, 1.12], gap="large")
    with izquierda:
        st.markdown("### 🌾 Datos (opcionales)")
        productor = st.text_input("Productor", placeholder="Nombre del productor", key="prod")
        comprador = st.text_input("Comprador", placeholder="Nombre del comprador", key="comp")
        variedad = st.text_input("Variedad", placeholder="Variedad de arroz", key="variedad")
        anio_input = st.text_input("Año de cosecha", placeholder="Ej. 2026", key="anio")
        mostrar_fecha = st.checkbox("Incluir fecha automática en el recibo", value=True)
        fecha_liquidacion = date.today()
        st.caption("La fecha se coloca automáticamente; no tienes que escribirla.")

    with derecha:
        st.markdown("### ⚖️ Datos necesarios para calcular")
        sacos = st.number_input("Total de sacos", min_value=0, value=0, step=1, key="sacos")
        peso_bruto = st.number_input("Peso bruto (kg)", min_value=0.0, value=0.0, step=10.0, key="peso")
        humedad = st.number_input("Humedad (%)", min_value=0, value=0, step=1, format="%d", key="humedad")
        precio_fanega = st.number_input("Precio por fanega (RD$)", min_value=0.0, value=0.0, step=50.0, key="precio")
        st.info("Descuento fijo: 0.50 kg por cada saco. El divisor se calcula automáticamente: 100 + humedad.")
        calcular = st.button("▦  Calcular Liquidación", type="primary", use_container_width=True)

    if calcular:
        if sacos <= 0:
            st.error("Introduce una cantidad de sacos mayor que cero.")
            st.session_state.resultado_liquidacion = None
        elif peso_bruto <= 0:
            st.error("Introduce un peso bruto mayor que cero.")
            st.session_state.resultado_liquidacion = None
        elif precio_fanega <= 0:
            st.error("Introduce un precio por fanega mayor que cero.")
            st.session_state.resultado_liquidacion = None
        else:
            descuento = sacos * TARA_FIJA
            peso_neto = peso_bruto - descuento
            divisor = 100 + int(humedad)
            if peso_neto <= 0:
                st.error("El peso neto debe ser mayor que cero. Revisa el peso bruto y la cantidad de sacos.")
                st.session_state.resultado_liquidacion = None
            else:
                rendimiento = peso_neto / divisor
                total = rendimiento * precio_fanega
                precio_saco = total / sacos
                st.session_state.resultado_liquidacion = {
                    "productor": productor.strip(),
                    "comprador": comprador.strip(),
                    "variedad": variedad.strip(),
                    "anio": anio_input.strip(),
                    "fecha": fecha_liquidacion,
                    "mostrar_fecha": mostrar_fecha,
                    "sacos": int(sacos),
                    "bruto": float(peso_bruto),
                    "descuento": descuento,
                    "neto": peso_neto,
                    "humedad": int(humedad),
                    "divisor": divisor,
                    "rendimiento": rendimiento,
                    "precio": float(precio_fanega),
                    "precio_saco": precio_saco,
                    "total": total,
                }

    datos = st.session_state.resultado_liquidacion
    if datos:
        st.markdown("---")
        st.markdown("## ✅ Resultado de la liquidación")
        tabla_izq, total_der = st.columns([1.05, 0.9], gap="large")
        with tabla_izq:
            renglones = [
                ("Total de sacos", f"{datos['sacos']:,}"),
                ("Peso bruto", f"{datos['bruto']:,.2f} kg"),
                ("Descuento por saco", "0.50 kg"),
                ("Descuento total", f"{datos['descuento']:,.2f} kg"),
                ("Peso neto", f"{datos['neto']:,.2f} kg"),
                ("Humedad", f"{datos['humedad']}%"),
                ("Divisor aplicado", str(datos["divisor"])),
                ("Rendimiento", f"{datos['rendimiento']:,.4f} fanegas"),
                ("Precio por fanega", formato_rd(datos["precio"])),
                ("Precio por saco", formato_rd(datos["precio_saco"])),
            ]
            tabla_markdown = "| Concepto | Resultado |\n|:--|--:|\n" + "\n".join(
                f"| {concepto} | {valor} |" for concepto, valor in renglones
            )
            st.markdown(tabla_markdown)
        with total_der:
            st.markdown(
                f"<div class='total-panel'><div class='label'>TOTAL A PAGAR</div><div class='amount'>{escape(formato_rd(datos['total']))}</div></div>",
                unsafe_allow_html=True,
            )
            st.success("¡Cálculo realizado con éxito!")
            texto_txt = f"""RAFC - LIQUIDACIÓN DE ARROZ\n\nProductor: {datos['productor'] or 'No especificado'}\nComprador: {datos['comprador'] or 'No especificado'}\nVariedad: {datos['variedad'] or 'No especificada'}\nAño de cosecha: {datos['anio'] or 'No especificado'}\nFecha: {datos['fecha'].strftime('%d/%m/%Y') if datos['mostrar_fecha'] else 'No especificada'}\n\nTotal de sacos: {datos['sacos']}\nPeso bruto: {datos['bruto']:.2f} kg\nDescuento por saco: 0.50 kg\nDescuento total: {datos['descuento']:.2f} kg\nPeso neto: {datos['neto']:.2f} kg\nHumedad: {datos['humedad']}%\nDivisor aplicado: {datos['divisor']}\nRendimiento: {datos['rendimiento']:.4f} fanegas\nPrecio por fanega: RD$ {datos['precio']:.2f}\nPrecio por saco: RD$ {datos['precio_saco']:.2f}\n\nTOTAL A PAGAR: RD$ {datos['total']:.2f}\n\n{AUTOR}\n"""
            st.download_button("⬇ Descargar liquidación TXT", texto_txt, file_name="liquidacion_RAFC.txt", mime="text/plain", use_container_width=True)

        st.markdown("### Vista previa del recibo")
        components.html(crear_recibo_html(datos), height=1000, scrolling=True)

# --------------------------- ACERCA --------------------------
elif st.session_state.pagina == "acerca":
    banner_principal()
    st.markdown("## Acerca de RAFC")
    st.write("RAFC es un sistema para apoyar la liquidación y el cálculo de arroz.")
    st.write("La tara fija configurada es de 0.50 kg por saco.")
    st.write("La fórmula acordada es: peso neto ÷ (100 + humedad).")
    st.markdown(f"**{AUTOR}**")
