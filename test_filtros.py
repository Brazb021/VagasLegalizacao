"""Testa os dois filtros de descarte: cargo avançado e escopo de área.

    python3 -m unittest discover -s . -p 'test_filtros.py' -v

Os casos são títulos reais que apareceram no histórico (`data/`), não exemplos
inventados: a lista de áreas do filtro de escopo saiu deles, e um teste com
título inventado não pegaria o erro de digitação que a lista teve.
"""

import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "monitor"))

import common  # noqa: E402
import descricoes  # noqa: E402

PASTA_DADOS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")


class FiltroDeCargo(unittest.TestCase):
    """cargo_para_descartar: nível de cargo, no título."""

    def test_descarta_nivel_avancado(self):
        for titulo in (
            "Analista de Suporte Sênior",
            "Coordenador de Compras",
            "Supervisor de Operação",
            "Gerente de Loja",
            "Diretor de TI",
            "Especialista em Dados",
            "Desenvolvedor Pleno",
            "Analista de Dados PL",
        ):
            with self.subTest(titulo):
                self.assertTrue(descricoes.cargo_para_descartar(titulo))

    def test_mantem_nivel_de_entrada(self):
        for titulo in (
            "Analista de Suporte Jr",
            "Trainee de Suporte",
            "Aprendiz Administrativo",
            "Assistente de Suporte",
            "Auxiliar de Limpeza",
        ):
            with self.subTest(titulo):
                self.assertFalse(descricoes.cargo_para_descartar(titulo))

    def test_aceita_ambos_os_niveis(self):
        # A empresa admite entry level, então o cargo não é avançado.
        for titulo in ("Fullstack AI Engineer - (JR/PL)", "Advogado(a) Júnior/Pleno"):
            with self.subTest(titulo):
                self.assertFalse(descricoes.cargo_para_descartar(titulo))

    def test_pl_sql_nao_e_pleno(self):
        # "PL/SQL" é dialeto de banco, não nível de cargo.
        self.assertFalse(descricoes.cargo_para_descartar("Analista de Sistemas PL/SQL"))

    def test_area_de_coordenacao_nao_vira_cargo(self):
        # "Coordenação" aqui é onde a pessoa trabalha, não o que ela faz.
        for titulo in (
            "Assistente de Coordenação Pedagógica",
            "Auxiliar de Coordenação Infantil e fundamental I",
        ):
            with self.subTest(titulo):
                self.assertFalse(descricoes.cargo_para_descartar(titulo))

    def test_estagiario_no_feminino_e_entrada(self):
        # Regressão: `estagiario|estagio` não cobria "estagiária", e o feminino
        # entrava no corte de nível como se fosse "sênior".
        for titulo in ("Estagiária Sênior", "Estagiário Sênior", "Estagiaria Pleno"):
            with self.subTest(titulo):
                self.assertFalse(descricoes.cargo_para_descartar(titulo))

    def test_prefixo_pessoa_nao_quebra_o_cargo_de_entrada(self):
        # Regressão: a âncora `^` não casava depois de "Pessoa", e o cargo de
        # entrada era lido como se a pessoa fosse a下一代 responsável.
        for titulo in (
            "Pessoa Estagiária de Coordenação",
            "Pessoa Assistente de Coordenação",
            "Pessoa Auxiliar de Supervisão",
            "Pessoa Trainee de Gerência",
        ):
            with self.subTest(titulo):
                self.assertFalse(descricoes.cargo_para_descartar(titulo))

    def test_cargo_avancado_vence_prefixo_de_entrada(self):
        # O nível declarado manda mesmo em título de entrada.
        for titulo in ("Assistente Sr", "Operador de Produção Sênior", "Pessoa Assistente Sênior"):
            with self.subTest(titulo):
                self.assertTrue(descricoes.cargo_para_descartar(titulo))


