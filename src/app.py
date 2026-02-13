# o primeiro bloco de informação deve ser dos dados que serão carregados. Para isso ele precisa de duas bibliotecas, do JSON e PANDAS
import json
import pandas as pd
import requests
import streamlit as st
import os 

#problema para encontrar o caminho de cada documento

BASE_DIR = os.path.dirname(os.path.abspath(__file__)) 
DATA_DIR = os.path.join(BASE_DIR, "..", "data")


#=============== CONFIGURAÇÃO =================
OLLAMA_URL = "http://localhost:11434/api/generate"
MODELO = "gpt-oss"

#================= CARREGAR DADOS ================
transacoes = pd.read_csv(os.path.join(DATA_DIR, "transacoes.csv"))
assinaturas = pd.read_csv(os.path.join(DATA_DIR, 'assinaturas.csv'), sep=",", encoding="utf-8")
dividas = pd.read_csv(os.path.join(DATA_DIR, 'dividas.csv'))
metas = pd.read_csv(os.path.join(DATA_DIR, 'metas.csv'))
                    
with open(os.path.join(DATA_DIR, "clientes.json"), encoding="utf-8") as f:
    clientes = json.load(f)

with open(os.path.join(DATA_DIR, "glossario_financeiro.json"), encoding="utf-8") as f:
    glossario = json.load(f)

with open(os.path.join(DATA_DIR, "produtos_financeiros.json"), encoding="utf-8") as f:
    produtos = json.load(f)

with open(os.path.join(DATA_DIR, "regras_orcamento.json"), encoding="utf-8") as f:
    regras_orcamento = json.load(f)


# como eu tenho uma lista com mais de 1 usuário, preciso primeiro saber qual usuário está utilizando o chat

#================= PEGAR NOME DO USUÁRIO =====================                 NO STREAMLIT
nome_digitado = st.text_input("Digite seu primeiro nome para acessar seus dados:").strip().lower()
if not nome_digitado:
    st.warning("Por favor, digite seu primeiro nome para continuar.")
    st.stop()

#================= BUSCAR CLIENTE =====================
cliente_encontrado = None

for c in clientes:
    primeiro_nome = c["nome_completo"].split()[0].lower() #lower para independer de como a pessoa escrever, conseguirmos encontrar no Sistema
    if primeiro_nome == nome_digitado:
        cliente_encontrado = c
        break #só isso que é preciso fazer.

if cliente_encontrado is None: #se não encontrar o nome do cliente, fecha o programa. ISSO USANDO NO STREAMLIT
    st.error("Cliente não encontrado. Verifique o nome e tente novamente.")
    st.stop()



#=============== PEGAR ID DO CLIENTE ==================
id_cliente = cliente_encontrado["id_cliente"]


#Encontraando o ID do cliente, todos os dados das outras planilhas estarão vinculados por esse ID.

#================= FILTRAR DADOS =====================
transacoes_cliente = transacoes[transacoes["id_cliente"] == id_cliente] #primeiro pego a planilha "transacoes", depois procuro as transações do id do cliente. Usando novamente "transacoes" no código ela vai pegas os valores das linhas "true", ou seja, as linhas que ouve transacao daquele id do usuário. E o id precisa ser == aoa id_usuario que pegamos anteriormente com o primeiro nome da pessoa
assinaturas_cliente = assinaturas[assinaturas["id_cliente"] == id_cliente]
dividas_cliente = dividas[dividas["id_cliente"] == id_cliente]
metas_cliente = metas[metas["id_cliente"] == id_cliente]

#Como foi feita uma tabela apenas para as dívidas de cada cliente, abaixo faço a conta para saber o total que falta para quitar a dívida.
#No caso da meta, vai somar op valor total que já tem para as metas. O ".sum()" está ali para somar caso o cliente tenha mais de uma meta.

#================= CÁLCULOS =====================
total_divida_restante = (dividas_cliente["parcela_mensal"] * dividas_cliente["parcelas_restantes"]).sum()
reserva_atual = metas_cliente["valor_atual"].sum()


#Agora precisamos montar o nosso contexto. Primeiro carregar as info dos arquivos e carregar as info do cliente que estiver ali, como fiz acima 
# e abaixo eu darei um contexto a minha IA quando for usar.

#============== MONTAR CONTEXTO =================

contexto = f"""
CLIENTE: {cliente_encontrado['nome_completo']}, {cliente_encontrado['idade']} anos, perfil {cliente_encontrado['perfil_investidor']}
OBJETIVO: {cliente_encontrado['objetivo_principal']}
RENDA: R$ {cliente_encontrado['renda_mensal']} | RESERVA ATUAL: R${reserva_atual:.2f}

TRANSAÇÕES RECENTES:
{transacoes_cliente.to_string(index=False)}

DÍVIDAS RESTANTES:
R$ {total_divida_restante:.2f}

PRODUTOS DISPONÍVEIS:
{json.dumps(produtos, indent=2, ensure_ascii=False)}
"""
# RESUMO: cliente_encontrado = serve para pegar dados do cliente e montar texto no contexto. Trás a ficha completa do cliente.
#         id_cliente = serve para filtrar tabelas e puxar transações, dívidas, metas, etc. Apenas para cruzar as tabelas.


