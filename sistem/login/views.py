#todos os imports necessarios
from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from .models import Usuario,Evento, Inscrito, Certificado
from django.core.validators import RegexValidator, EmailValidator
from django.core.exceptions import ValidationError
from django.contrib import messages
from django.db import transaction

#funcao para renderizar a pagina home
def base(request):
    return render(request, 'funcoes.html')

#Funcoes para usuarios--------------------------------------------------------------------------------------------------

#funcao para deletar usuario de acordo com o id
#nao sei explicar direito oq ta acontecendo aqui, fui fazendo pelo auto complete do vscode
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
    #se o metodo for post, ele pega as informacoes do formulario e valida elas
    if request.method == 'POST':
        nome = request.POST.get('nome')
        telefone = request.POST.get('telefone')
        instEnsino = request.POST.get('instEnsino')
        senha = request.POST.get('senha')
        email = request.POST.get('email')
        tipo = request.POST.get('tipo')
        senha_tipo = request.POST.get('senha_acesso')
        #verifica se o tipo de usuario e professor ou organizador e define a senha de acesso correta para cada tipo
        senha_prof = "professor123"
        senha_org = "organizador123"

        #valida o telefone e o email com regex
        telefone_valido = RegexValidator(regex= r'^\(\d{2}\) \d{4,5}-\d{4}$', 
                                     message="O telefone deve estar no formato (XX) XXXXX-XXXX ou (XX) XXXX-XXXX.")
        
        #valida o email com a funcao EmailValidator nativa do django
        email_valido = EmailValidator(message="O email fornecido é inválido.")

        #valida se o telefone e email ja estao cadastrados no banco de dados
        try:
            telefone_valido(telefone)
            email_valido(email)

            #se o telefone ja estiver cadastrado, retorna uma mensagem de erro
            if Usuario.objects.filter(telefone = telefone).exists():
                return HttpResponse('Telefone já cadastrado. Por favor, utilize outro telefone.')
            
            #se o tipo de usuario for professor, verifica se a senha de acesso bate com a senha correta
            if tipo == "professor":
                if senha_tipo != senha_prof:
                    return HttpResponse('Senha de acesso incorreta para o tipo Professor.')
            
            #se o tipo de usuario for organizador, verifica se a senha de acesso bate com a senha correta, igual a cima
            elif tipo == "organizador":
                if senha_tipo != senha_org:
                    return HttpResponse('Senha de acesso incorreta para o tipo Organizador.')
            
            #se o email ja estiver cadastrado, retorna uma mensagem de erro
            try:
                if Usuario.objects.filter(email=email).exists():
                    return HttpResponse('Email já cadastrado. Por favor, utilize outro email.')
            
            #se o email for invalido, retorna uma mensagem de erro
            except ValidationError:
                return HttpResponse('Email inválido. Por favor, insira um email válido.')
            
            #se todas as informacoes forem validas, cria um novo usuario no banco de dados
            Usuario.objects.create(
                nome=nome,
                telefone=telefone,
                instEnsino=instEnsino,
                senha=senha,
                email=email,
                tipo=tipo
            )
            #redireciona o usuario para a tela de login
            return redirect('login')
        
        except ValidationError:
            return HttpResponse('Telefone inválido. Por favor, insira um telefone válido.')
    
    return render(request, 'usuarios/usuarios.html')

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
        return redirect('inscricao')
    
    usuarios = { 'usuarios': Usuario.objects.all(), }

    return render(request, 'usuarios/ver_usuarios.html', usuarios)

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
                return redirect('inscricao')
            
            #caso o usuario n seja encontrado, retorna uma mensagem de erro
            else:
                return HttpResponse('Email ou senha incorretos. Tente novamente.')
        
        #caso o usuario n seja encontrado, retorna uma mensagem de erro
        except Usuario.DoesNotExist:
            return HttpResponse('Email ou senha incorretos. Tente novamente.')
    
    #se o metodo for get, ele renderiza a pagina de login
    return render(request, 'usuarios/login.html')

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
        telefone_valido = RegexValidator(regex= r'^\(\d{2}\) \d{4,5}-\d{4}$', 
                                     message="O telefone deve estar no formato (XX) XXXXX-XXXX ou (XX) XXXX-XXXX.")
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
        return redirect("inscricao")
    
    # Renderiza a página de edição com os dados do usuário atual
    return render(request, "usuarios/editar_usuario.html", {"usuario" : usuario})

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
        return redirect("inscricao")
    
    # Renderiza a página com todos os eventos
    eventos = {
        'eventos' : Evento.objects.all()
    }
    
    return render(request, "usuarios/visu_eventos.html", eventos)

