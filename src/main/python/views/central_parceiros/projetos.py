from webapp import db, cp, application
from models.table_projetos import Projetos
from models.table_arquivos import Arquivos
from models.table_cursos import Cursos
from models.table_links import Links
from models.table_palavras_chave import Palavras_chave
from models.table_relacao_projeto_arquivo import Rel_projeto_arquivo
from models.table_relacao_projeto_curso import Rel_projeto_curso
from models.table_relacao_projeto_parceiro import Rel_projeto_colaborador
from models.table_relacao_projeto_unidade import Rel_projeto_unidade
from models.table_relacao_projeto_categoria import Rel_projeto_categoria
from models.table_parceiros import Parceiros
from models.table_unidades import Unidades
from models.table_categorias_projeto import Categorias_projetos
from views.central_parceiros.login import token_required
from flask import request, jsonify
import os, datetime, json

@cp.route('/projetos', methods=['POST'])
@token_required
def post_projeto(current_user):
    data = json.loads(request.form['projeto'])

    projeto = Projetos(
        titulo = data['titulo'], 
        descricao = data['descricao'], 
        id_parceiro = current_user.id_geral, 
        premiado = data['premiado']
    )

    db.session.add(projeto)
    db.session.commit()

    unidades = data['unidades']
    for unidade in unidades:
        unidade = Unidades.query.filter_by(id = unidade).first()
        if not unidade:
            pass # TEM Q FAZER TRATAMENTO DE EXCESSÃO AQUI
        else:
            projetoUnidade = Rel_projeto_unidade(
                id_projeto = projeto.id, 
                id_unidade = unidade.id
            )
        
            db.session.add(projetoUnidade)
            db.session.commit()

    cursos = data['cursos']
    for curso in cursos:
        curso = Cursos.query.filter_by(id=curso).first()
        if not curso:
            pass # TEM Q FAZER TRATAMENTO DE EXCESSÃO AQUI
        else:
            projetoCurso = Rel_projeto_curso(
                id_projeto = projeto.id, 
                id_curso = curso.id
            )

            db.session.add(projetoCurso)
            db.session.commit()


    palavrasChave = data['palavrasChave']
    for palavra in palavrasChave:
        palavra = palavra.strip(" ")
        novaPalavra = Palavras_chave(
            id_projeto = projeto.id, 
            palavra = palavra
        )

        db.session.add(novaPalavra)
        db.session.commit()
 

    colaboradores = data['colaboradores']
    for colaborador in colaboradores:
        colaborador = colaborador.strip(" ")        
        colaborador = Parceiros.query.filter_by(email = colaborador).first()
        if not colaborador:
            pass # TEM Q FAZER TRATAMENTO DE EXCESSÃO AQUI
        else:
            projetoColaborador = Rel_projeto_colaborador(
                id_projeto = projeto.id, 
                id_colaborador = colaborador.id_geral
            )

            db.session.add(projetoColaborador)
            db.session.commit()
    
    if projeto.premiado == True:
        links = data['links']
        for link in links:
            link = link.strip(" ")
            link = Links(
                id_projeto = projeto.id, 
                url = link
            )

            db.session.add(link)
            db.session.commit()

    categorias = data['categorias']
    for categoria in categorias:
        projetoCategoria = Rel_projeto_categoria(
            id_projeto = projeto.id, 
            id_categoria = categoria['id']
        )

        db.session.add(projetoCategoria)
        db.session.commit()

    dadosArquivos = data['arquivos']
    for dado in dadosArquivos:
        nomeArquivo = dado['nomeMidia']
        extensao = nomeArquivo.split(".")[1]
        novoNome = str(hash('{}{}{}'.format(current_user.id_geral, str(datetime.datetime.now()), nomeArquivo))) + "." + extensao
        arquivo = request.files[dado['nomeMidia']]
        arquivo.filename = novoNome
        dado['nomeMidia'] = novoNome 

        arquivo.save(os.path.join(app.config['UPLOAD_FOLDER'], arquivo.filename))

        infoArquivo = Arquivos(
            midia = dado['nomeMidia'], 
            titulo = dado['titulo'], 
            descricao = dado['descricao'], 
            codigo = dado['codigo'], 
            id_parceiro = current_user.id_geral
        )

        db.session.add(infoArquivo)
        db.session.commit()

        projetoArquivo = Rel_projeto_arquivo(
            id_projeto = projeto.id, 
            id_arquivo = infoArquivo.id
        )

        db.session.add(projetoArquivo)
        db.session.commit()

    return jsonify({'Mensagem': 'Cadastrado com sucesso!'})