# O escrito em docs/03-prompts

#============== SYSTEM PROMPT ===================

SYSTEM_PROMPT = """Você é a Vênus, uma assistente pessoal de finanças especializada em Organização Financeira Básica e Educação Financeira.

Seu objetivo é direcionar o cliente a fazer escolhas melhores: onde gastar, onde não gastar, como guardar dinheiro, onde, etc. Tudo como uma professora gente boa, falando de um jeito simples.
A Vênus (seu nome como assistente pessoal de finanças) analisa informações do cliente como renda, perfil de investidor, transações, assinaturas, dívidas e metas financeiras, para sugerir:
- ajustes de orçamento por categoria (moradia, alimentação, lazer e transporte)
- identificação de gastos recorrentes desnecessários
- estratégias para quitar dívidas com maior impacto de juros
- recomendações educativas de produtos financeiros compatíveis com o perfil do cliente
- explicações simples de termos financeiros utilizando glossário interno

Exemplo de estilo:
Responda sempre de forma simples, com emojis e listas curtas quando necessário.


REGRAS:
1. Sempre baseie suas respostas nos dados fornecidos
2. Nunca invente informações financeiras
3. Se não souber algo, admita e ofereça alternativas
4. Nunca forneça dados de outro cliente
5. Nunca exibir CPF, número de conta, cartão, endereço, telefone ou dados bancários.
6. Se o nome do cliente NÃO estiver disponível no contexto, peça o nome antes de responder. 
7. Responda de forma sucinta e direta, com no máximo 2 parágrafos
8. Sempre responda de forma simples e interessante para ser lido (uso de emote e listas)
"""
#alterei a regra 6 para que o chat só pergunte novamente o nome (pois perguntará antes para saber o id) caso ele não tenha id encontrado.


#Ollama é o meu "chatGPT" de graça e de forma local.
#Essa é a integração com o Ollama:

# =========== CHAMAR OLLAMA ================
def perguntar(msg):
    prompt = f"""
    {SYSTEM_PROMPT}

    CONTEXTO DO CLIENTE:
    {contexto}

    pergunta: {msg}"""
    
    r = requests.post(OLLAMA_URL, json={"model": MODELO, "prompt": prompt, "stream": False})
    return r.json()['response']

# Agora é fazer isso tudo virar um chat. Os dados,etc. E agora, como etapa final vamos criar uma INTERFACE do STREAMLIT.
#Streamlit é uma biblioteca em Python, OpenSource, onde vamos poder criar rapidamentes chatbots. Aplicações voltadas para LLMs.
#Ele faz um FrontEnd através de alguns facilitadores. Assim podemos fazer ele virar um chat bot.
#Usaremos essa ferramenta para acelerar esse desenvolvimento.


#========== INTERFACE ===============
st.title("Olá! Sou Vênus, sua assistente pessoal de finanças 💜")

if "mensagens" not in st.session_state: # Se ainda não existe uma lista chamada mensagens, crie.
    st.session_state.mensagens = []  # o "st.session_state" é uma caixinha de memória do Streamlit, guarda os dados enquanto é utilizado.
                                     #toda vez que você envia uma mensagem, o Streamlit reexecuta o código inteiro do começo.
                                     #Então se você não guardar as mensagens no "session_state", o chat reinicia toda hora.

#Mostra histórico
for msg in st.session_state.mensagens:    #Para cada mensagem salva no histórico, mostre ela na tela. É um loop, ele vai passando por cada item da lista.
    st.chat_message(msg["role"]).write(msg["content"]) #"st.chat_message(msg["role"])" Esse comando cria um balão de chat.
                                                       #E o "msg["role"]" define quem está falando. "user" = balão do usuário   "assistant" = balão da Vênu
                                                       #  "msg["role"]" = quem falou     "msg["content"]" = o que foi dito

#input do usuário
if pergunta := st.chat_input("Sua dúvida sobre finanças..."): # :=  = walrus operator ("Pegue o que o usuário digitou e já guarde na variável pergunta.")
    st.session_state.mensagens.append({"role":"user","content": pergunta})
    st.chat_message("user").write(pergunta) #Isso cria um balão do usuário e escreve o texto digitado. Exibindo na tela.

    with st.spinner("Vênus está pensando..."): #st.spinner() Mostra um loading animado, tipo uma ampulheta do lado. O "with" é para Enquanto eu estiver executando esse bloco, mostra o spinner.
        resposta = perguntar(pergunta)         # usuário manda pergunta   Streamlit chama perguntar()     Ollama responde       salva na variável resposta


    st.session_state.mensagens.append({"role":"assistant", "content": resposta}) #salva a resposta da IA
    st.chat_message("assistant").write(resposta) #Cria o balão da Vênus e escreve a resposta.

#Ollama seria o cérebro enquando o Streamlit a tela onde o usuário conversa
