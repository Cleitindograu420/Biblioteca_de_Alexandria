#todos os imports necessarios
from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from .models import Usuario,Evento, Inscrito, Certificado, Log
from django.core.validators import RegexValidator, EmailValidator
from django.core.exceptions import ValidationError
from django.contrib import messages
from datetime import datetime
from django.db import transaction


#funcao para renderizar a pagina home
def base(request):
    usuario_id = request.session.get("usuario_id")

    if not usuario_id:
        #teste em front 
        return redirect("login")
    
    usuario = get_object_or_404(Usuario, id_usuario=usuario_id)

     # redireciona conforme o tipo
    if usuario.tipo == "organizador":
        return render(request, "base_org.html", {"usuario": usuario})
    else:
        return render(request, "home.html", {"usuario": usuario})
    
#Funcoes para usuarios--------------------------------------------------------------------------------------------------

#funcao para deletar usuario de acordo com o id
def delete_user(request):
    #esse trecho se repete em quase todas as funcoes, ele pega o id do usuario que ta logado na sessao e se n tiver ninguem logado redireciona pra tela de login
    usuario_id = request.session.get('usuario_id')

    if not usuario:
        return redirect('login')
    #------------------------------------------------------------------------------------------------------------------
    #se o metodo for get, ele pega o usuario com o id que ta na sessao e renderiza a pagina de deletar usuario
    if request.method == 'GET':
       usuario = get_object_or_404(Usuario, id_usuario = usuario_id)
       return render(request, 'usuarios/delete_usuario.html', {'usuario': usuario})
    
    #se o metodo for post, ele pega o usuario com o id que ta na sessao e verifica se a senha inserida no formulario bate com a senha do usuario
    if request.method == 'POST':
        usuario = get_object_or_404(Usuario, id_usuario = usuario_id)
        senha = request.POST.get('senha') 
        
        #se a senha n bater, ele retorna uma mensagem de erro
        if usuario.senha != senha:
            return HttpResponse('Senha incorreta. Tente novamente.')
        
        usuario.delete()
        return redirect('login')

def cadastro_usuario(request):
    usuario_id = request.session.get('usuario_id')
    if request.method == 'POST':
        nome = request.POST.get('nome')
        telefone = request.POST.get('telefone')
        instEnsino = request.POST.get('instEnsino')
        email = request.POST.get('email')
        tipo = request.POST.get('tipo', '').lower()

        senha = request.POST.get('senha')
        token_acesso = request.POST.get('token_acesso')

        # token pré-definido
        TOKEN_CORRETO = "ORG123"

        # VALIDADORES
        telefone_valido = RegexValidator(
            regex=r'^\(?\d{2}\)? ?\d{4,5}-\d{4}$',
            message="O telefone deve estar no formato (XX) XXXXX-XXXX ou XX XXXXX-XXXX."
        )

        senha_valida = RegexValidator(
            regex=r'^(?=.*[A-Za-z])(?=.*\d)(?=.*[^A-Za-z0-9]).{8,}$',
            message="A senha deve ter no mínimo 8 caracteres, incluindo letras, números e caracteres especiais."
        )

        email_valido = EmailValidator(message="O email fornecido é inválido.")

        try:
            # ------ VALIDAÇÕES BÁSICAS ------
            telefone_valido(telefone)
            email_valido(email)
            senha_valida(senha)

            # ------ ORGANIZADOR ------
            if tipo == "organizador":
                if not token_acesso:
                    return HttpResponse("Token obrigatório para organizadores.")

                if token_acesso != TOKEN_CORRETO:
                    return HttpResponse("Token inválido!")

            # ------ BANCO ------
            if Usuario.objects.filter(telefone=telefone).exists():
                return HttpResponse("Telefone já cadastrado.")

            if Usuario.objects.filter(email=email).exists():
                return HttpResponse("Email já cadastrado.")

            # ------ CRIA USUÁRIO ------
            novo_usuario = Usuario.objects.create(
                nome=nome,
                telefone=telefone,
                instEnsino=instEnsino,
                senha=senha,
                email=email,
                tipo=tipo,
                token_acesso=token_acesso if tipo == "organizador" else None,
            )

            Log.objects.create(
                usuario_id=novo_usuario,
                acao=f"Novo usuário cadastrado: {nome} ({email})"
            )
            return redirect('login')

        except ValidationError as e:
            return HttpResponse(f"Erro: {e}")

    return render(request, 'funcoes.html', {'usuarios': Usuario.objects.all()})

