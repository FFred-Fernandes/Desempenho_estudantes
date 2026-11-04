import re
from repositories.estudante_repository import EstudanteRepository
from entities.models import Estudante

class EstudanteService:
    @staticmethod
    def validar_cpf(cpf):
        cpf_limpo = re.sub(r'\D', '', str(cpf or ''))
        if len(cpf_limpo) != 11:
            return False, "O CPF deve conter exatamente 11 dígitos numéricos."
        if cpf_limpo == cpf_limpo[0] * 11:
            return False, "CPF inválido: não são permitidos dígitos repetidos (ex: 00000000000, 11111111111)."
        return True, cpf_limpo

    @staticmethod
    def validar_nome(nome):
        nome_str = str(nome or '').strip()
        if not nome_str:
            return False, "O nome não pode estar em branco."
        if not re.match(r'^[A-Za-zÀ-ÖØ-öø-ÿ\s]+$', nome_str):
            return False, "O nome do estudante deve conter apenas letras e espaços (sem números ou caracteres especiais)."
        return True, nome_str

    @staticmethod
    def criar_estudante(dados):
        # PARTE 3: Operação de cadastro (POST)
        nome = dados.get('nome')
        cpf = dados.get('cpf')
        matricula = str(dados.get('matricula', '')).strip()

        valido_nome, res_nome = EstudanteService.validar_nome(nome)
        if not valido_nome:
            return {"erro": res_nome}, 400

        valido_cpf, res_cpf = EstudanteService.validar_cpf(cpf)
        if not valido_cpf:
            return {"erro": res_cpf}, 400

        cpf_formatado = f"{res_cpf[:3]}.{res_cpf[3:6]}.{res_cpf[6:9]}-{res_cpf[9:]}"

        # REGRA 3: Prevenção de Duplicidade - Identificação única do estudante por CPF ou Matrícula
        if EstudanteRepository.buscar_por_cpf(cpf_formatado) or EstudanteRepository.buscar_por_cpf(res_cpf):
            return {"erro": "R3: CPF já cadastrado no sistema."}, 400

        if matricula and EstudanteRepository.buscar_por_matricula(matricula):
            return {"erro": "R3: Matrícula já cadastrada no sistema."}, 400
        
        novo_estudante = Estudante(
            nome=res_nome,
            cpf=cpf_formatado,
            matricula=matricula
        )
        salvo = EstudanteRepository.salvar(novo_estudante)
        return {"mensagem": "Estudante criado com sucesso!", "id": salvo.id}, 201

    @staticmethod
    def listar_estudantes():
        # PARTE 3: Operação de seleção geral (GET)
        # REGRA 8: Retorna os estudantes com a flag 'ativo' para auditoria de exclusão lógica
        estudantes = EstudanteRepository.buscar_todos()
        lista = [
            {
                "id": e.id,
                "nome": e.nome,
                "cpf": e.cpf,
                "matricula": e.matricula,
                "status": e.status,
                "ativo": e.ativo
            }
            for e in estudantes
        ]
        return lista, 200

    @staticmethod
    def buscar_estudante_por_id(id):
        # PARTE 3: Operação de seleção individual (GET por ID)
        estudante = EstudanteRepository.buscar_por_id(id)
        if not estudante or not estudante.ativo:
            return {"erro": "Estudante não encontrado ou inativo."}, 404
        return {
            "id": estudante.id,
            "nome": estudante.nome,
            "cpf": estudante.cpf,
            "matricula": estudante.matricula,
            "status": estudante.status,
            "ativo": estudante.ativo
        }, 200

    @staticmethod
    def atualizar_estudante(id, dados):
        # PARTE 3: Operação de edição (PUT)
        estudante = EstudanteRepository.buscar_por_id(id)
        if not estudante:
            return {"erro": "Estudante não encontrado."}, 404
        
        if 'nome' in dados:
            valido_nome, res_nome = EstudanteService.validar_nome(dados.get('nome'))
            if not valido_nome:
                return {"erro": res_nome}, 400
            estudante.nome = res_nome
        
        # REGRA 10: Proteção de Avaliação.
        # Atualização para 'Evasão' ou 'Trancado' impedirá novas notas e cálculos estatísticos.
        estudante.status = dados.get('status', estudante.status)
        
        EstudanteRepository.atualizar()
        return {"mensagem": "Estudante atualizado com sucesso!"}, 200

    @staticmethod
    def deletar_estudante(id):
        # PARTE 3: Operação de exclusão (DELETE)
        estudante = EstudanteRepository.buscar_por_id(id)
        if not estudante:
            return {"erro": "Estudante não encontrado."}, 404
        
        # REGRA 8: Integridade Histórica.
        # Não remove fisicamente do banco de dados para preservar histórico e avaliações.
        EstudanteRepository.inativar(estudante)
        return {"mensagem": "R8: Estudante inativado (exclusão lógica) com sucesso."}, 200
