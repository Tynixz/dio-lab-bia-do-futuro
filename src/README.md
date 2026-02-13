# Passo a passo de Execução

## Setup do Ollama (5 minutos)
```bash
# 1. Instalar Ollama (ollama.ai)
# 2. Baixar um modelo leve
ollama pull gpt-oss

# 3. Testar se funciona
ollama run gpt-oss "olá!"

```

## Código completo

Todo código-fonte está no arquivo `app.py`. 

## Exemplo de requirements.txt

```
streamlit
openai
python-dotenv
```

## Como Rodar

```bash
# 1. Instalar dependências

pip install streamlit pandas requests
ou
python -m pip install streamlit pandas requests

# 2. Garantir que Ollama está rodando
ollama serve

# 3. Rodar o app
streamlit run .\src\app.py
ou
python -m streamlit run .\src\app.py
```

## Estrutura

```
src/
├── app.py              # Aplicação principal (Streamlit)
├── agente.py           # Lógica do agente (Ollama)
```
## Evidências de Execução