class FiltroDeEscopo(unittest.TestCase):
    """estagio_fora_do_escopo: estágio de área que não é de tecnologia."""

    def test_descarta_estagio_de_area_nao_tech(self):
        for titulo in (
            "Estágio em Recursos Humanos | Gente e Gestão - SP",
            "Estágio em Jurídico",
            "Estágio de Pedagogia (TARDE)",
            "Pessoa Estagiária de Engenharia Civil – Obras | São Paulo - Zona Leste",
            "Estagiário(a) de Musculação - Seg a Sex 17h as 22h",
            "Estágio em SUPRIMENTOS (ADMINISTRAÇÃO, LOGÍSTICA) - ENOPS",
            "Estágio em FINANCEIRO (CIÊNCIAS CONTÁBEIS) - ENOPS",
            "Estágio - Compras e Não Revenda",
            "Estagiário de Remuneração e Benefícios",
            "ESTAGIARIO(A) DE OBRA - SANTO ANDRÉ",
        ):
            with self.subTest(titulo):
                self.assertTrue(descricoes.estagio_fora_do_escopo(titulo))

    def test_mantem_estagio_de_tecnologia(self):
        for titulo in (
            "Estágio em TI",
            "Estagiário(a) de TI - São Paulo",
            "ESTAGIÁRIO DE DESENVOLVIMENTO DE SOFTWARE - SÃO PAULO/SP",
            "Estágio em Desenvolvimento de Integrações | Consultoria em TI",
            "Estagiário(a) em Business Intelligence",
            "Estágio em Geoprocessamento 12571053M",
        ):
            with self.subTest(titulo):
                self.assertFalse(descricoes.estagio_fora_do_escopo(titulo))

    def test_tecnologia_no_titulo_vence_a_area(self):
        # Válvula de escape: "Suprimentos com SAP" é vaga de SAP, não de compras.
        # Descartar aqui seria o erro mais caro do filtro.
        for titulo in (
            "Estágio em Suprimentos com SAP",
            "Estagiário de Compras - SAP Business One",
            "Estágio em Jurídico com TI",
        ):
            with self.subTest(titulo):
                self.assertFalse(descricoes.estagio_fora_do_escopo(titulo))

    def test_administrativo_e_procurado(self):
        # Vaga de administrativo entra no escopo. A palavra NÃO está em
        # AREAS_FORA_DE_TECH de propósito.
        for titulo in (
            "ESTAGIARIO ADMINISTRATIVO | ITAIM BIBI, SP.",
            "Estagiária(o) em administração/Facilities",
            "Estagiário Administrativo de TI",
        ):
            with self.subTest(titulo):
                self.assertFalse(descricoes.estagio_fora_do_escopo(titulo))

    def test_administrativo_no_parente_ves_nao_salvou(self):
        # Regressão: "administração" aparece aqui só na lista de cursos
        # aceitos. A área de verdade vem antes do parêntese, e é por ela que a
        # vaga sai — se alguém reintroduzir o termo administrativo na lista,
        # estes quatro casos passam a depender da palavra errada.
        for titulo in (
            "Estágio em SUPRIMENTOS (ADMINISTRAÇÃO, LOGÍSTICA) - ENOPS",
            "Estágio em DEPARTAMENTO PESSOAL (ADMINISTRAÇÃO) - ENOPS",
            "Estágio em FINANCEIRO (ADMINISTRAÇÃO, ECONOMIA) - ENOPS",
            "Estágio em PRICING / COMÉRCIO EXTERIOR (COMÉRCIO EXTERIOR) - MSL",
        ):
            with self.subTest(titulo):
                self.assertTrue(descricoes.estagio_fora_do_escopo(titulo))

    def test_titulo_sem_area_fica(self):
        # O título não diz a área, e o filtro não adivinha: aparece para a
        # pessoa decidir, em vez de sumir sem ninguém ver.
        for titulo in ("Estagiário", "Estágio Universitário", "Programa de Estágio | Fast"):
            with self.subTest(titulo):
                self.assertFalse(descricoes.estagio_fora_do_escopo(titulo))

    def test_area_desconhecida_fica(self):
        # Uma área que ninguém catalogou passa. Errar para o lado de manter
        # custa um card; errar para o de descartar apaga a oportunidade.
        self.assertFalse(descricoes.estagio_fora_do_escopo("Estágio em Astrometria"))

    def test_nao_estagio_nao_entra_na_conta(self):
        # "Suporte" e "TI" são rótulos que o próprio filtro de cargo não pega
        # e que aqui não têm nada a ver: a área já vem do rótulo.
        for titulo in (
            "Analista de Suporte de Atendimento",
            "Analista de Tecnologia Júnior - Salesforce",
            "Técnico de Suporte JR - Noturno",
        ):
            with self.subTest(titulo):
                self.assertFalse(descricoes.estagio_fora_do_escopo(titulo))

    def test_aprendiz_tambem_e_estagio(self):
        self.assertTrue(descricoes.estagio_fora_do_escopo("Aprendiz de Jurídico"))


