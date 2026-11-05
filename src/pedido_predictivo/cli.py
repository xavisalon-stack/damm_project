"""Interfaz de línea de comandos reproducible."""

from __future__ import annotations

import argparse
import json

import pandas as pd

from .commercial import proposal_message
from .data import ESTABLISHMENT_COLUMN
from .pipeline import run_training


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Previsión semanal de CantidadUMB")
    subparsers = parser.add_subparsers(dest="command", required=True)

    train = subparsers.add_parser("entrenar", help="Entrena, evalúa y genera propuestas")
    train.add_argument("--datos", default="datos/ventas_sample.xlsx")
    train.add_argument("--salida", default="salidas/modelo_cantidadumb")

    query = subparsers.add_parser("consultar", help="Consulta un establecimiento")
    query.add_argument(
        "--previsiones",
        default="salidas/modelo_cantidadumb/previsiones_pedidos.csv",
    )
    query.add_argument("--establecimiento", required=True)
    query.add_argument("--exportar", help="CSV opcional con el establecimiento consultado")
    query.add_argument("--mensaje", action="store_true")
    return parser


def main() -> None:
    args = _parser().parse_args()
    if args.command == "entrenar":
        print(json.dumps(run_training(args.datos, args.salida), ensure_ascii=False, indent=2))
        return

    predictions = pd.read_csv(args.previsiones)
    selected = predictions.loc[
        predictions[ESTABLISHMENT_COLUMN].astype(str).eq(str(args.establecimiento))
    ]
    if selected.empty:
        raise SystemExit(f"No hay propuesta para {args.establecimiento}")
    if args.exportar:
        selected.to_csv(args.exportar, index=False)
    if args.mensaje:
        print(proposal_message(predictions, args.establecimiento))
    else:
        print(selected.to_csv(index=False))


if __name__ == "__main__":
    main()