def ver_usuario(request):
    usuario_id = request.session.get('usuario_id')

    if not usuario_id:
        return redirect('login')
    
    try:
        usuario = get_object_or_404(Usuario, id_usuario=usuario_id)

    except Usuario.DoesNotExist:
        return HttpResponse('Usuário não encontrado.')
    
    #se o usuario n for organizador, redireciona ele para a pagina de inscricoes, apenas organizadores podem ver a lista de usuarios
    if usuario.tipo != 'organizador':
        return redirect('inscricao_eventos')
    
    usuario = { 'usuarios': Usuario.objects.all(), }

    return render(request, "templates_org/usuarios_org.html", {'usuarios': Usuario.objects.all()}) 

def login_user(request):
    #se o metodo for post, ele pega as informacoes do formulario e valida elas
    if request.method == 'POST':
        email = request.POST.get('email')
        senha = request.POST.get('senha')

        #verifica se o email e a senha foram preenchidos
        try:
            if not email or not senha:
                return HttpResponse('Por favor, preencha todos os campos.')
            
            #pega o usuario com o email e senha inseridos no formulario
            user = Usuario.objects.get(email=email, senha=senha)

            #se o usuario for encontrado, cria uma sessao com o id do usuario e redireciona para a pagina de inscricoes
            if user:
                request.session['usuario_id'] = user.id_usuario
                return redirect('home_page')
            
            #caso o usuario n seja encontrado, retorna uma mensagem de erro
            else:
                return HttpResponse('Email ou senha incorretos. Tente novamente.')
        
        #caso o usuario n seja encontrado, retorna uma mensagem de erro
        except Usuario.DoesNotExist:
            return HttpResponse('Email ou senha incorretos. Tente novamente.')
    
    #se o metodo for get, ele renderiza a pagina de login
    return render(request, 'login.html')

def editar_usuario(request):
    usuario_id = request.session.get("usuario_id")
    
    if not usuario_id:
        redirect("login")
    
    usuario = get_object_or_404(Usuario, id_usuario = usuario_id)
    
    if request.method == "POST":
        nome = request.POST.get("nome")
        senha = request.POST.get("senha")
        telefone = request.POST.get("telefone")
        email = request.POST.get("email")
        tipo = request.POST.get('tipo')
        
        # Validação para verificar se o telefone e email já estão cadastrados por outro usuário
        if Usuario.objects.filter(telefone = telefone).exclude(id_usuario = usuario_id).exists():
            return HttpResponse("Este telefone já está cadastrado por outro usuário")
        
        if Usuario.objects.filter(email = email).exclude(id_usuario = usuario_id).exists():
            return HttpResponse("Este email já está cadastrado por outro usuário")

        # Validação para verificar se o telefone e email estão em um formato válido
        ##valida o telefone com regex
        telefone_valido = RegexValidator(
            regex=r'^\(?\d{2}\)? ?\d{4,5}-\d{4}$',
            message="O telefone deve estar no formato (XX) XXXXX-XXXX ou XX XXXXX-XXXX."
        )
        email_valido = EmailValidator(message="O email fornecido é inválido.")

        #se o telefone ou email forem invalidos, retorna uma mensagem de erro
        try:
            telefone_valido(telefone)
            email_valido(email)
        
        except ValidationError:
            return HttpResponse("Telefone ou email inválido. Por favor, insira um telefone ou email válido.")
        
        # Caso as informações sejam inseridas corretamente, as mudanças são salvas
        usuario.nome = nome
        usuario.senha = senha
        usuario.telefone = telefone
        usuario.email = email
        usuario.tipo = tipo
        usuario.save()
        
        # Redireciona o usuário para a página de inscrição após a edição
        return redirect("inscricao_eventos")

        
    # Renderiza a página de edição com os dados do usuário atual
    if usuario.tipo == 'organizador':
        return render(request, "templates_org/editar_user_org.html", {"usuario" : usuario})
    else:
        return render(request, "editar_user.html", {"usuario" : usuario})
#Funcoes para eventos--------------------------------------------------------------------------------------------------

def todos_eventos(request):
    usuario_id = request.session.get("usuario_id")
    
    if not usuario_id:
        return redirect("login")
      
    try:
        usuario = get_object_or_404(Usuario, id_usuario = usuario_id)
    
    except Usuario.DoesNotExist:
        return HttpResponse("Usuário não foi encontrado.")
    
    #se o usuario n for organizador, redireciona ele para a pagina de inscricoes, apenas organizadores podem ver a lista de eventos
    if usuario.tipo != "organizador":
        return redirect("inscricao_eventos")
    
    # Renderiza a página com todos os eventos
    eventos = {
        'eventos' : Evento.objects.all()
    }
    
    return render(request, "templates_org/list_eventos_org.html", eventos)

