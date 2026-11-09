#!/usr/bin/env python3
"""Genera un resumen JSON ligero para las experiencias web a partir de los Excel."""

import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DATOS = ROOT / "datos"
DESTINO = ROOT / "web" / "datos.js"


def registros(df: pd.DataFrame) -> list[dict]:
    return json.loads(df.to_json(orient="records", force_ascii=False))


def main() -> None:
    ventas = pd.read_excel(DATOS / "ventas_sample.xlsx", sheet_name="datos")
    pedidos = pd.read_excel(DATOS / "ca_pedidos_sample.xlsx", sheet_name="datos")
    establecimientos = pd.read_excel(
        DATOS / "dim_establecimiento_sample.xlsx", sheet_name="datos"
    )
    mercado = pd.read_excel(
        DATOS / "sell_out_ventas_Nielsen_sample.xlsx", sheet_name="datos"
    )

    ventas["mes"] = pd.to_datetime(ventas["Week-Month-Year"]).dt.to_period("M").astype(str)
    tendencia_ventas = (
        ventas.groupby("mes", as_index=False)
        .agg(venta=("VentaNeta", "sum"), margen=("Margen", "sum"), litros=("Litros", "sum"))
        .round(2)
    )
    materiales = (
        ventas.groupby("Material", as_index=False)
        .agg(venta=("VentaNeta", "sum"), litros=("Litros", "sum"))
        .nlargest(8, "venta")
        .round(2)
    )
    distribuidores = (
        ventas.groupby("Distribuidor", as_index=False)
        .agg(venta=("VentaNeta", "sum"), margen=("Margen", "sum"))
        .nlargest(6, "venta")
        .round(2)
    )

    activos = establecimientos[
        establecimientos["EstadoDesc"].astype(str).str.contains("ABIERTO", na=False)
    ].copy()
    candidatos = activos[
        activos["Barmanager"].astype(str).str.lower().ne("true")
    ].copy()
    candidatos["potencial"] = (
        candidatos["Capacidadinterior"].fillna(0)
        + candidatos["Mesasterraza"].fillna(0) * 4
    )
    oportunidades = (
        candidatos.nlargest(6, "potencial")[
            [
                "EstablecimientoCRMDesc",
                "Ciudad",
                "TipodeCuentaDesc",
                "CategoriaDesc",
                "Capacidadinterior",
                "Mesasterraza",
                "GestorcomercialZona",
            ]
        ]
        .rename(
            columns={
                "EstablecimientoCRMDesc": "nombre",
                "Ciudad": "ciudad",
                "TipodeCuentaDesc": "tipo",
                "CategoriaDesc": "categoria",
                "Capacidadinterior": "interior",
                "Mesasterraza": "terraza",
                "GestorcomercialZona": "zona",
            }
        )
        .fillna("—")
    )
    tipos = (
        activos["TipodeCuentaDesc"]
        .fillna("Sin clasificar")
        .value_counts()
        .head(6)
        .rename_axis("tipo")
        .reset_index(name="establecimientos")
    )

    mercado["mes"] = pd.to_datetime(mercado["month"]).dt.to_period("M").astype(str)
    damm = mercado[mercado["sociedades"].eq("S.DAMM")].copy()
    marcas = (
        damm.groupby("marca", as_index=False)
        .agg(
            litros=("vtas_ltrs", "sum"),
            valor=("vtas_valor", "sum"),
            precio=("precio_ltrs_promedio", "mean"),
            promo=("intensidad_promocional_porcen", "mean"),
            descuento=("porcen_descuento", "mean"),
        )
        .nlargest(10, "litros")
        .round(2)
    )
    segmentos = (
        mercado.groupby("segmento", as_index=False)
        .agg(litros=("vtas_ltrs", "sum"))
        .sort_values("litros", ascending=False)
        .round(2)
    )
    tendencia_consumidor = (
        damm.groupby("mes", as_index=False)
        .agg(litros=("vtas_ltrs", "sum"), valor=("vtas_valor", "sum"))
        .round(2)
    )
    formatos = (
        damm.groupby("envase", as_index=False)
        .agg(litros=("vtas_ltrs", "sum"))
        .sort_values("litros", ascending=False)
        .round(2)
    )
    destacados = (
        marcas.assign(puntuacion=marcas["promo"] * marcas["litros"])
        .nlargest(4, "puntuacion")
        .drop(columns="puntuacion")
    )

    salida = {
        "meta": {
            "preventaPeriodo": "Ene–Dic 2025",
            "consumidorPeriodo": "Ene–Dic 2024",
            "nota": "Visualización construida con muestras de datos; no representa actividad en tiempo real.",
        },
        "preventa": {
            "kpis": {
                "venta": round(float(ventas["VentaNeta"].sum()), 2),
                "margen": round(float(ventas["Margen"].sum()), 2),
                "litros": round(float(ventas["Litros"].sum()), 2),
                "establecimientos": int(ventas["Establecimiento"].nunique()),
                "pedidos": int(pedidos["NNum_Documento"].nunique()),
                "valorPedidos": round(float(pedidos["ValorNeto"].sum()), 2),
            },
            "tendencia": registros(tendencia_ventas),
            "materiales": registros(materiales),
            "distribuidores": registros(distribuidores),
            "oportunidades": registros(oportunidades),
            "tipos": registros(tipos),
            "coberturaDigital": round(float(establecimientos["Barmanager"].eq(True).mean() * 100), 1),
        },
        "consumidor": {
            "kpis": {
                "litrosDamm": round(float(damm["vtas_ltrs"].sum()), 2),
                "valorDamm": round(float(damm["vtas_valor"].sum()), 2),
                "marcas": int(damm["marca"].nunique()),
                "precioMedio": round(float(damm["precio_ltrs_promedio"].mean()), 2),
            },
            "marcas": registros(marcas),
            "segmentos": registros(segmentos),
            "tendencia": registros(tendencia_consumidor),
            "formatos": registros(formatos),
            "destacados": registros(destacados),
        },
    }

    DESTINO.parent.mkdir(parents=True, exist_ok=True)
    DESTINO.write_text(
        "window.DAMM_DATA = " + json.dumps(salida, ensure_ascii=False, separators=(",", ":")) + ";\n",
        encoding="utf-8",
    )
    print(DESTINO)


if __name__ == "__main__":
    main()