@cp.route('/projetos', methods=['GET'])
@token_required
def get_projetos(current_user):
    dados = Projetos.query.all()

    projetos = []

    for dado in dados:
        projeto = {}
        projeto['id'] = dado.id
        projeto['titulo'] = dado.titulo
        projeto['descricao'] = dado.descricao

        projetos.append(projeto)

    return jsonify(projetos)

@cp.route('/projetos/<int:id>', methods=['GET'])
@token_required
def get_projeto(current_user, id):
    dados = Projetos.query.filter_by(id = id).first()

    if not dados:
        return jsonify({'Mensagem': 'Projeto não encontrado!'})
    
    projeto = {}
    projeto['titulo'] = dados.titulo
    projeto['descricao'] = dados.descricao

    # PARCEIRO
    parceiro = Parceiros.query.filter_by(id_geral = dados.id_parceiro).first()
    if parceiro is not None:
        projeto['id_parceiro'] = parceiro.id_geral
        projeto['nome_parceiro'] = "{} {}".format(parceiro.nome, parceiro.sobrenome)

    # UNIDADES
    idUnidadesRelacionadas = Rel_projeto_unidade.query.filter_by(id_projeto = dados.id).all()
    unidades = []
    for relacao in idUnidadesRelacionadas:
        unidade = Unidades.query.filter_by(id = relacao.id_unidade).first()
        infosUnidade = {}
        infosUnidade['id'] = unidade.id
        infosUnidade['nome'] = unidade.nome
        infosUnidade['cidade'] = unidade.cidade

        unidades.append(infosUnidade)
    
    projeto['unidades'] = unidades

    # CURSOS
    idCursosRelacionados = Rel_projeto_curso.query.filter_by(id_projeto = dados.id).all()
    cursos = []
    for relacao in idCursosRelacionados:
        curso = Cursos.query.filter_by(id = relacao.id_curso).first()
        infosCurso = {}
        infosCurso['id'] = curso.id
        infosCurso['nome'] = curso.nome

        cursos.append(infosCurso)
    
    projeto['cursos'] = cursos

    # PALAVRAS-CHAVE
    listaPalavras = Palavras_chave.query.filter_by(id_projeto = dados.id).all()
    palavrasChave = []
    for item in listaPalavras:
        infosPalavra = {}
        infosPalavra['palavra'] = item.palavra

        palavrasChave.append(infosPalavra)
    
    projeto['palavras-chave'] = palavrasChave

    # COLABORADORES
    idColaboradoresRelacionados = Rel_projeto_colaborador.query.filter_by(id_projeto = dados.id).all()
    colaboradores = []
    for relacao in idColaboradoresRelacionados:
        colaborador = Parceiros.query.filter_by(id_geral = relacao.id_colaborador).first()
        infosColaborador = {}
        infosColaborador['id'] = id
        infosColaborador['nome'] = "{} {}".format(colaborador.nome, colaborador.sobrenome)
        infosColaborador['email'] = colaborador.email

        colaboradores.append(infosColaborador)

    projeto['colaboradores'] = colaboradores

    # ARQUIVOS
    idArquivosRelacionados = Rel_projeto_arquivo.query.filter_by(id_projeto = dados.id).all()
    arquivos = []
    for relacao in idArquivosRelacionados:
        arquivo = Arquivos.query.filter_by(id = relacao.id_arquivo).first()
        infosArquivo = {}
        infosArquivo['midia'] = arquivo.midia
        infosArquivo['titulo'] = arquivo.titulo
        infosArquivo['descricao'] = arquivo.descricao
        infosArquivo['codigo'] = arquivo.codigo

        arquivos.append(infosArquivo)

    projeto['arquivos'] = arquivos

    # PREMIADO
    projeto['premiado'] = dados.premiado
    links = []
    if dados.premiado == True:
        linksRelacionados = Links.query.filter_by(id_projeto = dados.id).all()
        for link in linksRelacionados:
            infosLink = {}
            infosLink['URL'] = link.url

            links.append(infosLink)

    projeto['links'] = links

    # CATEGORIAS
    idCategoriasRelacionadas = Rel_projeto_categoria.query.filter_by(id_projeto = dados.id).all()
    categorias = []
    for relacao in idCategoriasRelacionadas:
        dadosCategoria = Categorias_projetos.query.filter_by(id = relacao.id_categoria).first()
        infosCategoria = {}
        infosCategoria['id'] = dadosCategoria.id
        infosCategoria['nome'] = dadosCategoria.categoria

    return jsonify(projeto)

# ====================================================================
@cp.route('/projetos/categorias', methods=['GET'])
@token_required
def get_categorias(current_user):
    dadosCategorias = Categorias_projetos.query.all()

    listaCategorias = []
    for dado in dadosCategorias:
        categoria = {}
        categoria['id'] = dado.id
        categoria['nome'] = dado.categoria

        listaCategorias.append(categoria)
    
    return jsonify(listaCategorias)