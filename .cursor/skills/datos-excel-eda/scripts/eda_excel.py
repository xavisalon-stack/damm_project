#!/usr/bin/env python3
"""EDA de un Excel. Lee el original y escribe informe, PNG y CSV en eda/."""

from __future__ import annotations

import argparse
import math
import re
import sys
import unicodedata
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

DOC_SHEET_NAMES = {
    "info",
    "metadata",
    "metadatos",
    "diccionario",
    "readme",
    "leeme",
    "léeme",
}
NULL_USELESS = 0.95
ID_TEXT_RATIO = 0.95
LOW_CARDINALITY = 15
CORR_STRONG = 0.4
CORR_FALLBACK = 0.2
MAX_SCATTERS = 6
SCATTER_SAMPLE = 4000
BOX_SAMPLE = 20_000
BOX_FLIER_CAP = 200
TOP_CATEGORIES = 15
PREVIEW_ROWS = 5
PREVIEW_COL_GROUP = 8
CELL_WIDTH = 40


def repo_root() -> Path:
    cwd = Path.cwd()
    candidates = [cwd, *cwd.parents]
    for candidate in candidates:
        if (candidate / "datos").is_dir():
            return candidate
    return cwd


def slug(value: object, limit: int = 50) -> str:
    text = unicodedata.normalize("NFKD", str(value))
    text = text.encode("ascii", "ignore").decode("ascii")
    text = re.sub(r"[^A-Za-z0-9]+", "_", text).strip("_").lower()
    return (text or "col")[:limit]


def md_cell(value: object, limit: int = CELL_WIDTH) -> str:
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return ""
    try:
        if pd.isna(value):
            return ""
    except TypeError:
        pass
    text = str(value).replace("\r", " ").replace("\n", " ").replace("|", "\\|")
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) > limit:
        return text[: limit - 1] + "…"
    return text


def fmt_num(value: object) -> str:
    if value is None:
        return "—"
    try:
        if pd.isna(value):
            return "—"
    except TypeError:
        pass
    number = float(value)
    if math.isnan(number) or math.isinf(number):
        return "—"
    if abs(number) >= 1e12 or (abs(number) > 0 and abs(number) < 1e-4):
        return f"{number:.4g}"
    rounded = round(number)
    if abs(number - rounded) < 1e-9:
        return f"{int(rounded)}"
    return f"{number:.4g}"


def n_palabras(count: int, singular: str, plural: str) -> str:
    return f"{count} {singular if count == 1 else plural}"


def fmt_pct(share: float) -> str:
    if math.isnan(share):
        return "—"
    return f"{share * 100:.1f} %"


def md_table(headers: list[str], rows: list[list[str]]) -> list[str]:
    head = "| " + " | ".join(headers) + " |"
    rule = "| " + " | ".join("---" for _ in headers) + " |"
    body = ["| " + " | ".join(row) + " |" for row in rows]
    return [head, rule, *body]


def is_doc_sheet(name: str, frame: pd.DataFrame) -> bool:
    if name.strip().lower() in DOC_SHEET_NAMES:
        return True
    return frame.shape[1] <= 2 and frame.shape[0] <= 5


