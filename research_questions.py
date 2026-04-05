"""
research_questions.py
Define todas as categorias de pesquisa, ficheiros de destino e perguntas.
As perguntas devem corresponder EXACTAMENTE ao texto em backlog.md para que
o researcher.py possa marcar os checkboxes correctamente.
"""

CATEGORIES = {
    "identidade_territorio": {
        "file": "identidade_territorio.md",
        "title": "Identidade e Território",
        "projectplan_label": "Identidade e Território",
        "questions": [
            "Qual a origem e evolução do nome \"Mafamude\" — étimo árabe, formas medievais documentadas?",
            "Quais são as fronteiras geográficas actuais de Mafamude e como evoluíram historicamente?",
            "Qual o papel do Rio Douro na identidade histórica e quotidiana de Mafamude?",
            "Quais são o brasão, símbolos oficiais e lema da freguesia de Mafamude?",
            "Como evoluiu a organização administrativa de Mafamude desde 1834 até à união de freguesias?",
        ],
    },
    "historia": {
        "file": "historia.md",
        "title": "História",
        "projectplan_label": "História",
        "questions": [
            "Quais são as evidências documentais da presença árabe ou muçulmana em Mafamude (séc. X–XIII)?",
            "Como se desenvolveu Mafamude no período medieval (séc. XIII–XV) — documentos, propriedades, senhorios?",
            "Qual foi o papel da Igreja de São Cristóvão na história de Mafamude desde a sua fundação?",
            "Como era Mafamude nos séculos XVII e XVIII — economia, população, estrutura social?",
            "Que impacto teve a industrialização do séc. XIX e início do séc. XX em Mafamude?",
            "Que acontecimentos históricos marcantes (guerras, epidemias, cheias, conflitos) afectaram Mafamude?",
            "Como se transformou Mafamude ao longo do séc. XX — urbanização, crescimento populacional, mudanças?",
            "Que relação histórica existe entre Mafamude e Vila Nova de Gaia enquanto sede de município?",
        ],
    },
    "pessoas_notaveis": {
        "file": "pessoas_notaveis.md",
        "title": "Pessoas Notáveis",
        "projectplan_label": "Pessoas Notáveis",
        "questions": [
            "Que artistas, escritores ou intelectuais nasceram ou viveram em Mafamude?",
            "Que figuras políticas ou religiosas estão historicamente associadas a Mafamude?",
            "Que desportistas notáveis são naturais ou estão associados a Mafamude?",
            "Que personalidades populares, folclóricas ou lendárias fazem parte da memória colectiva de Mafamude?",
            "Qual a ligação de Soares dos Reis a Mafamude e a Vila Nova de Gaia?",
            "Que figuras locais do séc. XX marcaram a vida social, cultural ou económica de Mafamude?",
        ],
    },
    "lugares_patrimonio": {
        "file": "lugares_patrimonio.md",
        "title": "Lugares e Património",
        "projectplan_label": "Lugares e Património",
        "questions": [
            "Qual é a história completa da Igreja de São Cristóvão de Mafamude — construção, obras, espólio artístico?",
            "Que edifícios históricos, solares ou quintas existiram ou existem em Mafamude?",
            "Que parques, jardins ou espaços públicos históricos existem em Mafamude?",
            "Que mercados, feiras ou espaços de comércio tradicional marcaram a vida de Mafamude?",
            "Que locais históricos de Mafamude foram demolidos ou transformados ao longo do séc. XX?",
            "O que revelam os nomes das ruas de Mafamude sobre a história e identidade local?",
            "Que elementos do património imaterial (saberes, ofícios, práticas) estão associados a Mafamude?",
        ],
    },
    "gastronomia": {
        "file": "gastronomia.md",
        "title": "Gastronomia",
        "projectplan_label": "Gastronomia",
        "questions": [
            "Quais são os pratos típicos e tradicionais da zona de Mafamude e da orla ribeirinha de Gaia?",
            "Que doces, pães ou confeitaria são ou foram tradicionais em Mafamude?",
            "Que tascas, cafés, tabernas ou restaurantes históricos existiram ou existem em Mafamude?",
            "Que produtos locais — peixe do Douro, vinho de Gaia, hortícolas — estão associados à gastronomia de Mafamude?",
            "Que festas ou feiras gastronómicas acontecem ou aconteceram em Mafamude?",
        ],
    },
    "festas_tradicoes": {
        "file": "festas_tradicoes.md",
        "title": "Festas e Tradições",
        "projectplan_label": "Festas e Tradições",
        "questions": [
            "Como se celebra ou celebrava a Festa de São Cristóvão (padroeiro) em Mafamude — história e rituais?",
            "Como era o São João em Mafamude — tradições específicas, arraiais, fogueiras, costumes locais?",
            "Que romarias, procissões ou festas religiosas marcavam o calendário de Mafamude?",
            "Que tradições populares (cantigas, jogos, costumes sazonais) existiam em Mafamude?",
            "Que tradições de Mafamude já desapareceram ao longo do séc. XX?",
            "Que festas de bairro ou eventos comunitários existem actualmente em Mafamude?",
        ],
    },
    "associacoes_colectividades": {
        "file": "associacoes_colectividades.md",
        "title": "Associações e Colectividades",
        "projectplan_label": "Associações e Colectividades",
        "questions": [
            "Que clubes desportivos existem ou existiram em Mafamude — história, fundação, modalidades?",
            "Que associações culturais, recreativas ou filarmónicas marcaram a vida de Mafamude?",
            "Que grupos de teatro, ranchos folclóricos ou grupos corais existem ou existiram em Mafamude?",
            "Que movimentos de moradores, associações de bairro ou organizações cívicas actuaram em Mafamude?",
            "Que colectividades de Mafamude participam ou participaram nas marchas de São João?",
        ],
    },
    "arte_cultura": {
        "file": "arte_cultura.md",
        "title": "Arte e Cultura",
        "projectplan_label": "Arte e Cultura",
        "questions": [
            "Que artistas plásticos nasceram, viveram ou trabalharam em Mafamude?",
            "Que escritores, poetas ou jornalistas estão associados a Mafamude?",
            "Que músicos, bandas ou grupos musicais são originários de Mafamude?",
            "Que murais, esculturas ou arte urbana existem no espaço público de Mafamude?",
            "Que espólio fotográfico histórico existe sobre Mafamude — arquivo, colecções, fontes?",
        ],
    },
    "lendas_historias": {
        "file": "lendas_historias.md",
        "title": "Lendas e Histórias Populares",
        "projectplan_label": "Lendas e Histórias Populares",
        "questions": [
            "Que lendas locais existem em Mafamude — sobre o rio, a igreja, lugares ou personagens?",
            "Que histórias de bairro ou memórias colectivas são transmitidas oralmente em Mafamude?",
            "Que personagens populares, excêntricos ou pitorescos fazem parte da memória de Mafamude?",
            "Que acontecimentos insólitos, crimes famosos ou episódios marcantes fazem parte do folclore de Mafamude?",
            "Que superstições, crenças ou práticas populares estavam associadas à vida em Mafamude?",
        ],
    },
    "arquitetura_urbanismo": {
        "file": "arquitetura_urbanismo.md",
        "title": "Arquitectura e Urbanismo",
        "projectplan_label": "Arquitectura e Urbanismo",
        "questions": [
            "Que estilos arquitectónicos predominam em Mafamude e que exemplos notáveis existem?",
            "Que casas típicas, villas, quintas ou solares são representativos da arquitectura de Mafamude?",
            "Como se transformou o tecido urbano de Mafamude ao longo do séc. XX — bairros, demolições, expansão?",
            "Que bairros históricos ou zonas com identidade própria existem dentro de Mafamude?",
            "Como se manifesta a tensão entre o rural e o urbano na arquitectura e urbanismo de Mafamude?",
        ],
    },
    "economia_trabalho": {
        "file": "economia_trabalho.md",
        "title": "Economia e Trabalho",
        "projectplan_label": "Economia e Trabalho",
        "questions": [
            "Que profissões históricas eram dominantes em Mafamude — pescadores, barqueiros, operários, agricultores?",
            "Que indústrias, fábricas ou armazéns existiram em Mafamude ao longo da história?",
            "Que comércio tradicional ainda existe ou existiu em Mafamude?",
            "Como afectou a proximidade ao Porto a economia e os hábitos de trabalho de Mafamude?",
            "Como evoluiu a estrutura económica de Mafamude do séc. XIX até hoje?",
        ],
    },
    "religiao": {
        "file": "religiao.md",
        "title": "Religião e Espiritualidade",
        "projectplan_label": "Religião e Espiritualidade",
        "questions": [
            "Qual é a história completa da Paróquia de São Cristóvão de Mafamude — fundação, párocos notáveis, momentos marcantes?",
            "Que outras capelas, cruzeiros ou locais de devoção existem ou existiram em Mafamude?",
            "Que irmandades, confrarias ou associações religiosas actuaram em Mafamude ao longo da história?",
            "Que santos, devoções ou cultos populares são específicos de Mafamude?",
            "Qual foi o papel da Igreja na vida social e cultural de Mafamude nos sécs. XIX e XX?",
            "Como se manifesta a religiosidade popular em Mafamude hoje — práticas, festas, devoções?",
        ],
    },
    "desporto": {
        "file": "desporto.md",
        "title": "Desporto",
        "projectplan_label": "Desporto",
        "questions": [
            "Que clubes de futebol existem ou existiram em Mafamude — história, fundação, conquistas?",
            "Que desportistas notáveis são naturais ou estão associados a Mafamude?",
            "Que instalações desportivas históricas existiram ou existem em Mafamude?",
            "Que outras modalidades desportivas têm tradição em Mafamude para além do futebol?",
        ],
    },
    "marchas_sao_joao": {
        "file": "marchas_sao_joao.md",
        "title": "Marchas e São João",
        "projectplan_label": "Marchas e São João",
        "questions": [
            "Qual é o histórico completo de participações de Mafamude no concurso de Marchas de São João de Gaia?",
            "Em que anos Mafamude ganhou ou foi premiada no concurso de marchas?",
            "Que colectividades ou grupos organizaram as marchas de Mafamude ao longo dos anos?",
            "Que temas, letras ou conceitos criativos foram usados em edições anteriores das marchas de Mafamude?",
            "Qual é o formato e critérios do concurso Marchas de São João de Vila Nova de Gaia?",
            "Como se compara o concurso de Gaia com as Marchas de Santo António de Lisboa em termos de formato e tradição?",
        ],
    },
    "relacao_gaia": {
        "file": "relacao_gaia.md",
        "title": "Relação com Vila Nova de Gaia",
        "projectplan_label": "Relação com Vila Nova de Gaia",
        "questions": [
            "Qual é a posição e o peso de Mafamude no contexto do município de Vila Nova de Gaia?",
            "Que relação histórica e administrativa existe entre Mafamude e a Câmara Municipal de Gaia?",
            "O que distingue Mafamude das outras freguesias de Vila Nova de Gaia em termos de identidade e características?",
            "Como é que a fronteira entre Mafamude/Gaia e o Porto se manifesta na identidade local?",
        ],
    },
}