def cadastro_eventos(request):
    try:
        # Validação das informações adquiridas no campo das datas
        dia_inicio_date = request.POST.get("dataIni")
        dia_fim_date = request.POST.get("dataFin")

        # Verifica se os espaços dos dias não estão vazios
        if not dia_inicio_date or not dia_fim_date:  
            return HttpResponse("O campo data de início e final são obrigatórios")

        
        try:
            dia_inicio = int(dia_inicio_date)
            dia_fim = int(dia_fim_date)
        except ValueError:
            return HttpResponse("O campo data de início e final devem ser uma data válida")

        
        # Validação das informações adquiridas no campo dos horários
        horarioIni_h = request.POST.get("horarioIni")
        horarioFin_h = request.POST.get("horarioFin")
        
        # Verifica se os espaços não estão vazios
        if not horarioIni_h or not horarioFin_h:
            return HttpResponse("O campo do horário inicial e final são obrigatórios")
        
        try:
            horario_inicio = int(horarioIni_h)
            horario_final = int(horarioFin_h)
        except ValueError:
            return HttpResponse("O campo do horário inicial e final devem ser um horário válido")
        
        # Validação das informações adquiridas no campo das vagas
        vagas_int = request.POST.get("vagas")
        quantParticipantes_str = request.POST.get("quantPart")
        
        # Verifica se a informação adquirida é um número inteiro
        try:
            vagasInt = int(vagas_int)
        except ValueError:
            return HttpResponse("O valor das vagas deve ser um número inteiro positivo")
        
        try:
            quantParticipantesInt = int(quantParticipantes_str)
        except ValueError:
            return HttpResponse("O valor da quantidade de participantes deve ser um valor inteiro positivo")
        
        # Verifica se há uma quantidade maior de vagas do que de participantes
        if vagasInt > quantParticipantesInt:
            return HttpResponse("Não pode haver um número maior de vagas do que de participantes")
        
        # Verifica se os valores são positivos
        if quantParticipantesInt < 0:
            return HttpResponse("Não pode haver uma quantidade negativa de participantes")
        
        if vagasInt < 0:
            return HttpResponse("Não pode haver uma quantidade negativa de vagas")
        
        horasC = horario_final - horario_inicio
        
        horasinp = request.POST.get("horas")
        if horasinp and horasinp.isdigit():
            horas = int(horasinp)
        else:
            horas = horasC
        
        # Caso todas as informações sejam verificadas, um novo evento é criado
        novo_evento = Evento(
        nome = request.POST.get("nome"),
        tipoevento = request.POST.get("tipoE"),
        dataI = dia_inicio,
        dataF = dia_fim,
        horarioIni = horario_inicio,
        horarioFin = horario_final,
        horasDura = horas,
        local = request.POST.get("local"),
        quantPart = quantParticipantesInt,
        organResp = request.POST.get("organResp"),
        vagas = vagasInt
        )
        
        novo_evento.save()    
    
    except ValueError:
        messages.error(request, "Erro")
        return redirect("visu_eventos")
    
    eventos = {
        'eventos' : Evento.objects.all()
    }
    
    return render(request, 'usuarios/visu_eventos.html', eventos)

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
    
    evento.delete()
    return redirect("even")