class FiltroDeLegalizacao(unittest.TestCase):
    """Escopo da aba "Legalização": tira advogado, estágio e licença de software."""

    def test_mantem_vagas_de_legalizacao(self):
        for titulo in (
            "Analista de Legalização Pleno",
            "Pessoa Analista Incorporação e Legalização Pleno",
            "Paralegal II - SP",
            "Analista Administrativo (Paralegal).",
            "Analista Jurídico – Societário, Compliance e Governança Corporativa",
            "Analista Planejamento Pleno | Licenciamento Empresarial | Corporativo São Paulo",
            "Analista de Onboarding (Abertura de Empresas)",
        ):
            with self.subTest(titulo=titulo):
                self.assertFalse(descricoes.legalizacao_fora_do_escopo(titulo))

    def test_descarta_o_que_nao_e_legalizacao(self):
        for titulo in (
            "Advogado(a) Pleno - Societário e Mercado de Capitais",
            "ESTAGIARIO EM ADVOCACIA - Societário e Governança Corporativa",
            "Estagiária(o) Societário",
            "Analista de Marca e Licenciamento",
            "Analista de Operações Cloud e Licenciamento",
            "Advogado(a) Sócio(a) de Serviço - Regulatório",
            "ESTAGIÁRIO(A) — FOLHA DE PAGAMENTO E PARALEGAL",
        ):
            with self.subTest(titulo=titulo):
                self.assertTrue(descricoes.legalizacao_fora_do_escopo(titulo))

    def test_legalizacao_no_titulo_vence(self):
        self.assertFalse(descricoes.legalizacao_fora_do_escopo("Advogado de Legalização Imobiliária"))


class VagaParaDescartar(unittest.TestCase):
    """A função que junta os filtros, como o chamador os usa."""

    def test_cargo_nao_roda_em_legalizacao(self):
        # A aba é para quem já tem experiência: pleno e sênior ficam.
        vaga = {"name": "Analista de Legalização Sênior"}
        self.assertEqual(common.vaga_para_descartar(vaga, destino="legal"), "")

    def test_motivo_do_escopo(self):
        vaga = {"name": "Advogado(a) Pleno - Societário"}
        self.assertEqual(
            common.vaga_para_descartar(vaga, destino="legal"),
            "fora da área de legalização",
        )

    def test_escopo_nao_roda_em_gerais(self):
        vaga = {"name": "Estágio em Jurídico"}
        self.assertEqual(common.vaga_para_descartar(vaga, destino="geral"), "")

    def test_cargo_roda_em_gerais(self):
        vaga = {"name": "Analista de Suporte Sênior"}
        self.assertEqual(common.vaga_para_descartar(vaga, destino="geral"), "cargo avançado")

    def test_titulo_ausente_nao_quebra(self):
        self.assertEqual(common.vaga_para_descartar({}, destino="legal"), "")


class LimpezaDoHistorico(unittest.TestCase):
    """A limpeza roda numa pasta temporária: `salvar_vagas_recentes` escreve no disco."""

    def _limpar(self, vagas, destino):
        with tempfile.TemporaryDirectory() as pasta:
            historico = os.path.join(pasta, "historico.json")
            with open(historico, "w", encoding="utf-8") as f:
                json.dump(vagas, f, ensure_ascii=False)
            common.salvar_vagas_recentes([], "Teste", historico, destino=destino)
            with open(historico, encoding="utf-8") as f:
                return [v["name"] for v in json.load(f)]

    def test_legalizacao_guarda_30_dias(self):
        from datetime import datetime, timedelta, timezone
        ha_20_dias = (datetime.now(timezone.utc) - timedelta(days=20)).isoformat()
        vagas = [{"id": "1", "name": "Analista de Legalização", "publishedDate": ha_20_dias}]
        self.assertEqual(self._limpar(vagas, "legal"), ["Analista de Legalização"])
        # Em "Vagas Gerais" a retenção continua de 7 dias.
        self.assertEqual(self._limpar(vagas, "geral"), [])

    def test_limpeza_tira_advogado_da_legalizacao(self):
        from datetime import datetime, timezone
        agora = datetime.now(timezone.utc).isoformat()
        vagas = [
            {"id": "1", "name": "Analista de Legalização", "publishedDate": agora},
            {"id": "2", "name": "Advogado Societário", "publishedDate": agora},
        ]
        self.assertEqual(self._limpar(vagas, "legal"), ["Analista de Legalização"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