def clean_frame(frame: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    notes = {"columnas_renombradas": [], "celdas_vacias_a_nulo": 0, "nombres_duplicados": []}
    cleaned = frame.copy()
    new_names: list[str] = []
    seen: dict[str, int] = {}
    for column in cleaned.columns:
        original = str(column)
        name = original.strip() or "columna"
        if name != original:
            notes["columnas_renombradas"].append((original, name))
        count = seen.get(name, 0) + 1
        seen[name] = count
        if count > 1:
            unique = f"{name}_{count}"
            notes["nombres_duplicados"].append((name, unique))
            name = unique
        new_names.append(name)
    cleaned.columns = new_names
    for column in cleaned.columns:
        series = cleaned[column]
        if not (
            series.dtype == object or pd.api.types.is_string_dtype(series)
        ):
            continue
        as_text = series.astype("string").str.strip()
        empty = as_text.eq("") | as_text.eq("#")
        notes["celdas_vacias_a_nulo"] += int(empty.fillna(False).sum())
        cleaned[column] = as_text.mask(empty, pd.NA)
    return cleaned, notes


def parse_dates(series: pd.Series) -> pd.Series | None:
    if pd.api.types.is_datetime64_any_dtype(series):
        return series
    if not (series.dtype == object or pd.api.types.is_string_dtype(series)):
        return None
    present = series.dropna()
    if present.empty:
        return None
    sample = present.astype(str).head(40).str.strip()
    iso = sample.str.match(
        r"^\d{4}[-/.]\d{1,2}[-/.]\d{1,2}([ T]\d{1,2}:\d{2}(:\d{2})?)?$"
    ).mean()
    dmy = sample.str.match(r"^\d{1,2}[-/.]\d{1,2}[-/.]\d{4}$").mean()
    if max(iso, dmy) < 0.8:
        return None
    parsed = pd.to_datetime(series, errors="coerce", dayfirst=bool(dmy >= iso))
    if parsed.notna().sum() < 0.8 * len(present):
        return None
    return parsed


def is_identifier(series: pd.Series) -> bool:
    present = series.dropna()
    if len(present) < 20:
        return False
    ratio = present.nunique(dropna=True) / len(present)
    if pd.api.types.is_integer_dtype(series):
        return present.nunique(dropna=True) == len(present)
    if pd.api.types.is_bool_dtype(series) or pd.api.types.is_numeric_dtype(series):
        return False
    return ratio >= ID_TEXT_RATIO


def column_roles(
    frame: pd.DataFrame,
) -> tuple[list[str], list[str], list[str], dict[str, pd.Series]]:
    numeric: list[str] = []
    categorical: list[str] = []
    dates: list[str] = []
    parsed_dates: dict[str, pd.Series] = {}
    for column in frame.columns:
        series = frame[column]
        if pd.api.types.is_bool_dtype(series):
            categorical.append(column)
            continue
        if pd.api.types.is_numeric_dtype(series):
            numeric.append(column)
            continue
        parsed = parse_dates(series)
        if parsed is not None:
            dates.append(column)
            parsed_dates[column] = parsed
            continue
        categorical.append(column)
    return numeric, categorical, dates, parsed_dates


def duplicate_columns(frame: pd.DataFrame) -> list[tuple[str, str]]:
    fingerprints: dict[int, list[str]] = {}
    pairs: list[tuple[str, str]] = []
    for column in frame.columns:
        digest = int(pd.util.hash_pandas_object(frame[column], index=False).sum())
        fingerprints.setdefault(digest, []).append(column)
    for columns in fingerprints.values():
        for index, left in enumerate(columns):
            for right in columns[index + 1 :]:
                if frame[left].equals(frame[right]):
                    pairs.append((left, right))
    return pairs


def useless_columns(
    frame: pd.DataFrame,
    identifiers: list[str],
    copies: list[tuple[str, str]],
    dates: list[str],
) -> list[tuple[str, str]]:
    proposals: list[tuple[str, str]] = []
    rows = max(len(frame), 1)
    seen: set[str] = set()
    for column in frame.columns:
        null_share = float(frame[column].isna().mean()) if rows else 1.0
        distinct = int(frame[column].nunique(dropna=True))
        if null_share >= NULL_USELESS:
            proposals.append((column, f"{fmt_pct(null_share)} de nulos"))
            seen.add(column)
        elif distinct <= 1 and null_share >= 0.5:
            proposals.append(
                (
                    column,
                    f"un solo valor informado y {fmt_pct(null_share)} de nulos",
                )
            )
            seen.add(column)
        elif distinct <= 1:
            if column in dates:
                reason = "un solo valor; fecha que fija el periodo, valorar conservarla"
            else:
                reason = "un solo valor distinto"
            proposals.append((column, reason))
            seen.add(column)
    for column in identifiers:
        if column in seen:
            continue
        proposals.append((column, "posible identificador (casi un valor por fila)"))
        seen.add(column)
    for _left, right in copies:
        if right in seen:
            continue
        proposals.append((right, f"copia exacta de {_left}"))
        seen.add(right)
    return proposals


def iqr_report(series: pd.Series) -> dict | None:
    values = pd.to_numeric(series, errors="coerce").replace([np.inf, -np.inf], np.nan).dropna()
    if values.empty:
        return None
    q1, q3 = np.percentile(values.to_numpy(dtype=float), [25, 75])
    iqr = float(q3 - q1)
    if iqr == 0:
        return {
            "n": int(values.shape[0]),
            "q1": float(q1),
            "q3": float(q3),
            "iqr": 0.0,
            "lower": None,
            "upper": None,
            "n_out": 0,
            "applicable": False,
        }
    lower = float(q1 - 1.5 * iqr)
    upper = float(q3 + 1.5 * iqr)
    mask = (values < lower) | (values > upper)
    return {
        "n": int(values.shape[0]),
        "q1": float(q1),
        "q3": float(q3),
        "iqr": iqr,
        "lower": lower,
        "upper": upper,
        "n_out": int(mask.sum()),
        "applicable": True,
    }


def save_fig(fig: plt.Figure, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=120, bbox_inches="tight")
    plt.close(fig)


def plot_bars(counts: pd.Series, title: str, path: Path, total_classes: int) -> None:
    fig_h = max(3.2, 0.38 * len(counts) + 1.2)
    fig, ax = plt.subplots(figsize=(8, fig_h))
    positions = np.arange(len(counts))
    ax.barh(positions, counts.to_numpy(), color="#1f4e79")
    ax.set_yticks(positions)
    ax.set_yticklabels([md_cell(label, 32) for label in counts.index.astype(str)])
    ax.invert_yaxis()
    ax.set_xlabel("Frecuencia")
    shown = len(counts)
    if total_classes > shown:
        title = f"{title} ({shown} clases más frecuentes de {total_classes})"
    ax.set_title(title)
    save_fig(fig, path)


def plot_hist(values: pd.Series, title: str, path: Path) -> None:
    array = values.to_numpy(dtype=float)
    distinct = int(pd.Series(array).nunique())
    bins = 30 if distinct > 30 else max(distinct, 1)
    fig, ax = plt.subplots(figsize=(7.5, 4.2))
    ax.hist(array, bins=bins, color="#1f4e79", edgecolor="white")
    ax.set_xlabel(title)
    ax.set_ylabel("Frecuencia")
    ax.set_title(f"Distribución de {title}")
    save_fig(fig, path)


def plot_box(values: pd.Series, title: str, path: Path, report: dict) -> str:
    array = values.to_numpy(dtype=float)
    note = ""
    drawn = array
    if array.size > BOX_SAMPLE:
        rng = np.random.default_rng(42)
        drawn = rng.choice(array, size=BOX_SAMPLE, replace=False)
        note = f" Gráfico con una muestra de {BOX_SAMPLE} filas; el recuento IQR usa todas."
    show_fliers = bool(report["applicable"] and report["n_out"] <= BOX_FLIER_CAP)
    if report["applicable"] and report["n_out"] > BOX_FLIER_CAP:
        note += " Puntos atípicos omitidos en el gráfico por volumen; el recuento está en la tabla."
    fig, ax = plt.subplots(figsize=(7.5, 3.6))
    ax.boxplot(
        drawn, orientation="horizontal", showfliers=show_fliers, widths=0.55
    )
    ax.set_yticks([])
    ax.set_xlabel(title)
    if report["applicable"]:
        ax.set_title(
            f"{title}: {report['n_out']} atípicos "
            f"({fmt_pct(report['n_out'] / report['n'])}) por IQR"
        )
        ax.axvline(report["lower"], color="#b45309", ls="--", lw=1)
        ax.axvline(report["upper"], color="#b45309", ls="--", lw=1)
    else:
        ax.set_title(f"{title}: IQR nulo, criterio no aplicable")
    save_fig(fig, path)
    return note.strip()


def plot_correlation(frame: pd.DataFrame, columns: list[str], path: Path) -> pd.DataFrame:
    corr = frame[columns].corr(method="pearson", numeric_only=True)
    size = max(6, min(18, 0.45 * len(columns) + 3))
    fig, ax = plt.subplots(figsize=(size, size * 0.85))
    annotate = len(columns) <= 12
    sns.heatmap(
        corr,
        ax=ax,
        cmap="RdBu_r",
        center=0,
        vmin=-1,
        vmax=1,
        annot=annotate,
        fmt=".2f",
        square=True,
        cbar_kws={"label": "Pearson"},
    )
    ax.set_title("Matriz de correlación (Pearson)")
    save_fig(fig, path)
    return corr


def plot_scatter(
    frame: pd.DataFrame, left: str, right: str, coef: float, path: Path
) -> None:
    pair = frame[[left, right]].dropna()
    if len(pair) > SCATTER_SAMPLE:
        pair = pair.sample(SCATTER_SAMPLE, random_state=42)
    fig, ax = plt.subplots(figsize=(6.5, 5.2))
    ax.scatter(pair[left], pair[right], s=12, alpha=0.45, color="#1f4e79", linewidths=0)
    ax.set_xlabel(left)
    ax.set_ylabel(right)
    ax.set_title(f"{left} y {right} (r = {coef:.2f})")
    save_fig(fig, path)


def preview_tables(frame: pd.DataFrame, cell_limit: int = CELL_WIDTH) -> list[str]:
    preview = frame.head(PREVIEW_ROWS)
    if preview.empty:
        return ["Sin filas que mostrar.", ""]
    lines: list[str] = []
    columns = list(preview.columns)
    groups = [
        columns[start : start + PREVIEW_COL_GROUP]
        for start in range(0, len(columns), PREVIEW_COL_GROUP)
    ]
    for group_index, group in enumerate(groups, start=1):
        if len(groups) > 1:
            lines.append(
                f"Columnas {group_index} de {len(groups)} "
                f"({group[0]} … {group[-1]})."
            )
            lines.append("")
        headers = ["#", *[md_cell(column, 80) for column in group]]
        rows = []
        for offset, (_, row) in enumerate(preview.iterrows(), start=1):
            rows.append(
                [str(offset), *[md_cell(row[column], cell_limit) for column in group]]
            )
        lines.extend(md_table(headers, rows))
        lines.append("")
    return lines


def numeric_stats_row(series: pd.Series) -> list[str]:
    values = pd.to_numeric(series, errors="coerce")
    present = int(values.notna().sum())
    if present == 0:
        return [fmt_num(0), "—", "—", "—", "—", "—", "—", "—"]
    described = values.describe()
    return [
        fmt_num(present),
        fmt_num(described.get("mean")),
        fmt_num(described.get("std")),
        fmt_num(described.get("min")),
        fmt_num(described.get("25%")),
        fmt_num(described.get("50%")),
        fmt_num(described.get("75%")),
        fmt_num(described.get("max")),
    ]


def strongest_pairs(corr: pd.DataFrame) -> list[tuple[str, str, float]]:
    pairs: list[tuple[str, str, float]] = []
    columns = list(corr.columns)
    for i, left in enumerate(columns):
        for right in columns[i + 1 :]:
            coef = corr.loc[left, right]
            if coef is None or (isinstance(coef, float) and math.isnan(coef)):
                continue
            pairs.append((left, right, float(coef)))
    pairs.sort(key=lambda item: abs(item[2]), reverse=True)
    strong = [item for item in pairs if abs(item[2]) >= CORR_STRONG][:MAX_SCATTERS]
    if strong:
        return strong
    if pairs and abs(pairs[0][2]) >= CORR_FALLBACK:
        return pairs[:1]
    return []


def clear_previous_outputs(out_dir: Path) -> None:
    if not out_dir.exists():
        return
    graphs = out_dir / "graficos"
    if graphs.exists():
        for png in graphs.glob("*.png"):
            png.unlink()
    for csv_path in out_dir.glob("datos_limpios*.csv"):
        csv_path.unlink()
    report = out_dir / "informe_eda.md"
    if report.exists():
        report.unlink()


def image_link(out_dir: Path, path: Path, alt: str) -> str:
    relative = path.relative_to(out_dir).as_posix()
    alt_text = md_cell(alt, 80).replace("(", "").replace(")", "")
    return f"![{alt_text}]({relative})"


def unique_png(directory: Path, stem: str, used: set[str]) -> Path:
    candidate = stem
    index = 2
    while candidate in used:
        candidate = f"{stem}_{index}"
        index += 1
    used.add(candidate)
    return directory / f"{candidate}.png"


def analyze_sheet(
    sheet: str,
    frame: pd.DataFrame,
    out_dir: Path,
    sheet_slug: str,
    multi_sheet: bool,
    extra_cleaning: list[str] | None = None,
) -> tuple[list[str], list[str]]:
    lines: list[str] = []
    findings: list[str] = []
    used_names: set[str] = set()
    numeric, categorical, dates, parsed_dates = column_roles(frame)
    identifiers = [
        column
        for column in [*numeric, *categorical]
        if is_identifier(frame[column])
    ]
    copies = duplicate_columns(frame)
    proposals = useless_columns(frame, identifiers, copies, dates)
    measure_numeric = [column for column in numeric if column not in identifiers]

    lines.append(f"### Hoja `{sheet}`")
    lines.append("")
    lines.append(
        f"- Filas: {len(frame)}. Columnas: {frame.shape[1]}. "
        f"Numéricas: {len(numeric)}. Categóricas: {len(categorical)}. "
        f"Fechas: {len(dates)}."
    )
    lines.append("")
    lines.append("Primeras filas:")
    lines.append("")
    lines.extend(preview_tables(frame))

    lines.append("#### Tipos de variables")
    lines.append("")
    if numeric:
        lines.append("Numéricas:")
        lines.append("")
        rows = []
        for column in numeric:
            distinct = int(frame[column].nunique(dropna=True))
            note = ""
            if column in identifiers:
                note = "posible identificador"
            elif distinct <= LOW_CARDINALITY:
                note = (
                    "baja cardinalidad ("
                    f"{n_palabras(distinct, 'valor', 'valores')})"
                )
            rows.append([md_cell(column, 40), *numeric_stats_row(frame[column]), note])
        lines.extend(
            md_table(
                [
                    "Variable",
                    "No nulos",
                    "Media",
                    "Desv. típica",
                    "Mín.",
                    "P25",
                    "Mediana",
                    "P75",
                    "Máx.",
                    "Nota",
                ],
                rows,
            )
        )
        lines.append("")
    else:
        lines.append("No hay variables numéricas.")
        lines.append("")

    if categorical:
        lines.append("Categóricas:")
        lines.append("")
        rows = []
        for column in categorical:
            present = frame[column].dropna()
            classes = int(present.nunique())
            if present.empty:
                top, top_n = "—", "0"
            else:
                mode = present.astype(str).value_counts().iloc[0]
                top = md_cell(present.astype(str).value_counts().index[0], 32)
                top_n = str(int(mode))
            note = "posible identificador" if column in identifiers else ""
            rows.append(
                [
                    md_cell(column, 40),
                    fmt_num(len(present)),
                    fmt_num(classes),
                    top,
                    top_n,
                    fmt_pct(float(frame[column].isna().mean())),
                    note,
                ]
            )
        lines.extend(
            md_table(
                [
                    "Variable",
                    "No nulos",
                    "Clases",
                    "Clase más frecuente",
                    "Frecuencia",
                    "Nulos",
                    "Nota",
                ],
                rows,
            )
        )
        lines.append("")
    else:
        lines.append("No hay variables categóricas.")
        lines.append("")

    if dates:
        lines.append("Fechas:")
        lines.append("")
        rows = []
        for column in dates:
            parsed = parsed_dates[column]
            rows.append(
                [
                    md_cell(column, 40),
                    fmt_num(int(parsed.notna().sum())),
                    str(parsed.min().date()) if parsed.notna().any() else "—",
                    str(parsed.max().date()) if parsed.notna().any() else "—",
                    fmt_num(int(parsed.nunique(dropna=True))),
                ]
            )
        lines.extend(
            md_table(["Variable", "No nulos", "Mínimo", "Máximo", "Valores distintos"], rows)
        )
        lines.append("")

    dup_rows = int(frame.duplicated().sum())
    lines.append("#### Limpieza")
    lines.append("")
    for note in extra_cleaning or []:
        lines.append(f"- {note}")
    lines.append(
        f"- Filas duplicadas exactas que permanecen: {dup_rows} de {len(frame)} "
        f"({fmt_pct(dup_rows / len(frame) if len(frame) else 0)})."
    )
    nulls = frame.isna().sum()
    null_rows = []
    for column in frame.columns:
        count = int(nulls[column])
        if count == 0:
            continue
        null_rows.append(
            [md_cell(column, 40), str(count), fmt_pct(count / len(frame) if len(frame) else 0)]
        )
    if null_rows:
        lines.append("- Columnas con nulos:")
        lines.append("")
        lines.extend(md_table(["Variable", "Nulos", "%"], null_rows))
        lines.append("")
    else:
        lines.append("- Ninguna columna tiene nulos.")
        lines.append("")
    if proposals:
        lines.append(
            "Columnas poco útiles. Propuesta, no eliminadas de esta ejecución "
            "salvo que figuren más abajo como confirmadas:"
        )
        lines.append("")
        lines.extend(
            md_table(
                ["Variable", "Motivo"],
                [[md_cell(name, 40), reason] for name, reason in proposals],
            )
        )
        lines.append("")
    else:
        lines.append("No se proponen columnas a eliminar.")
        lines.append("")

    csv_name = (
        f"datos_limpios_{sheet_slug}.csv" if multi_sheet else "datos_limpios.csv"
    )
    csv_path = out_dir / csv_name
    frame.to_csv(csv_path, index=False)
    lines.append(f"- Datos de esta hoja: [{csv_name}]({csv_name}).")
    lines.append("")

    findings.append(
        f"Hoja `{sheet}`: {n_palabras(len(frame), 'fila', 'filas')}, "
        f"{n_palabras(frame.shape[1], 'columna', 'columnas')}, "
        f"{n_palabras(dup_rows, 'fila duplicada', 'filas duplicadas')}, "
        f"{n_palabras(len(proposals), 'columna poco útil', 'columnas poco útiles')}."
    )

    graph_dir = out_dir / "graficos"
    lines.append("#### Valores atípicos (rango intercuartílico)")
    lines.append("")
    lines.append(
        "Un valor es atípico si está por debajo de Q1 − 1,5·IQR o por encima de "
        "Q3 + 1,5·IQR. Las líneas discontinuas del boxplot marcan esas vallas."
    )
    lines.append("")
    outlier_rows = []
    if not measure_numeric:
        lines.append("No hay variables numéricas de medida a las que aplicar el criterio.")
        lines.append("")
    for column in measure_numeric:
        report = iqr_report(frame[column])
        if report is None:
            continue
        path = unique_png(graph_dir, f"{sheet_slug}_box_{slug(column)}", used_names)
        values = pd.to_numeric(frame[column], errors="coerce").dropna()
        note = plot_box(values, column, path, report)
        if not report["applicable"]:
            outlier_rows.append(
                [
                    md_cell(column, 32),
                    fmt_num(report["q1"]),
                    fmt_num(report["q3"]),
                    "0",
                    "—",
                    "—",
                    "criterio no aplicable (IQR nulo)",
                ]
            )
            findings.append(f"`{column}` tiene IQR nulo; no se marcan atípicos.")
        else:
            share = report["n_out"] / report["n"] if report["n"] else 0
            outlier_rows.append(
                [
                    md_cell(column, 32),
                    fmt_num(report["q1"]),
                    fmt_num(report["q3"]),
                    fmt_num(report["iqr"]),
                    f"{fmt_num(report['lower'])} … {fmt_num(report['upper'])}",
                    f"{report['n_out']} ({fmt_pct(share)})",
                    image_link(out_dir, path, f"Boxplot de {column}"),
                ]
            )
            if share >= 0.05:
                findings.append(
                    f"`{column}` tiene {n_palabras(report['n_out'], 'atípico', 'atípicos')} "
                    f"({fmt_pct(share)})."
                )
        if note:
            lines.append(f"Nota de `{column}`: {note}")
            lines.append("")
    if outlier_rows:
        lines.extend(
            md_table(
                ["Variable", "Q1", "Q3", "IQR", "Vallas", "Atípicos", "Boxplot"],
                outlier_rows,
            )
        )
        lines.append("")

    lines.append("#### Gráficos")
    lines.append("")
    lines.append("Distribución de categóricas:")
    lines.append("")
    plotted_cat = False
    for column in categorical:
        present = frame[column].dropna()
        classes = int(present.nunique())
        if classes <= 1:
            lines.append(
                f"- `{column}`: {n_palabras(classes, 'clase', 'clases')}. "
                "Sin gráfico de distribución."
            )
            lines.append("")
            continue
        if column in identifiers or classes == len(present):
            lines.append(
                f"- `{column}`: {n_palabras(classes, 'clase', 'clases')}, "
                "una por fila no nula. Sin gráfico de distribución."
            )
            lines.append("")
            continue
        counts = present.astype(str).value_counts().head(TOP_CATEGORIES)
        path = unique_png(graph_dir, f"{sheet_slug}_bar_{slug(column)}", used_names)
        plot_bars(counts, column, path, classes)
        lines.append(image_link(out_dir, path, f"Distribución de {column}"))
        lines.append("")
        plotted_cat = True
    if not plotted_cat:
        lines.append("No hay distribuciones categóricas que graficar.")
        lines.append("")

    lines.append("Distribución de numéricas:")
    lines.append("")
    plotted_num = False
    for column in measure_numeric:
        values = pd.to_numeric(frame[column], errors="coerce").replace(
            [np.inf, -np.inf], np.nan
        ).dropna()
        if values.nunique() <= 1:
            lines.append(f"- `{column}`: sin variación. Sin gráfico de distribución.")
            lines.append("")
            continue
        distinct = int(values.nunique())
        path = unique_png(graph_dir, f"{sheet_slug}_dist_{slug(column)}", used_names)
        if distinct <= LOW_CARDINALITY:
            counts = values.value_counts().sort_values(ascending=False).head(TOP_CATEGORIES)
            plot_bars(counts, column, path, distinct)
        else:
            plot_hist(values, column, path)
        lines.append(image_link(out_dir, path, f"Distribución de {column}"))
        lines.append("")
        plotted_num = True
    if not plotted_num:
        lines.append("No hay distribuciones numéricas que graficar.")
        lines.append("")

    lines.append("Matriz de correlación y relaciones más fuertes:")
    lines.append("")
    usable = []
    for column in measure_numeric:
        values = pd.to_numeric(frame[column], errors="coerce")
        if values.nunique(dropna=True) > 1:
            usable.append(column)
    if len(usable) < 2:
        lines.append(
            "No hay al menos dos variables numéricas con variación para correlacionar."
        )
        lines.append("")
        findings.append(f"Hoja `{sheet}`: sin pares numéricos para correlacionar.")
    else:
        numeric_frame = frame[usable].apply(pd.to_numeric, errors="coerce")
        path = unique_png(graph_dir, f"{sheet_slug}_correlacion", used_names)
        corr = plot_correlation(numeric_frame, usable, path)
        lines.append(image_link(out_dir, path, f"Matriz de correlación de {sheet}"))
        lines.append("")
        pairs = strongest_pairs(corr)
        if not pairs:
            lines.append(
                "Ningún par alcanza |r| ≥ 0,2. No se generan scatterplots."
            )
            lines.append("")
            findings.append(f"Hoja `{sheet}`: correlaciones lineales débiles (|r| < 0,2).")
        else:
            for left, right, coef in pairs:
                scatter_path = unique_png(
                    graph_dir,
                    f"{sheet_slug}_scatter_{slug(left)}_vs_{slug(right)}",
                    used_names,
                )
                plot_scatter(numeric_frame, left, right, coef, scatter_path)
                lines.append(
                    f"`{left}` y `{right}`: r = {coef:.2f}."
                )
                lines.append("")
                lines.append(
                    image_link(out_dir, scatter_path, f"{left} frente a {right}")
                )
                lines.append("")
                if abs(coef) >= CORR_STRONG:
                    findings.append(
                        f"`{left}` y `{right}` se mueven juntas (r = {coef:.2f})."
                    )

    return lines, findings


def doc_sheet_lines(sheet: str, frame: pd.DataFrame) -> list[str]:
    lines = [
        f"### Hoja `{sheet}`",
        "",
        "Hoja de documentación: entra en la vista general y no en el resto del EDA.",
        "",
        f"- Filas: {len(frame)}. Columnas: {frame.shape[1]}.",
        "",
    ]
    if frame.empty:
        lines.append("La hoja no tiene filas.")
        lines.append("")
        return lines
    shown = frame.head(80)
    lines.append("Contenido (hasta 80 filas):")
    lines.append("")
    lines.extend(preview_tables(shown, cell_limit=400))
    if len(frame) > 80:
        lines.append(f"Quedan {len(frame) - 80} filas sin volcar en el informe.")
        lines.append("")
    return lines


def draft_conclusions(
    findings: list[str],
    proposals: list[str],
    excluded: list[str],
    dropped_duplicates: bool,
) -> list[str]:
    lines = [
        "## 6. Conclusiones",
        "",
        "> Borrador automático del script. Reescribir esta sección en español "
        "después de revisar los gráficos y borrar esta cita.",
        "",
        "### Hallazgos principales",
        "",
    ]
    if findings:
        lines.extend(f"- {item}" for item in findings)
    else:
        lines.append("- El fichero no aporta hallazgos numéricos adicionales.")
    lines.extend(["", "### Problemas de calidad de los datos", ""])
    if proposals:
        lines.append(
            "- Hay columnas poco útiles (nulos, constantes, identificadores o copias). "
            "Siguen en el CSV porque no se han confirmado eliminaciones."
        )
        lines.extend(f"- {item}" for item in proposals[:12])
    else:
        lines.append("- El script no marca columnas poco útiles.")
    if dropped_duplicates:
        lines.append("- Las filas duplicadas se eliminaron del CSV con confirmación del usuario.")
    lines.extend(["", "### Recomendaciones", ""])
    if excluded:
        lines.append(
            "- Esta ejecución ya excluye, con confirmación, las columnas: "
            + ", ".join(f"`{name}`" for name in excluded)
            + "."
        )
    elif proposals:
        lines.append(
            "- Confirmar si se eliminan las columnas propuestas antes de un segundo EDA. "
            "Hasta entonces no se quitan."
        )
    lines.append(
        "- Tratar los códigos de baja cardinalidad como categorías si el negocio los usa así."
    )
    lines.append(
        "- Revisar los atípicos del criterio IQR antes de agregarlos o de winsorizar."
    )
    lines.append("")
    return lines


def build_report(
    excel: Path,
    root: Path,
    exclude: list[str],
    drop_duplicates: bool,
    force_sheets: set[str],
) -> Path:
    if not excel.is_file():
        raise SystemExit(f"No existe el fichero: {excel}")
    datos = (root / "datos").resolve()
    out_dir = (root / "eda" / f"{excel.stem}_eda").resolve()
    try:
        out_dir.relative_to(datos)
        inside_datos = True
    except ValueError:
        inside_datos = False
    if inside_datos:
        raise SystemExit("La salida no puede quedar dentro de datos/.")
    source = excel
    try:
        source_label = excel.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        source_label = str(excel)

    sns.set_theme(style="whitegrid", context="notebook")
    plt.rcParams["axes.unicode_minus"] = False

    workbook = pd.ExcelFile(source, engine="openpyxl")
    raw_sheets = []
    for sheet in workbook.sheet_names:
        frame = pd.read_excel(workbook, sheet_name=sheet)
        raw_sheets.append((sheet, frame))
    analyzed = [
        (sheet, frame)
        for sheet, frame in raw_sheets
        if sheet in force_sheets or not is_doc_sheet(sheet, frame)
    ]
    multi = len(analyzed) > 1

    clear_previous_outputs(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    now = datetime.now(ZoneInfo("Europe/Madrid")).strftime("%Y-%m-%d %H:%M")
    lines = [
        f"# Informe EDA: {excel.name}",
        "",
        f"Fuente (solo lectura): `{source_label}`. Generado: {now} (Europe/Madrid).",
        "",
        "El Excel original no se ha modificado. El CSV es una copia con nombres y textos recortados, textos vacíos a nulo y el marcador `#` a nulo.",
        "",
        "## 1. Vista general",
        "",
        f"Hojas ({len(raw_sheets)}): "
        + ", ".join(f"`{sheet}` ({frame.shape[0]}×{frame.shape[1]})" for sheet, frame in raw_sheets)
        + ".",
        "",
    ]
    all_findings: list[str] = []
    all_proposals: list[str] = []
    for sheet, frame in raw_sheets:
        if sheet in force_sheets or not is_doc_sheet(sheet, frame):
            continue
        lines.extend(doc_sheet_lines(sheet, frame))

    per_sheet_blocks: list[list[str]] = []
    used_sheet_slugs: set[str] = set()
    for sheet, frame in analyzed:
        cleaned, notes = clean_frame(frame)
        missing = [name for name in exclude if name not in cleaned.columns]
        if missing:
            available = ", ".join(map(str, cleaned.columns))
            raise SystemExit(
                "Columnas a excluir que no existen: "
                + ", ".join(missing)
                + f". Columnas disponibles: {available}"
            )
        if exclude:
            cleaned = cleaned.drop(columns=exclude)
        removed = 0
        if drop_duplicates:
            before = len(cleaned)
            cleaned = cleaned.drop_duplicates()
            removed = before - len(cleaned)
        extra: list[str] = []
        if notes["celdas_vacias_a_nulo"]:
            extra.append(
                "Textos vacíos o marcador `#` convertidos a nulo: "
                f"{notes['celdas_vacias_a_nulo']}."
            )
        if notes["columnas_renombradas"] or notes["nombres_duplicados"]:
            extra.append("Nombres de columna recortados o desambiguados en la copia.")
        if drop_duplicates:
            extra.append(
                f"Filas duplicadas eliminadas del CSV con confirmación: {removed}."
            )
        if exclude:
            extra.append(
                "Columnas excluidas del CSV con confirmación: "
                + ", ".join(f"`{name}`" for name in exclude)
                + "."
            )
        base_slug = slug(sheet)
        sheet_slug = base_slug
        suffix = 2
        while sheet_slug in used_sheet_slugs:
            sheet_slug = f"{base_slug}_{suffix}"
            suffix += 1
        used_sheet_slugs.add(sheet_slug)
        sheet_lines, findings = analyze_sheet(
            sheet,
            cleaned,
            out_dir,
            sheet_slug,
            multi,
            extra,
        )
        per_sheet_blocks.append(sheet_lines)
        all_findings.extend(findings)
        numeric, categorical, dates, _parsed = column_roles(cleaned)
        identifiers = [
            column
            for column in [*numeric, *categorical]
            if is_identifier(cleaned[column])
        ]
        for name, reason in useless_columns(
            cleaned, identifiers, duplicate_columns(cleaned), dates
        ):
            all_proposals.append(f"`{sheet}` / `{name}`: {reason}.")

    section_map = [
        "#### Tipos de variables",
        "#### Limpieza",
        "#### Valores atípicos (rango intercuartílico)",
        "#### Gráficos",
    ]
    buckets: dict[str, list[str]] = {key: [] for key in section_map}
    for block in per_sheet_blocks:
        indexes = [block.index(marker) for marker in section_map]
        lines.extend(block[: indexes[0]])
        heading = block[0]
        for position, marker in enumerate(section_map):
            start = indexes[position] + 1
            end = indexes[position + 1] if position + 1 < len(section_map) else len(block)
            buckets[marker].extend([heading, "", *block[start:end]])

    lines = rebuild_sections(lines, buckets)
    lines.extend(
        draft_conclusions(all_findings, all_proposals, exclude, drop_duplicates)
    )
    report_path = out_dir / "informe_eda.md"
    report_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    print(report_path.as_posix())
    return report_path


def rebuild_sections(lines: list[str], buckets: dict[str, list[str]]) -> list[str]:
    """Añade las secciones 2 a 5, en ese orden, detrás de la vista general."""
    trimmed = list(lines)
    titles = {
        "#### Tipos de variables": "## 2. Tipos de variables",
        "#### Limpieza": "## 3. Limpieza",
        "#### Valores atípicos (rango intercuartílico)": "## 4. Valores atípicos",
        "#### Gráficos": "## 5. Gráficos",
    }
    intros = {
        "#### Tipos de variables": (
            "Las columnas numéricas incluyen códigos si el Excel los guardó como número. "
            "La nota de baja cardinalidad señala las que tienen 15 valores distintos o menos."
        ),
        "#### Limpieza": (
            "No se elimina ninguna columna sin confirmación del usuario. "
            "La copia CSV conserva todas las columnas salvo las pasadas "
            "con `--excluir-columnas`."
        ),
        "#### Valores atípicos (rango intercuartílico)": (
            "Criterio del rango intercuartílico sobre cada variable numérica de medida."
        ),
        "#### Gráficos": (
            "Rutas relativas a este informe, para que los PNG se vean en GitHub."
        ),
    }
    for key, title in titles.items():
        trimmed.append(title)
        trimmed.append("")
        trimmed.append(intros[key])
        trimmed.append("")
        body = buckets.get(key, [])
        if not body:
            trimmed.append("Sin hojas de datos que analizar.")
            trimmed.append("")
        else:
            trimmed.extend(body)
    return trimmed


def comprobar_informe(path: Path) -> None:
    if not path.is_file():
        raise SystemExit(f"No existe el informe: {path}")
    text = path.read_text(encoding="utf-8")
    if "Borrador automático del script" in text:
        raise SystemExit(
            "La sección 6 sigue en borrador. Reescríbela antes de dar el EDA por cerrado."
        )
    missing = []
    absolute = []
    for match in re.findall(r"!\[[^\]]*\]\(([^)]+)\)", text):
        if match.startswith("http://") or match.startswith("https://"):
            continue
        if match.startswith("/") or re.match(r"^[A-Za-z]:[\\/]", match):
            absolute.append(match)
            continue
        if not (path.parent / match).is_file():
            missing.append(match)
    if absolute or missing:
        details = []
        if absolute:
            details.append("rutas no relativas: " + ", ".join(absolute))
        if missing:
            details.append("PNG ausentes: " + ", ".join(missing))
        raise SystemExit("Informe incompleto. " + "; ".join(details))
    print("ok")


def parse_list(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


def main() -> None:
    parser = argparse.ArgumentParser(description="EDA de un fichero Excel.")
    parser.add_argument("excel", nargs="?", type=Path, help="Ruta del .xlsx")
    parser.add_argument(
        "--excluir-columnas",
        default="",
        help="Columnas a quitar del CSV y del análisis, separadas por coma.",
    )
    parser.add_argument(
        "--eliminar-duplicados",
        action="store_true",
        help="Quita filas duplicadas exactas del CSV. Solo con confirmación.",
    )
    parser.add_argument(
        "--incluir-hojas",
        default="",
        help="Hojas de documentación que también deben analizarse.",
    )
    parser.add_argument(
        "--comprobar-informe",
        type=Path,
        help="Comprueba rutas relativas de PNG y que la sección 6 ya no es un borrador.",
    )
    args = parser.parse_args()
    if args.comprobar_informe:
        comprobar_informe(args.comprobar_informe)
        return
    if args.excel is None:
        raise SystemExit("Indica el Excel, por ejemplo datos/ventas_sample.xlsx")
    root = repo_root()
    build_report(
        args.excel if args.excel.is_absolute() else (root / args.excel),
        root,
        parse_list(args.excluir_columnas),
        args.eliminar_duplicados,
        set(parse_list(args.incluir_hojas)),
    )


if __name__ == "__main__":
    main()
