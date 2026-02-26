import streamlit as st
import sqlite3
import face_recognition
import numpy as np
import pickle

# --- CONFIGURAÇÃO DE SEGURANÇA ---
SENHA_ADM = "admin123"  # Você pode mudar para a senha que desejar

# --- CONEXÃO COM O BANCO ---
def connect_db():
    conn = sqlite3.connect('dados_sst.db', check_same_thread=False)
    return conn

def iniciar_banco():
    conn = connect_db()
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS colaboradores 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT, area TEXT, 
                  encoding BLOB, nr10 TEXT, nr35_a TEXT, nr35_b TEXT, aso TEXT, pendencias TEXT)''')
    conn.commit()
    conn.close()

iniciar_banco()

st.set_page_config(page_title="SST Face ID", page_icon="🛡️")

aba1, aba2 = st.tabs(["🔍 Verificação Rápida", "⚙️ Administração"])

# --- ABA DE IDENTIFICAÇÃO (PÚBLICA) ---
with aba1:
    st.header("Consulta de Colaborador")
    foto_v = st.camera_input("Identificar agora")

    if foto_v:
        conn = connect_db()
        c = conn.cursor()
        c.execute("SELECT nome, area, encoding, nr10, nr35_a, nr35_b, aso, pendencias FROM colaboradores")
        registros = c.fetchall()
        conn.close()

        img_v = face_recognition.load_image_file(foto_v)
        encoding_v = face_recognition.face_encodings(img_v)

        if encoding_v:
            found = False
            for r in registros:
                db_encoding = pickle.loads(r[2])
                match = face_recognition.compare_faces([db_encoding], encoding_v[0], tolerance=0.5)
                if match[0]:
                    st.success(f"### Identificado: {r[0]}")
                    st.write(f"**Área:** {r[1]}")
                    st.divider()
                    c1, c2 = st.columns(2)
                    c1.write(f"📅 **NR10:** {r[3]}")
                    c1.write(f"📅 **ASO:** {r[6]}")
                    c2.write(f"📅 **NR35 (A):** {r[4]}")
                    c2.write(f"📅 **NR35 (B):** {r[5]}")
                    if r[7]: st.warning(f"⚠️ **Pendências:** {r[7]}")
                    found = True
                    break
            if not found: st.error("Colaborador não cadastrado.")
        else: st.warning("Rosto não detectado.")

# --- ABA DE ADMINISTRAÇÃO (PROTEGIDA) ---
with aba2:
    st.header("Painel de Controle")
    
    # Sistema de Login Simples
    senha_digitada = st.text_input("Digite a senha de administrador", type="password")
    
    if senha_digitada == SENHA_ADM:
        st.success("Acesso Autorizado")
        
        menu_adm = st.radio("O que deseja fazer?", ["Cadastrar Novo", "Ver Todos / Excluir"])
        
        if menu_adm == "Cadastrar Novo":
            with st.form("cadastro_novo"):
                nome = st.text_input("Nome Completo")
                area = st.text_input("Área")
                nr10 = st.text_input("Vencimento NR10")
                aso = st.text_input("Vencimento ASO")
                foto_c = st.camera_input("Capturar Biometria")
                submit = st.form_submit_button("Salvar")
                
                if submit and foto_c and nome:
                    img = face_recognition.load_image_file(foto_c)
                    enc = face_recognition.face_encodings(img)
                    if enc:
                        blob = pickle.dumps(enc[0])
                        conn = connect_db()
                        c = conn.cursor()
                        c.execute("INSERT INTO colaboradores (nome, area, encoding, nr10, aso) VALUES (?,?,?,?,?)", 
                                  (nome, area, blob, nr10, aso))
                        conn.commit()
                        conn.close()
                        st.success("Cadastrado com sucesso!")
                    else: st.error("Erro na leitura da foto.")
        
        elif menu_adm == "Ver Todos / Excluir":
            conn = connect_db()
            df_colabs = conn.execute("SELECT id, nome, area FROM colaboradores").fetchall()
            conn.close()
            for colab in df_colabs:
                c1, c2 = st.columns([3, 1])
                c1.write(f"{colab[1]} ({colab[2]})")
                if c2.button("Excluir", key=f"del_{colab[0]}"):
                    conn = connect_db()
                    conn.execute(f"DELETE FROM colaboradores WHERE id={colab[0]}")
                    conn.commit()
                    conn.close()
                    st.rerun()
    
    elif senha_digitada != "":
        st.error("Senha Incorreta")