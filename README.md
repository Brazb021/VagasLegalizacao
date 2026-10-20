# ⚖️ Vagas de Legalização — Dashboard de Vagas Gupy

Clone do [MinhasVagas](https://github.com/lucsgdeo/MinhasVagas) adaptado para quem trabalha com **legalização de empresas** (abertura, alteração e baixa de empresas, societário, paralegal, alvarás e licenças).

O monitor em Python consulta a API pública da Gupy todo dia, guarda as vagas em `data/` e o GitHub Pages serve o dashboard.

---

## 📌 O que mudou em relação ao original

| | MinhasVagas (original) | Este projeto |
|---|---|---|
| Aba principal | **Vagas Tech** (Suporte, Estágio, Dev, TI, Outras) | **Legalização** (Todas, Legalização, Societário, Paralegal, Licenças) |
| Termos buscados | suporte, estágio, dev, TI… | legalização, abertura de empresas, societário, paralegal, alvará, licenciamento, regularização |
| Filtro de cargo (tira sênior/pleno/gerente) | em todas as abas | **só em Vagas Gerais**: na Legalização, pleno e sênior ficam |
| Filtro de escopo | tira estágio que não é de TI | tira **advogado, estágio, sócio** e licenciamento de software, marca ou ambiental |
| Janela de publicação / retenção | 4 dias / 7 dias | **30 dias / 30 dias** na Legalização (vaga rara); Gerais igual ao original |
| Sub-aba padrão | Últimos 2 dias | **Últimos 7 dias** |
| Histórico | `data/vagas_recentes.json` | `data/vagas_legalizacao.json` |

A aba **Vagas Gerais**, a aba **Horários de Postagem**, os temas, o modo escuro, o painel de descrição e a marcação "Vista" funcionam igual ao original.

---

## 🧭 Buscas

Todas ficam na lista `BUSCAS` de `monitor/consultas.py`. Cada linha gera uma consulta presencial (São Paulo + ABC) e uma remota.

| Termo (`jobName`) | Rótulo / botão |
|---|---|
| `legalização` | Legalização |
| `abertura de empresas` | Legalização |
| `societário` | Societário |
| `paralegal` | Paralegal |
| `alvará` | Licenças |
| `licenciamento` | Licenças |
| `regularização` | Licenças |

A API da Gupy busca no **título** e ignora acentos. Também testamos `junta comercial`, `cnpj`, `certidões` e `despachante`, mas hoje esses termos não devolvem nenhuma vaga. Para incluir um termo novo, basta adicionar uma linha em `BUSCAS`.

As cidades ficam em `CIDADES`, no mesmo arquivo.

### Filtro de escopo

Está em `legalizacao_fora_do_escopo()` (`monitor/descricoes.py`). A lista `TERMOS_FORA_DE_LEGALIZACAO` é escrita **sem acento**, com um grupo de termos por linha. Quando o título traz "legalização" ou "paralegal", a vaga fica mesmo que tenha um termo da lista.

---

## 🚀 Como executar

```bash
python monitor/main.py                                   # atualiza data/*.json (usa a API real)
python -m unittest discover -s . -p "test_*.py"          # testes, sem rede
python -m http.server                                    # abre o site em http://localhost:8000
```

Usa só a biblioteca padrão do Python 3.11+. No Windows, sem o pacote `tzdata`, o fuso cai para UTC−3 fixo, que dá o mesmo resultado (o Brasil não tem horário de verão).

---

## 🔄 Automação (GitHub Actions)

- `main.yml` roda **todo dia às 18h30** (21:30 UTC) e também pode ser disparado pela aba **Actions**. Ele executa o monitor e comita o `data/`.
- `guardiao.yml` roda a cada 3h e só executa o monitor quando a execução do dia não aconteceu (o GitHub às vezes descarta agendamentos).
- O secret opcional `HC_PING_URL` ativa um heartbeat externo.

Para os commits do bot funcionarem, o repositório precisa de **Settings → Actions → General → Workflow permissions → Read and write**.