def cadastro_eventos(request):
    from datetime import datetime
    usuario_id = request.session.get("usuario_id")
    organizador = Usuario.objects.get(id_usuario=usuario_id)

    
    if not usuario_id:
        return redirect("login")
      
    try:
        usuario = get_object_or_404(Usuario, id_usuario = usuario_id)
    
    except Usuario.DoesNotExist:
        return HttpResponse("Usuário não foi encontrado.")
    
    #se o usuario n for organizador, redireciona ele para a pagina de inscricoes, apenas organizadores podem deletar eventos
    if usuario.tipo != "organizador":
        return redirect("inscricao")
    
    if request.method == "POST":
        dia_inicio_date = request.POST.get("dataIni")
        dia_fim_date = request.POST.get("dataFin")

        if not dia_inicio_date or not dia_fim_date:
            return HttpResponse("O campo data de início e final são obrigatórios")

        try:
            dia_inicio = datetime.strptime(dia_inicio_date, "%Y-%m-%d").date()
            dia_fim = datetime.strptime(dia_fim_date, "%Y-%m-%d").date()
        except ValueError:
            return HttpResponse("O campo data de início e final devem ser uma data válida")


        novo_evento = Evento(
            nome=request.POST.get("nome"),
            tipoEvento=request.POST.get("tipoEvento"),  
            dataIni=dia_inicio,
            dataFin=dia_fim,
            horasIni=request.POST.get("horasIni"),
            horasFin=request.POST.get("horasFin"),
            horasDura=request.POST.get("horasDura"),
            local=request.POST.get("local"),
            organizador=organizador,
            vagas=request.POST.get("vagas"),
        )
        

        novo_evento.save()

        Log.objects.create(
            id_evento=novo_evento,
            acao=f"Novo evento cadastrado: {novo_evento.nome}"
            )
        

        return redirect("eventos")

    # Se for GET, apenas exibe o formulário
    return render(request, 'templates_org/cad_eventos_org.html', {"organizadores": Usuario.objects.filter(tipo="organizador",), "professor": Usuario.objects.filter(tipo="professor")})

def verificacao_org(request):
    usuario_id = request.session.get("usuario_id")
    
    if not usuario_id:
        return redirect("login")
      
    try:
        usuario = get_object_or_404(Usuario, id_usuario = usuario_id)
    
    except Usuario.DoesNotExist:
        return HttpResponse("Usuário não foi encontrado.")
    
    #se o usuario n for organizador, redireciona ele para a pagina de eventos, apenas organizadores podem ver a lista de eventos
    if usuario.tipo != "organizador":
        return redirect("inscricao")
    
    return render(request, "usuarios/eventos.html", {"usuarios" : usuario})

def deletar_evento(request, pk):
    usuario_id = request.session.get("usuario_id")
    
    if not usuario_id:
        return redirect("login")
      
    try:
        usuario = get_object_or_404(Usuario, id_usuario = usuario_id)
    
    except Usuario.DoesNotExist:
        return HttpResponse("Usuário não foi encontrado.")
    
    #se o usuario n for organizador, redireciona ele para a pagina de inscricoes, apenas organizadores podem deletar eventos
    if usuario.tipo != "organizador":
        return redirect("inscricao")
    
    #pega o evento com o id passado na url e o deleta
    evento = get_object_or_404(Evento, pk = pk)
    
    # garante atomicidade entre criação do log e exclusão do evento
    with transaction.atomic():
        Log.objects.create(
            id_evento=evento,
            acao=f"Evento deletado: {evento.nome}"
        )

        evento.delete()

    return redirect("eventos")

