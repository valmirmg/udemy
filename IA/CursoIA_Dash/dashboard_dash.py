from pathlib import Path

import dash
from dash import Input, Output, dcc, html
import pandas as pd
import plotly.express as px

from analise_pandas import gerar_csv


BASE_DIR = Path(__file__).resolve().parent
CSV_PATH = BASE_DIR / "dados_vendas_ficticios.csv"


def carregar_dados() -> pd.DataFrame:
    if not CSV_PATH.exists():
        gerar_csv(CSV_PATH)

    df = pd.read_csv(CSV_PATH, parse_dates=["data"])
    df["faturamento"] = df["quantidade"] * df["preco_unitario"]
    df["custo_total"] = df["quantidade"] * df["custo_unitario"]
    df["lucro"] = df["faturamento"] - df["custo_total"]
    df["margem_percentual"] = (df["lucro"] / df["faturamento"]) * 100
    df["mes"] = df["data"].dt.to_period("M").astype(str)
    return df


df_base = carregar_dados()

app = dash.Dash(__name__)
app.title = "Dashboard de Vendas"

app.layout = html.Div(
    [
        html.H1("Dashboard de Vendas - Dados Ficticios"),
        html.P("Use os filtros para explorar faturamento, lucro e margem."),
        html.Div(
            [
                html.Div(
                    [
                        html.Label("Categoria"),
                        dcc.Dropdown(
                            id="filtro-categoria",
                            options=[{"label": c, "value": c} for c in sorted(df_base["categoria"].unique())],
                            value=sorted(df_base["categoria"].unique().tolist()),
                            multi=True,
                        ),
                    ],
                    style={"width": "24%"},
                ),
                html.Div(
                    [
                        html.Label("Regiao"),
                        dcc.Dropdown(
                            id="filtro-regiao",
                            options=[{"label": r, "value": r} for r in sorted(df_base["regiao"].unique())],
                            value=sorted(df_base["regiao"].unique().tolist()),
                            multi=True,
                        ),
                    ],
                    style={"width": "24%"},
                ),
                html.Div(
                    [
                        html.Label("Canal de Venda"),
                        dcc.Dropdown(
                            id="filtro-canal",
                            options=[{"label": c, "value": c} for c in sorted(df_base["canal_venda"].unique())],
                            value=sorted(df_base["canal_venda"].unique().tolist()),
                            multi=True,
                        ),
                    ],
                    style={"width": "24%"},
                ),
                html.Div(
                    [
                        html.Label("Periodo"),
                        dcc.DatePickerRange(
                            id="filtro-data",
                            min_date_allowed=df_base["data"].min().date(),
                            max_date_allowed=df_base["data"].max().date(),
                            start_date=df_base["data"].min().date(),
                            end_date=df_base["data"].max().date(),
                            display_format="DD/MM/YYYY",
                        ),
                    ],
                    style={"width": "24%"},
                ),
            ],
            style={"display": "flex", "gap": "12px", "marginBottom": "20px"},
        ),
        html.Div(
            [
                html.Div(id="kpi-faturamento", style={"width": "33%"}),
                html.Div(id="kpi-lucro", style={"width": "33%"}),
                html.Div(id="kpi-margem", style={"width": "33%"}),
            ],
            style={"display": "flex", "gap": "12px", "marginBottom": "20px"},
        ),
        dcc.Graph(id="grafico-faturamento-categoria"),
        dcc.Graph(id="grafico-faturamento-mensal"),
        dcc.Graph(id="grafico-lucro-regiao"),
    ],
    style={"maxWidth": "1200px", "margin": "0 auto", "padding": "20px"},
)


def card_kpi(titulo: str, valor: str, cor: str) -> html.Div:
    return html.Div(
        [
            html.H4(titulo, style={"marginBottom": "8px"}),
            html.H2(valor, style={"marginTop": "0", "color": cor}),
        ],
        style={"padding": "12px", "border": "1px solid #ddd", "borderRadius": "8px"},
    )


@app.callback(
    Output("grafico-faturamento-categoria", "figure"),
    Output("grafico-faturamento-mensal", "figure"),
    Output("grafico-lucro-regiao", "figure"),
    Output("kpi-faturamento", "children"),
    Output("kpi-lucro", "children"),
    Output("kpi-margem", "children"),
    Input("filtro-categoria", "value"),
    Input("filtro-regiao", "value"),
    Input("filtro-canal", "value"),
    Input("filtro-data", "start_date"),
    Input("filtro-data", "end_date"),
)
def atualizar_dashboard(categorias, regioes, canais, data_inicio, data_fim):
    df = df_base.copy()
    df = df[df["categoria"].isin(categorias)]
    df = df[df["regiao"].isin(regioes)]
    df = df[df["canal_venda"].isin(canais)]
    df = df[(df["data"] >= pd.to_datetime(data_inicio)) & (df["data"] <= pd.to_datetime(data_fim))]

    if df.empty:
        fig_vazio = px.bar(title="Sem dados para os filtros selecionados")
        kpi_vazio = card_kpi("Sem dados", "R$ 0,00", "#999")
        return fig_vazio, fig_vazio, fig_vazio, kpi_vazio, kpi_vazio, kpi_vazio

    por_categoria = (
        df.groupby("categoria", as_index=False)["faturamento"]
        .sum()
        .sort_values("faturamento", ascending=False)
    )
    fig_categoria = px.bar(
        por_categoria,
        x="categoria",
        y="faturamento",
        title="Faturamento por Categoria",
        labels={"categoria": "Categoria", "faturamento": "Faturamento (R$)"},
        text_auto=".2s",
    )

    por_mes = df.groupby("mes", as_index=False)["faturamento"].sum().sort_values("mes")
    fig_mensal = px.line(
        por_mes,
        x="mes",
        y="faturamento",
        title="Evolucao do Faturamento Mensal",
        markers=True,
        labels={"mes": "Mes", "faturamento": "Faturamento (R$)"},
    )

    por_regiao = df.groupby("regiao", as_index=False)["lucro"].sum().sort_values("lucro", ascending=False)
    fig_regiao = px.bar(
        por_regiao,
        x="regiao",
        y="lucro",
        title="Lucro por Regiao",
        labels={"regiao": "Regiao", "lucro": "Lucro (R$)"},
        text_auto=".2s",
    )

    faturamento = df["faturamento"].sum()
    lucro = df["lucro"].sum()
    margem = (lucro / faturamento) * 100 if faturamento else 0

    kpi_faturamento = card_kpi("Faturamento", f"R$ {faturamento:,.2f}", "#1f77b4")
    kpi_lucro = card_kpi("Lucro", f"R$ {lucro:,.2f}", "#2ca02c")
    kpi_margem = card_kpi("Margem", f"{margem:.2f}%", "#ff7f0e")

    return fig_categoria, fig_mensal, fig_regiao, kpi_faturamento, kpi_lucro, kpi_margem


if __name__ == "__main__":
    app.run(debug=True)
