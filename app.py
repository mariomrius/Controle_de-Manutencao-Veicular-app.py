import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import time

# =========================
# CONFIGURAÇÃO DA PÁGINA
# =========================
st.set_page_config(
    page_title="Controle de Manutenção Veicular",
    layout="wide"
)

# =========================
# BANCO DE DADOS
# =========================
conn = sqlite3.connect(
    'manutencao.db',
    check_same_thread=False
)

cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS manutencoes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    data TEXT,
    km INTEGER,
    peca TEXT,
    valor_peca REAL,
    mao_obra REAL,
    valor_total REAL,
    descricao TEXT
)
''')

conn.commit()

# =========================
# FUNÇÕES
# =========================
def formatar_real(valor):

    return (
        f"R$ {valor:,.2f}"
        .replace(",", "X")
        .replace(".", ",")
        .replace("X", ".")
    )

def formatar_km(valor):

    return f"{int(valor):,}".replace(",", ".")

def adicionar_manutencao(
    data,
    km,
    peca,
    valor_peca,
    mao_obra,
    descricao
):

    valor_total = valor_peca + mao_obra

    data_br = data.strftime('%d/%m/%Y')

    cursor.execute('''
    INSERT INTO manutencoes
    (
        data,
        km,
        peca,
        valor_peca,
        mao_obra,
        valor_total,
        descricao
    )
    VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (
        data_br,
        km,
        peca,
        valor_peca,
        mao_obra,
        valor_total,
        descricao
    ))

    conn.commit()

def listar_manutencoes():

    query = '''
    SELECT * FROM manutencoes
    ORDER BY id DESC
    '''

    return pd.read_sql_query(
        query,
        conn
    )

def excluir_manutencao(id_registro):

    cursor.execute(
        "DELETE FROM manutencoes WHERE id = ?",
        (id_registro,)
    )

    conn.commit()

def atualizar_manutencao(
    id_registro,
    data,
    km,
    peca,
    valor_peca,
    mao_obra,
    descricao
):

    valor_total = valor_peca + mao_obra

    data_br = data.strftime('%d/%m/%Y')

    cursor.execute('''
    UPDATE manutencoes
    SET
        data = ?,
        km = ?,
        peca = ?,
        valor_peca = ?,
        mao_obra = ?,
        valor_total = ?,
        descricao = ?
    WHERE id = ?
    ''', (
        data_br,
        km,
        peca,
        valor_peca,
        mao_obra,
        valor_total,
        descricao,
        id_registro
    ))

    conn.commit()

# =========================
# TÍTULO
# =========================
st.title("🚗 Controle de Manutenção Veicular")

# =========================
# MENU
# =========================
menu = st.sidebar.selectbox(
    "Menu",
    [
        "Cadastrar Manutenção",
        "Consultar Manutenções"
    ]
)

# =========================
# CADASTRAR
# =========================
if menu == "Cadastrar Manutenção":

    st.subheader(
        "Cadastrar Nova Manutenção"
    )

    with st.form(
        "form_manutencao",
        clear_on_submit=True
    ):

        data = st.date_input(
            "Data",
            format="DD/MM/YYYY"
        )

        km = st.number_input(
            "KM do veículo",
            min_value=0,
            step=1000,
            format="%d"
        )

        st.info(
            f"KM Atual: {formatar_km(km)}"
        )

        peca = st.text_input(
            "Peça"
        )

        valor_peca = st.number_input(
            "Valor da peça (R$)",
            min_value=0.0,
            format="%.2f"
        )

        st.caption(
            formatar_real(valor_peca)
        )

        mao_obra = st.number_input(
            "Mão de obra (R$)",
            min_value=0.0,
            format="%.2f"
        )

        st.caption(
            formatar_real(mao_obra)
        )

        valor_total = (
            valor_peca +
            mao_obra
        )

        st.info(
            f"Valor Total: {formatar_real(valor_total)}"
        )

        descricao = st.text_area(
            "Descrição"
        )

        salvar = st.form_submit_button(
            "Salvar"
        )

        if salvar:

            adicionar_manutencao(
                data,
                km,
                peca,
                valor_peca,
                mao_obra,
                descricao
            )

            st.success(
                "Manutenção cadastrada com sucesso!"
            )

            time.sleep(1)

            st.rerun()

