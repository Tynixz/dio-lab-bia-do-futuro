# Base de Conhecimento

## Dados Utilizados

Descreva se usou os arquivos da pasta `data`, por exemplo:

| Arquivo | Formato | Utilização no Agente |
|---------|---------|---------------------|
| `clientes.json` | JSON | Armazenar dados pessoais, perfil do investidor, renda e objetivos financeiros |
| `transacoes.csv` | CSV | Analisar padrão de gastos, categorias e comportamento de consumo |
| `assinaturas.csv` | CSV | Identificar gastos recorrentes com serviços e assinaturas |
| `dividas.csv` | CSV | Avaliar dívidas atuais, juros e impacto no orçamento mensal |
| `metas.csv` | CSV | Verificar metas financeiras, prazos e progresso atual |
| `glossario_financeiro.json` | JSON | Explicar termos financeiros de forma simples e didática |
| `produtos_financeiros.json` | JSON | Recomendar produtos financeiros com base no perfil do cliente |
| `regras_orcamento.json` | JSON | Gerar sugestões de orçamento com percentuais recomendados por perfil de renda |

> [!TIP]
> **Quer um dataset mais robusto?** Você pode utilizar datasets públicos do [Hugging Face](https://huggingface.co/datasets) relacionados a finanças, desde que sejam adequados ao contexto do desafio.

---

## Adaptações nos Dados

> Você modificou ou expandiu os dados mockados? Descreva aqui.

O dataset inicial foi adaptado e expandido para representar melhor um cenário realista de organização financeira e permitir que o agente gere respostas mais completas e personalizadas.

As principais modificações realizadas foram:

- **Criação do arquivo `clientes.json`**, contendo informações detalhadas de múltiplos clientes, incluindo:
  - nome completo
  - idade
  - profissão
  - renda mensal
  - perfil de investidor
  - objetivo principal
  - cidade/estado
  - dependentes

- **Expansão do arquivo `transacoes.csv`**, adicionando novas colunas para enriquecer a análise financeira:
  - `data`: permite avaliar gastos ao longo do tempo
  - `categoria`: permite identificar padrões de consumo (moradia, lazer, alimentação, transporte)
  
  Além disso, o arquivo já possui informações como:
  - forma de pagamento
  - recorrência
  - essencialidade
  - compras parceladas

- **Expansão do arquivo `produtos_financeiros.json`**, adicionando atributos para facilitar recomendações mais explicadas e coerentes:
  - `rentabilidade` (baixa, média, alta)
  - `risco` (baixo, médio, alto)

- **Inclusão do arquivo `assinaturas.csv`**, permitindo ao agente identificar gastos recorrentes e sugerir cortes ou otimizações.

- **Inclusão do arquivo `dividas.csv`**, permitindo ao agente priorizar pagamentos e sugerir estratégias de quitação com base em juros e status da dívida.

- **Inclusão do arquivo `metas.csv`**, permitindo que o agente compare valores atuais e valores totais, sugerindo planos de economia mensais até o prazo final.

- **Criação do arquivo `glossario_financeiro.json`**, contendo explicações simplificadas e exemplos práticos de termos financeiros, ajudando o agente a atuar também como ferramenta educativa.

- **Criação do arquivo `regras_orcamento.json`**, permitindo recomendações baseadas em percentuais por categoria, conforme perfis de renda (baixa, média e alta renda).

- **Remoção do arquivo `historico_atendimento.csv`**, pois não era essencial para o funcionamento do agente no contexto do projeto, e os arquivos principais já fornecem dados suficientes para gerar recomendações personalizadas.

---

## Estratégia de Integração

### Como os dados são carregados?
> Descreva como seu agente acessa a base de conhecimento.

```Python
import pandas as pd
import json

# CSVs
transacoes = pd.read_csv('data/transacoes.csv')
assinaturas = pd.read_csv('data/assinaturas.csv')
dividas = pd.read_csv('data/dividas.csv')
metas = pd.read_csv('data/metas.csv')

```# JSONs
with open('data/clientes.json', 'r', encoding='utf-8') as f:
    clientes = json.load(f)

with open('data/glossario_financeiro.json', 'r', encoding='utf-8') as f:
    glossario = json.load(f)

with open('data/produtos_financeiros.json', 'r', encoding='utf-8') as f:
    produtos = json.load(f)

with open('data/regras_orcamento.json', 'r', encoding='utf-8') as f:
    regras_orcamento = json.load(f)
```

### Como os dados são usados no prompt?
> Os dados vão no system prompt? São consultados dinamicamente?

Os dados são consultados dinamicamente conforme o cliente selecionado, utilizando o `id_cliente` como chave principal.

O agente monta um contexto personalizado reunindo:

 - informações pessoais e perfil do investidor (`clientes.json`)

 - transações e categorias de gastos (`transacoes.csv`)

 - assinaturas recorrentes (`assinaturas.csv`)

 - dívidas e parcelas pendentes (`dividas.csv`)

 - metas e progresso financeiro (`metas.csv`)

 - regras de orçamento por categoria (`regras_orcamento.json`)

Além disso, quando o usuário solicita explicações sobre conceitos financeiros, o agente utiliza o `glossario_financeiro.json` para responder com linguagem simples e exemplos práticos.

As recomendações de investimento são feitas cruzando o perfil do investidor do cliente com os produtos disponíveis no `produtos_financeiros.json`, considerando também risco e rentabilidade.

---

## Exemplo de Contexto Montado

> Mostre um exemplo de como os dados são formatados para o agente.

Dados do Cliente:
- Nome: Ana Maria Braga
- Idade: 35 anos
- Profissão: Analista de Marketing
- Cidade: São Paulo/SP
- Perfil: Moderado
- Renda mensal: R$ 4.500
- Objetivo principal: Comprar apartamento
- Dependentes: 0

Metas Financeiras:
- Reserva de emergência: R$ 5.000 / R$ 10.000 (Prazo: 2026-12-31)

Dívidas:
- Cartão de crédito: R$ 3.000 (6 parcelas restantes, juros 8.5%, status: em dia)

Assinaturas Ativas:
- Netflix: R$ 39,90/mês
- Spotify: R$ 19,90/mês

Últimas transações:
- 2026-01-05: moradia (pix) - R$ 1.200
- 2026-01-10: lazer (crédito - 3/12) - R$ 250
- 2026-01-15: alimentação (débito recorrente) - R$ 300

Regras de orçamento aplicáveis:
- Moradia: 30%
- Alimentação: 20%
- Lazer: 15%

Produtos financeiros recomendados para perfil moderado:
- CDB Liquidez Diária (risco baixo, rentabilidade média)
- Fundos Imobiliários (risco médio, rentabilidade média)