def editar_evento(request, pk):
    organizador_id = request.session.get("organizador")
    usuario_id = request.session.get("usuario_id")
    
    organizador_obj = get_object_or_404(Usuario, id_usuario=organizador_id)
    organizador_nome = organizador_obj.nome
    
    if not usuario_id:
        return redirect("login")
      
    try:
        usuario = get_object_or_404(Usuario, id_usuario = usuario_id)
    except Usuario.DoesNotExist:
        return HttpResponse("Usuário não foi encontrado.")
    
    if usuario.tipo != "organizador":
        return redirect("inscricao")

    evento = get_object_or_404(Evento, pk = pk)

    context = {
        "evento": evento,
        "organizadores": Usuario.objects.filter(tipo="organizador"),
        "professor": Usuario.objects.filter(tipo="professor"),
    }
    
    if request.method == "POST":
        # 1. LEITURA DOS CAMPOS
        nome = request.POST.get("nome")
        tipoevento_id = request.POST.get("tipoEvento")
        dataI_str = request.POST.get("dataIni")
        dataF_str = request.POST.get("dataFin")
        horarioIni_str = request.POST.get("horasIni")
        horarioFin_str = request.POST.get("horasFin")
        local = request.POST.get("local")
        organizador_id = request.POST.get("organizador")
        vagas_str = request.POST.get("vagas")
        horasinp_str = request.POST.get("horasDura")
        

        # 2. VALIDAÇÃO SIMPLES: Verifique apenas campos estritamente visíveis e obrigatórios no HTML
        # Os campos quantPart e assinatura devem ser validados pelo seu valor ser maior que zero/existir.
        campos_obrigatorios_visiveis = [
            nome
        ]

        if not all(campos_obrigatorios_visiveis):
            return HttpResponse("Todos os campos visíveis devem ser preenchidos.")

        # 3. CONVERSÃO DE TIPOS E TRATAMENTO DE ERROS MAIS ROBUSTO
        try:
            from datetime import datetime, time # Importar datetime aqui se não estiver no topo

            # Converte Strings para Datas/Tempos
            dataI = datetime.strptime(dataI_str, '%Y-%m-%d').date()
            dataF = datetime.strptime(dataF_str, '%Y-%m-%d').date()
            horarioI = datetime.strptime(horarioIni_str, '%H:%M').time()
            horarioF = datetime.strptime(horarioFin_str, '%H:%M').time()
            
            # Converte Strings para Inteiros (Usando valor padrão 0 em caso de erro/vazio)
            # Use o operador OR para garantir que a string tem algum valor antes de converter.
            vagas = int(vagas_str or 0)
            horas_duracao = int(horasinp_str or 0)

        except ValueError:
            return HttpResponse("Erro de formato: Certifique-se de que os campos de Data, Hora e Número estão preenchidos corretamente.")
        
        
        if dataI > dataF:
            return HttpResponse("A data inicial não pode ser depois da data final.")
        
        
        if dataI == dataF and horarioI > horarioF:
             return HttpResponse("O horário inicial não pode ser menor que o horário final.")

        # SALVAMENTO DOS DADOS NO MODELO
        try:
            
            evento.nome = nome
            evento.tipoevento_id = tipoevento_id 
            evento.dataI = dataI
            evento.dataF = dataF
            evento.horarioIni = horarioI
            evento.horarioFin = horarioF
            evento.local = local
            evento.organResp_id = organizador_id 
            evento.vagas = vagas
            evento.horas_duracao = horas_duracao 
            evento.organizador = organizador_nome

            evento.save()

            # Log
            with transaction.atomic():
                Log.objects.create(
                    id_evento=evento,
                    usuario_id=usuario,
                    acao=f"Evento editado: {evento.nome}"
                )

            return redirect("eventos")

        except Exception as e:
            # Retorna o erro real do Django (ex: campo NOT NULL violado)
            return HttpResponse(f"Erro ao salvar evento no banco de dados: {e}")

    return render(request, "templates_org/editar_evento.html", context)
#Funcoes para inscricoes------------------------------------------------------------------------------------------------

def home_inscricao(request):
    usuario_id = request.session.get("usuario_id")
    if not usuario_id:
        return redirect("login")
    
    usuario = get_object_or_404(Usuario, id_usuario=usuario_id)
    
    inscritos = Inscrito.objects.filter(usuario_id=usuario)
    
    #Lista de eventos em que o usuário está inscrito
    eventos_inscritos = [i.evento_id for i in inscritos]
    
    return render(request, "list_inscricoes.html", {
        "usuario": usuario,
        "eventos": eventos_inscritos,
    })

def inscricao_evento(request, evento_id):
    usuario_id = request.session.get("usuario_id")

    if not usuario_id:
        return redirect("login")
    
    if request.method == "POST":
        usuario = get_object_or_404(Usuario, id_usuario = usuario_id)
        evento = get_object_or_404(Evento, id_evento = evento_id)
    
        if Inscrito.objects.filter(usuario_id = usuario, evento_id = evento).exists():
            return HttpResponse("Você já está inscrito neste evento")
     
        if evento.vagas <= 0:
            return HttpResponse("Não há mais vagas disponíveis")
    
        Inscrito.objects.create(usuario_id = usuario, evento_id = evento)

        evento.vagas -= 1
        evento.save()

        # garante atomicidade e usa instâncias em vez de IDs
        with transaction.atomic():
            Log.objects.create(
                id_evento=evento,
                usuario_id=usuario,
                acao=f"Usuário {usuario.nome} inscrito no evento {evento.nome}"
            )

        return redirect("list_inscricao")
        

    return render(request,"inscricao.html", {"usuarios": Usuario.objects.all(), "eventos": Evento.objects.all()}) 

