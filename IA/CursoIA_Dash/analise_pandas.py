import random
from pathlib import Path

import pandas as pd
import plotly.express as px


def gerar_csv(caminho_csv: Path) -> pd.DataFrame:
    random.seed(42)

    categorias = ["Eletronicos", "Roupas", "Casa", "Esporte", "Beleza"]
    regioes = ["Norte", "Nordeste", "Centro-Oeste", "Sudeste", "Sul"]
    canais = ["Online", "Loja Fisica", "Marketplace"]

    registros = []
    pedido_id = 1000

    for mes in range(1, 13):
        for _ in range(50):
            categoria = random.choice(categorias)
            regiao = random.choice(regioes)
            canal = random.choice(canais)

            if categoria == "Eletronicos":
                preco_base = random.uniform(800, 5000)
                custo_percentual = random.uniform(0.55, 0.75)
            elif categoria == "Roupas":
                preco_base = random.uniform(70, 400)
                custo_percentual = random.uniform(0.30, 0.50)
            elif categoria == "Casa":
                preco_base = random.uniform(120, 900)
                custo_percentual = random.uniform(0.35, 0.55)
            elif categoria == "Esporte":
                preco_base = random.uniform(90, 1200)
                custo_percentual = random.uniform(0.40, 0.60)
            else:
                preco_base = random.uniform(40, 300)
                custo_percentual = random.uniform(0.25, 0.45)

            quantidade = random.randint(1, 8)
            desconto = round(random.uniform(0.00, 0.18), 2)
            preco_unitario = round(preco_base * (1 - desconto), 2)
            custo_unitario = round(preco_unitario * custo_percentual, 2)

            dia = random.randint(1, 28)
            data = pd.Timestamp(year=2025, month=mes, day=dia)
            avaliacao = round(random.uniform(3.2, 5.0), 1)

            registros.append(
                {
                    "pedido_id": pedido_id,
                    "data": data,
                    "categoria": categoria,
                    "regiao": regiao,
                    "canal_venda": canal,
                    "quantidade": quantidade,
                    "preco_unitario": preco_unitario,
                    "custo_unitario": custo_unitario,
                    "avaliacao_cliente": avaliacao,
                }
            )
            pedido_id += 1

    df = pd.DataFrame(registros).sort_values("data").reset_index(drop=True)
    df.to_csv(caminho_csv, index=False, encoding="utf-8")
    return df


def analisar_dados(df: pd.DataFrame) -> list[str]:
    df["faturamento"] = df["quantidade"] * df["preco_unitario"]
    df["custo_total"] = df["quantidade"] * df["custo_unitario"]
    df["lucro"] = df["faturamento"] - df["custo_total"]
    df["margem_percentual"] = (df["lucro"] / df["faturamento"]) * 100
    df["mes"] = df["data"].dt.to_period("M").astype(str)

    insights = []

    faturamento_total = df["faturamento"].sum()
    lucro_total = df["lucro"].sum()
    margem_media = df["margem_percentual"].mean()
    insights.append(
        f"1) O faturamento total foi de R$ {faturamento_total:,.2f}, com lucro total de R$ {lucro_total:,.2f} e margem media de {margem_media:.2f}%."
    )

    top_categoria = (
        df.groupby("categoria", as_index=False)["faturamento"]
        .sum()
        .sort_values("faturamento", ascending=False)
        .iloc[0]
    )
    insights.append(
        f"2) A categoria com maior faturamento foi {top_categoria['categoria']}, totalizando R$ {top_categoria['faturamento']:,.2f}."
    )

    top_regiao_lucro = (
        df.groupby("regiao", as_index=False)["lucro"]
        .sum()
        .sort_values("lucro", ascending=False)
        .iloc[0]
    )
    insights.append(
        f"3) A regiao mais lucrativa foi {top_regiao_lucro['regiao']}, com lucro acumulado de R$ {top_regiao_lucro['lucro']:,.2f}."
    )

    ticket_medio_canal = (
        df.assign(ticket_pedido=df["faturamento"])
        .groupby("canal_venda", as_index=False)["ticket_pedido"]
        .mean()
        .sort_values("ticket_pedido", ascending=False)
        .iloc[0]
    )
    insights.append(
        f"4) O canal com maior ticket medio por pedido foi {ticket_medio_canal['canal_venda']}, com R$ {ticket_medio_canal['ticket_pedido']:,.2f}."
    )

    mes_forte = (
        df.groupby("mes", as_index=False)["faturamento"]
        .sum()
        .sort_values("faturamento", ascending=False)
        .iloc[0]
    )
    insights.append(
        f"5) O mes de maior faturamento foi {mes_forte['mes']}, com R$ {mes_forte['faturamento']:,.2f}."
    )

    correlacao = df[["avaliacao_cliente", "margem_percentual"]].corr().iloc[0, 1]
    insights.append(
        f"6) A correlacao entre avaliacao do cliente e margem percentual foi de {correlacao:.3f}, indicando relacao fraca entre satisfacao e margem."
    )

    return insights