def editar_evento(request, pk):
    usuario_id = request.session.get("usuario_id")
    
    if not usuario_id:
        return redirect("login")
      
    try:
        usuario = get_object_or_404(Usuario, id_usuario = usuario_id)
    
    except Usuario.DoesNotExist:
        return HttpResponse("Usuário não foi encontrado.")
    
    #se o usuario n for organizador, redireciona ele para a pagina de inscricoes, apenas organizadores podem editar eventos
    if usuario.tipo != "organizador":
        return redirect("inscricao")

    #pega o evento com o id passado na url    
    evento = get_object_or_404(Evento, pk = pk)

    if request.method == "POST":
        nome = request.POST.get("nome")
        tipoevento = request.POST.get("tipo_evento")
        dataI_str = request.POST.get("dataI")
        dataF_str = request.POST.get("dataF")
        horarioI_str = request.POST.get("horarioI")
        horarioF_str = request.POST.get("horarioF")
        local = request.POST.get("local")
        quantPart_str = request.POST.get("quantPart")
        organResp = request.POST.get("organResp")
        vagas_str = request.POST.get("vagas")
        assinatura = request.POST.get("assinatura")
        horasinp = request.POST.get("horas")
        
        # Verifica se os campos, se preenchidos coretamenete, sao salvos
        try:
            if nome and tipoevento and dataI_str and dataF_str and horarioI_str and horarioF_str and local and quantPart_str and organResp and vagas_str and assinatura and horasinp:
                dataI = int(dataI_str)
                dataF = int(dataF_str)
                vagas = int(vagas_str)
                quantPart = int(quantPart_str)
                horarioI = int(horarioI_str)
                horarioF = int(horarioF_str)

                if quantPart == 0:
                    return HttpResponse("Um evento não pode ter 0 participantes.")
                
                if quantPart < 0:
                    return HttpResponse("O evento não pode possuir um número negativo de participantes.")
            
                if dataI > dataF:
                    return HttpResponse("A data inicial não pode ser depois da data final.")
            
                if horarioI < 0 or horarioI > 24 or horarioF < 0 or horarioF > 31:
                    return HttpResponse("O horário deve ser entre 0 e 24.")
            
                if vagas > quantPart:
                    return HttpResponse("Não pode haver uma quantidade maior de vagas do que de participantes.")
            
                if horarioI > horarioF:
                    return HttpResponse("O horário inicial não pode ser menor que o horário final.")
            
                evento.nome = nome
                evento.tipoevento = tipoevento
                evento.dataI = dataI
                evento.dataF = dataF
                evento.horarioI = horarioI
                evento.horarioF = horarioF
                evento.local = local
                evento.quantPart = quantPart
                evento.organResp = organResp
                evento.vagas = vagas
                evento.save()

                return redirect("even")

        #verifica se algum campo nao foi preenchido
        except UnboundLocalError:
            return HttpResponse("Todas as caixas devem ser preenchidas.")

        else:
            return HttpResponse("Nenhum dos campos pode estar vazio.")

        #renderiza a página de edição com os dados do evento atual

    return render(request, "usuarios/editar_evento.html", {"evento" : evento})
#Funcoes para inscricoes------------------------------------------------------------------------------------------------

def home_inscricao(request):
    usuario_id = request.session.get("usuario_id")

    if not usuario_id:
        return redirect("login")

    #pega o usuario logado, todos os eventos
    usuario = Usuario.objects.get(id_usuario=usuario_id)
    eventos = Evento.objects.all()
    
    #pega os eventos que o usuario ja ta inscrito
    inscritos = Inscrito.objects.filter(usuario_id=usuario).values_list("evento_id", flat=True)

    #renderiza a pagina de inscricoes com os eventos que o usuario esta inscrito
    return render(request, "usuarios/eventosU.html", {
        "usuario": usuario,
        "eventos": eventos,
        "inscritos": inscritos
    })

def inscricao_evento(request, usuario_id, evento_id):
    usuario_id = request.session.get("usuario_id")

    if not usuario_id:
        return redirect("login")
    
    #recebe o id do usuario e do evento pelo html
    if request.method == "POST":
        usuario = get_object_or_404(Usuario, id_usuario = usuario_id)
        evento = get_object_or_404(Evento, id_evento = evento_id)
        
        #verifica se o usuario ja ta inscrito no evento e se ainda ha vagas disponiveis
        if Inscrito.objects.filter(usuario_id = usuario, evento_id = evento).exists():
            return HttpResponse("Você já está inscrito neste evento")
     
        if evento.vagas <= 0:
            return HttpResponse("Não há mais vagas disponíveis")

        #se tudo estiver ok, cria a inscricao e diminui o numero de vagas disponiveis
        Inscrito.objects.create(usuario_id = usuario, evento_id = evento)

        evento.vagas -= 1
        evento.save()
        
        messages.success(request, f"Você foi inscrito com sucesso no seguinte evento: {evento.nome}!")
        return redirect("inscricao")
        

    return render(request,"usuarios/meus_eventos.html", {"usuarios": Usuario.objects.all(), "eventos": Evento.objects.all()}) 

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
    
    return render(request, "usuarios/certificados.html", eventos)

def emitir_certificados(request, evento_id):

    #permite que tudo dentro do bloco seja executado como uma transacao atomica, ou seja, se der algum erro em qualquer parte do bloco, nenhuma mudanca sera feita no banco de dados
    with transaction.atomic():
        #pega o evento com a pk passado na url
        try:
            evento = get_object_or_404(Evento, pk = evento_id)

            inscricoes = Inscrito.objects.filter(evento_id = evento.pk)


            #se n houver inscricoes, retorna uma mensagem de erro
            if not inscricoes.exists():
                return HttpResponse("Não há inscritos para este evento.")
            
            for inscricao in inscricoes:
                Certificado.objects.create(usuario_id = inscricao.usuario_id, evento_id = inscricao.evento_id, assinatura = inscricao.evento_id.assinatura, horas = inscricao.evento_id.horas)
            
            Inscrito.objects.filter(evento_id = evento.pk).delete()        
            
            #salva que o certificado ja foi emitido para o evento
            evento.emitido = True
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