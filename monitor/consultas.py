"""Consultas à API da Gupy.

Único arquivo a editar para incluir, remover ou ajustar uma busca.
URL, pasta de destino e rótulo do card saem daqui.
"""

from dataclasses import dataclass
from urllib.parse import urlencode

BASE_URL = "https://portal.gupy.io/api/job-search/jobs"

CIDADES = "São Bernardo do Campo,Diadema,Santo André,São Caetano do Sul,São Paulo"
ESTADO = "São Paulo"
LIMIT = 100  # teto da API; acima disso retorna HTTP 400

# As duas URLs padrão. Presencial e remoto só diferem neste filtro.
MODALIDADES = {
    "Presencial": {"city": CIDADES, "state": ESTADO},
    "Remoto": {"workplaceType": "remote"},
}

# ---------------------------------------------------------------------------
# A LISTA DE BUSCAS — adicione ou remova uma linha e pronto.
#
#   (jobName, destino, rótulo presencial)
#
#     jobName : termo buscado. None = todas as vagas, sem filtro de nome.
#     destino : "legal" -> vagas_legalizacao.json (aba "Legalização")
#               "geral" -> vagas_gerais.json      (aba "Vagas Gerais")
#     rótulo  : texto exibido no card e usado pelos filtros do dashboard.
#               A variante remota deriva dele trocando o sufixo:
#               "Societário" -> "Societário Remoto".
#
# A ORDEM É IMPORTANTE. A primeira busca que encontra uma vaga define o rótulo
# dela (as demais são ignoradas por deduplicação de ID), então a lista segue a
# ordem dos botões do dashboard: legalização primeiro, gerais depois. A busca
# ampla (jobName None) vem por último de propósito — ela é a rede de segurança
# que rotula as vagas que nenhum termo específico capturou.
#
# A API busca no título e ignora acento: "legalizacao" e "legalização"
# devolvem o mesmo conjunto, então basta um. Termos testados que hoje não
# devolvem nada ("junta comercial", "cnpj", "certidões", "despachante") ficaram
# de fora; "alvará" fica porque é o nome do cargo quando aparece.
# ---------------------------------------------------------------------------
BUSCAS = [
    # ---- Legalização: ordem dos botões Legalização > Societário > Paralegal > Licenças ----
    ("legalização", "legal", "Legalização"),
    ("abertura de empresas", "legal", "Legalização"),
    ("societário", "legal", "Societário"),
    ("paralegal", "legal", "Paralegal"),
    ("alvará", "legal", "Licenças"),
    ("licenciamento", "legal", "Licenças"),
    ("regularização", "legal", "Licenças"),
    # ---- Vagas Gerais: Assistente > Júnior > Auxiliar > Remoto > Presencial ----
    ("assistente", "geral", "Assistente Presencial"),
    ("jr", "geral", "Júnior"),
    ("Júnior", "geral", "Júnior"),
    ("auxiliar", "geral", "Auxiliar Presencial"),
    (None, "geral", "Geral Presencial"),
]

# Onde cada busca grava o resultado.
DESTINOS = {
    "legal": "vagas_legalizacao.json",
    "geral": "vagas_gerais.json",
}


@dataclass(frozen=True)
class Consulta:
    job_name: str | None
    modalidade: str
    destino: str
    rotulo_base: str

    @property
    def rotulo(self) -> str:
        """Campo `topic` do JSON — é por ele que o card e os filtros funcionam."""
        if self.modalidade == "Presencial":
            return self.rotulo_base
        return f"{self.rotulo_base.removesuffix(' Presencial')} Remoto"

    @property
    def rotulo_exibicao(self) -> str:
        """Como a consulta aparece no terminal: o termo buscado e o rótulo gravado.

        Sem isso o log repete "Desenvolvimento" cinco vezes — uma por busca
        (desenvolvedor, desenvolvimento, dev, software, devops) — e não dá para
        saber qual delas trouxe a vaga. Só afeta a exibição: o `topic` do JSON
        continua sendo `rotulo`.
        """
        busca = f'"{self.job_name}"' if self.job_name else "(busca ampla)"
        return f"{busca} → {self.rotulo}"

    @property
    def url(self) -> str:
        params = {"limit": LIMIT, "offset": 0, **MODALIDADES[self.modalidade]}
        if self.job_name:
            params["jobName"] = self.job_name
        return f"{BASE_URL}?{urlencode(params)}"


def gerar_consultas():
    """Gera uma consulta por (busca x modalidade)."""
    for job_name, destino, rotulo_base in BUSCAS:
        for modalidade in MODALIDADES:
            yield Consulta(job_name, modalidade, destino, rotulo_base)