# =========================
# CONSULTAR
# =========================
elif menu == "Consultar Manutenções":

    st.subheader(
        "Histórico de Manutenções"
    )

    df = listar_manutencoes()

    if not df.empty:

        df_exibir = df.copy()

        df_exibir['km'] = df_exibir[
            'km'
        ].apply(formatar_km)

        df_exibir['valor_peca'] = df_exibir[
            'valor_peca'
        ].apply(formatar_real)

        df_exibir['mao_obra'] = df_exibir[
            'mao_obra'
        ].apply(formatar_real)

        df_exibir['valor_total'] = df_exibir[
            'valor_total'
        ].apply(formatar_real)

        df_exibir.columns = [
            "ID",
            "Data",
            "KM",
            "Peça",
            "Valor Peça",
            "Mão de Obra",
            "Valor Total",
            "Descrição"
        ]

        st.dataframe(
            df_exibir,
            use_container_width=True,
            hide_index=True
        )

        st.divider()

        st.subheader(
            "Ações"
        )

        ids = df['id'].tolist()

        id_selecionado = st.selectbox(
            "Selecione o ID",
            ids
        )

        col1, col2 = st.columns(2)

        with col1:

            if st.button(
                "✏️ Editar"
            ):

                st.session_state[
                    'editar_id'
                ] = id_selecionado

        with col2:

            if st.button(
                "🗑️ Excluir"
            ):

                excluir_manutencao(
                    id_selecionado
                )

                st.success(
                    "Registro excluído!"
                )

                time.sleep(1)

                st.rerun()

        total = listar_manutencoes()[
            'valor_total'
        ].sum()

        st.metric(
            "💰 Total Gasto",
            formatar_real(total)
        )

        # =========================
        # FORMULÁRIO DE EDIÇÃO
        # =========================
        if 'editar_id' in st.session_state:

            id_editar = st.session_state[
                'editar_id'
            ]

            registro_filtrado = df[
                df['id'] == id_editar
            ]

            if not registro_filtrado.empty:

                st.divider()

                st.subheader(
                    "✏️ Editar Manutenção"
                )

                registro = registro_filtrado.iloc[0]

                with st.form(
                    "form_editar"
                ):

                    nova_data = st.date_input(
                        "Data",
                        datetime.strptime(
                            registro['data'],
                            '%d/%m/%Y'
                        ),
                        format="DD/MM/YYYY"
                    )

                    novo_km = st.number_input(
                        "KM",
                        min_value=0,
                        value=int(
                            registro['km']
                        ),
                        step=1000,
                        format="%d"
                    )

                    st.info(
                        f"KM Atual: {formatar_km(novo_km)}"
                    )

                    nova_peca = st.text_input(
                        "Peça",
                        value=registro['peca']
                    )

                    novo_valor_peca = st.number_input(
                        "Valor da peça (R$)",
                        min_value=0.0,
                        value=float(
                            registro['valor_peca']
                        ),
                        format="%.2f"
                    )

                    st.caption(
                        formatar_real(
                            novo_valor_peca
                        )
                    )

                    nova_mao_obra = st.number_input(
                        "Mão de obra (R$)",
                        min_value=0.0,
                        value=float(
                            registro['mao_obra']
                        ),
                        format="%.2f"
                    )

                    st.caption(
                        formatar_real(
                            nova_mao_obra
                        )
                    )

                    novo_total = (
                        novo_valor_peca +
                        nova_mao_obra
                    )

                    st.info(
                        f"Valor Total: {formatar_real(novo_total)}"
                    )

                    nova_descricao = st.text_area(
                        "Descrição",
                        value=registro['descricao']
                    )

                    col_a, col_b = st.columns(2)

                    with col_a:

                        atualizar = st.form_submit_button(
                            "Atualizar"
                        )

                    with col_b:

                        cancelar = st.form_submit_button(
                            "Cancelar"
                        )

                    if atualizar:

                        atualizar_manutencao(
                            id_editar,
                            nova_data,
                            novo_km,
                            nova_peca,
                            novo_valor_peca,
                            nova_mao_obra,
                            nova_descricao
                        )

                        del st.session_state[
                            'editar_id'
                        ]

                        st.success(
                            "Registro atualizado!"
                        )

                        time.sleep(1)

                        st.rerun()

                    if cancelar:

                        del st.session_state[
                            'editar_id'
                        ]

                        st.rerun()

            else:

                del st.session_state[
                    'editar_id'
                ]

                st.rerun()

    else:

        st.warning(
            "Nenhuma manutenção cadastrada."
        )