def criar_visualizacoes(df: pd.DataFrame, pasta_saida: Path) -> list[Path]:
    pasta_saida.mkdir(parents=True, exist_ok=True)
    arquivos_gerados: list[Path] = []

    faturamento_por_categoria = (
        df.groupby("categoria", as_index=False)["faturamento"]
        .sum()
        .sort_values("faturamento", ascending=False)
    )
    fig_categoria = px.bar(
        faturamento_por_categoria,
        x="categoria",
        y="faturamento",
        title="Faturamento por Categoria",
        labels={"categoria": "Categoria", "faturamento": "Faturamento (R$)"},
        text_auto=".2s",
    )
    caminho_categoria = pasta_saida / "01_faturamento_por_categoria.html"
    fig_categoria.write_html(caminho_categoria)
    arquivos_gerados.append(caminho_categoria)

    faturamento_mensal = (
        df.groupby("mes", as_index=False)["faturamento"]
        .sum()
        .sort_values("mes")
    )
    fig_mensal = px.line(
        faturamento_mensal,
        x="mes",
        y="faturamento",
        title="Evolucao do Faturamento Mensal",
        markers=True,
        labels={"mes": "Mes", "faturamento": "Faturamento (R$)"},
    )
    caminho_mensal = pasta_saida / "02_faturamento_mensal.html"
    fig_mensal.write_html(caminho_mensal)
    arquivos_gerados.append(caminho_mensal)

    lucro_por_regiao = (
        df.groupby("regiao", as_index=False)["lucro"]
        .sum()
        .sort_values("lucro", ascending=False)
    )
    fig_regiao = px.bar(
        lucro_por_regiao,
        x="regiao",
        y="lucro",
        title="Lucro por Regiao",
        labels={"regiao": "Regiao", "lucro": "Lucro (R$)"},
        text_auto=".2s",
    )
    caminho_regiao = pasta_saida / "03_lucro_por_regiao.html"
    fig_regiao.write_html(caminho_regiao)
    arquivos_gerados.append(caminho_regiao)

    faturamento_por_canal = (
        df.groupby("canal_venda", as_index=False)["faturamento"]
        .sum()
        .sort_values("faturamento", ascending=False)
    )
    fig_canal = px.pie(
        faturamento_por_canal,
        names="canal_venda",
        values="faturamento",
        title="Participacao do Faturamento por Canal",
    )
    caminho_canal = pasta_saida / "04_participacao_por_canal.html"
    fig_canal.write_html(caminho_canal)
    arquivos_gerados.append(caminho_canal)

    fig_correlacao = px.scatter(
        df,
        x="avaliacao_cliente",
        y="margem_percentual",
        color="categoria",
        title="Correlacao: Avaliacao do Cliente x Margem Percentual",
        labels={
            "avaliacao_cliente": "Avaliacao do Cliente",
            "margem_percentual": "Margem Percentual (%)",
        },
        trendline="ols",
    )
    caminho_correlacao = pasta_saida / "05_correlacao_avaliacao_margem.html"
    fig_correlacao.write_html(caminho_correlacao)
    arquivos_gerados.append(caminho_correlacao)

    return arquivos_gerados


def main() -> None:
    pasta_base = Path(__file__).resolve().parent
    caminho_csv = pasta_base / "dados_vendas_ficticios.csv"

    if caminho_csv.exists():
        df = pd.read_csv(caminho_csv, parse_dates=["data"])
    else:
        df = gerar_csv(caminho_csv)

    insights = analisar_dados(df)
    pasta_graficos = pasta_base / "visualizacoes_plotly"
    graficos = criar_visualizacoes(df, pasta_graficos)

    print("Arquivo CSV pronto em:", caminho_csv)
    print("\nInsights extraidos:")
    for insight in insights:
        print(insight)
    print("\nGraficos Plotly gerados:")
    for grafico in graficos:
        print("-", grafico)


if __name__ == "__main__":
    main()