def eventos_disponiveis(request):
    usuario_id = request.session.get("usuario_id")
    if not usuario_id:
        return redirect("login")
    
    usuario = get_object_or_404(Usuario, id_usuario=usuario_id)
    
    #Lista de eventos em que o usuário já está inscrito
    inscritos_ids = Inscrito.objects.filter(usuario_id=usuario).values_list('evento_id', flat=True)
    
    eventos = Evento.objects.all()
    
    return render(request, "inscricao.html", {
        "usuario": usuario,
        "eventos": eventos,
        "inscritos": inscritos_ids,  # só os IDs
    })

def usuario_eventos(request, usuario_id):
    
    #pega o id do usuario logado na sessao
    user = get_object_or_404(Usuario, id_usuario = usuario_id)
    inscricoes = Inscrito.objects.filter(usuario_id = user)
    
    #pega os eventos que o usuario ta inscrito
    eventos = [inscricao.evento_id for inscricao in inscricoes]
    
    return render(request, "usuarios/meus_eventos.html", {"usuario" : user, "eventos" : eventos})

#Funcoes para certificados----------------------------------------------------------------------------------------------

def ver_certificados(request):
    
    #pega todos os certificados que n foram emitidos
    eventos = {
        'eventos' : Evento.objects.filter(emitido = False)
    }
    
    Log.objects.create(
        acao="Visualização da lista de certificados pendentes de emissão"
    )

    return render(request, "usuarios/certificados.html", eventos)

def emitir_certificados(request, evento_id):
    
    with transaction.atomic():
        try:
            evento = get_object_or_404(Evento, pk=evento_id)

            inscricoes = Inscrito.objects.filter(evento_id=evento.pk)

            if not inscricoes.exists():
                return HttpResponse("Não há inscritos para este evento.")

            for inscricao in inscricoes:
                Certificado.objects.create(
                    usuario_id = inscricao.usuario_id,
                    evento_id = inscricao.evento_id,
                    horas = inscricao.evento_id.horasDura
                )
                Log.objects.create(
                    id_evento=evento,
                    usuario_id=inscricao.usuario_id,
                    acao=f"Certificado emitido para o usuário {inscricao.usuario_id.nome} no evento {evento.nome}"
                )

            # Remove inscritos após emitir
            Inscrito.objects.filter(evento_id=evento.pk).delete()

            # Marca evento como certificado emitido
            evento.certificado = True
            evento.save()

        except Exception as e:
            return HttpResponse(f"Erro na emissão de certificados: {e}")

    return redirect("/certificados/")

def meus_certificados(request):
    #pega o id do usuario logado na sessao
    usuario_id = request.session.get("usuario_id")
    
    #busca o usuario e os certificados dele verificando se o id do usuario na sessao bate com o id do usuario nos certificados
    try:
        usuario = get_object_or_404(Usuario, id_usuario = usuario_id)
        certs = Certificado.objects.filter(usuario_id = usuario)
    
    except Exception:
        return HttpResponse("Erro ao buscar certificados.")
    
    return render(request, "usuarios/meus_certificados.html", {"usuario" : usuario, "certificados" : certs})

#Funcoes para logout----------------------------------------------------------------------------------------------------

def logout(request):
    # Verifica se há um id de usuário armazenado na sessão, se houver, o deletar e redireciona o usuário para a tela de login
    if "usuario_id" in request.session:
        del request.session["usuario_id"]
    
    request.session.flush()
    
    return redirect("login")


#Funcoes para logs------------------------------------------------------------------------------------------------------

def logs(request):
    usuario_id = request.session.get("usuario_id")
    
    if not usuario_id:
        return redirect("login")
      
    try:
        usuario = get_object_or_404(Usuario, id_usuario = usuario_id)
    
    except Usuario.DoesNotExist:
        return HttpResponse("Usuário não foi encontrado.")
    
    #se o usuario n for organizador, redireciona ele para a pagina de inscricoes, apenas organizadores podem ver os logs
    if usuario.tipo != "organizador":
        return redirect("inscricao")
    
    context = {
        'Logs' : Log.objects.all().order_by('-horaAcao')
    }
    # Renderiza a página com todos os logs
    return render(request, "templates_org/log.html", context)