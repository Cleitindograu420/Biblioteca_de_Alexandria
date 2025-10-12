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
    usuario_id = request.session.get('usuario_id')

    if not usuario:
        return redirect('login')
    
    if request.method == 'GET':
       usuario = get_object_or_404(Usuario, id_usuario = usuario_id)
       return render(request, 'usuarios/delete_usuario.html', {'usuario': usuario})
    
    if request.method == 'POST':
        usuario = get_object_or_404(Usuario, id_usuario = usuario_id)
       
        senha = request.POST.get('senha') 
        
        if usuario.senha != senha:
            return HttpResponse('Senha incorreta. Tente novamente.')
        
        usuario.delete()
        return redirect('login')

def cadastro_usuario(request):
    if request.method == 'POST':
        nome = request.POST.get('nome')
        telefone = request.POST.get('telefone')
        instEnsino = request.POST.get('instEnsino')
        senha = request.POST.get('senha')
        email = request.POST.get('email')
        tipo = request.POST.get('tipo')
        senha_tipo = request.POST.get('senha_acesso')

        senha_prof = "professor123"
        senha_org = "organizador123"
    
        telefone_valido = RegexValidator(regex= r'^\(\d{2}\) \d{4,5}-\d{4}$', 
                                     message="O telefone deve estar no formato (XX) XXXXX-XXXX ou (XX) XXXX-XXXX.")
    
        email_valido = EmailValidator(message="O email fornecido é inválido.")

        try:
            telefone_valido(telefone)
            email_valido(email)

            if Usuario.objects.filter(telefone = telefone).exists():
                return HttpResponse('Telefone já cadastrado. Por favor, utilize outro telefone.')
            
            if tipo == "professor":
                if senha_tipo != senha_prof:
                    return HttpResponse('Senha de acesso incorreta para o tipo Professor.')
                
            elif tipo == "organizador":
                if senha_tipo != senha_org:
                    return HttpResponse('Senha de acesso incorreta para o tipo Organizador.')
            
            try:
                if Usuario.objects.filter(email=email).exists():
                    return HttpResponse('Email já cadastrado. Por favor, utilize outro email.')
            
            except ValidationError:
                return HttpResponse('Email inválido. Por favor, insira um email válido.')
            
            Usuario.objects.create(
                nome=nome,
                telefone=telefone,
                instEnsino=instEnsino,
                senha=senha,
                email=email,
                tipo=tipo
            )
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
    
    if usuario.tipo != 'organizador':
        return redirect('inscricao')
    
    usuarios = { 'usuarios': Usuario.objects.all(), }

    return render(request, 'usuarios/ver_usuarios.html', usuarios)

def login_user(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        senha = request.POST.get('senha')

        try:
            if not email or not senha:
                return HttpResponse('Por favor, preencha todos os campos.')
            
            user = Usuario.objects.get(email=email, senha=senha)

            if user:
                request.session['usuario_id'] = user.id_usuario
                return redirect('inscricao')
            
            else:
                return HttpResponse('Email ou senha incorretos. Tente novamente.')
        
        except Usuario.DoesNotExist:
            return HttpResponse('Email ou senha incorretos. Tente novamente.')
    
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
        
        if Usuario.objects.filter(telefone = telefone).exclude(id_usuario = usuario_id).exists():
            return HttpResponse("Este telefone já está cadastrado por outro usuário")
        
        validator = RegexValidator(regex = r'^\d{13}$', message = "O número de telefone deve ser inserido no formato: '+9999999999999'.")
        
        try:
            validator(telefone)
        
        except ValidationError:
            return HttpResponse("O número deve ser inserido no seguinte formato: '+9999999999999'.")
        
        # Caso as informações sejam inseridas corretamente, as mudanças são salvas
        usuario.nome = nome
        usuario.senha = senha
        usuario.telefone = telefone
        usuario.save()
    
        return redirect("inscricao")

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
    
    if usuario.tipo != "organizador":
        return redirect("inscricao")
    
    eventos = {
        'eventos' : Evento.objects.all()
    }
    
    return render(request, "usuarios/visu_eventos.html", eventos)

def cadastro_eventos(request):
    try:
        # Validação das informações adquiridas no campo das datas
        dia_inicio_str = request.POST.get("dataIni")
        dia_fim_str = request.POST.get("dataFin")

        # Verifica se os espaços dos dias não estão vazios
        if not dia_inicio_str or not dia_fim_str:  
            return HttpResponse("O campo data de início e final são obrigatórios")

        try:
            dia_inicio = int(dia_inicio_str)
            dia_fim = int(dia_fim_str)
        except ValueError:
            return HttpResponse("O campo data de início e final devem ser um número inteiro")
 
        # Verifica se a data é um dia válido (entre 1 ou 31)
        if dia_inicio < 1 or dia_inicio > 31 or dia_fim < 1 or dia_fim > 31:
            return HttpResponse("O dia de início e final devem estar entre 1 e 31")
        
        # Validação das informações adquiridas no campo dos horários
        horarioIni_str = request.POST.get("horarioIni")
        horarioFin_str = request.POST.get("horarioFin")
        
        # Verifica se os espaços não estão vazios
        if not horarioIni_str or not horarioFin_str:
            return HttpResponse("O campo do horário inicial e final são obrigatórios")
        
        try:
            horario_inicio = int(horarioIni_str)
            horario_final = int(horarioFin_str)
        except ValueError:
            return HttpResponse("O campo do horário inicial e final devem ser número inteiros")
            
        # Verifica se os horários estão entre horários existentes (entre 0 ou 24 horas)
        if horario_inicio < 0 or horario_inicio > 24 or horario_final < 0 or horario_final > 24:
            return HttpResponse("O horário inicial e final devem estar entre 0 e 24")
        
        # Validação das informações adquiridas no campo das vagas
        vagas_str = request.POST.get("vagas")
        quantParticipantes_str = request.POST.get("quantPart")
        
        # Verifica se a informação adquirida é um número inteiro
        try:
            vagasInt = int(vagas_str)
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
    
    if usuario.tipo != "organizador":
        return redirect("inscricao")
    
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
    
    if usuario.tipo != "organizador":
        return redirect("inscricao")
    
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
        
        try:
            if nome and tipoevento and dataI_str and dataF_str and horarioI_str and horarioF_str and local and quantPart_str and organResp and vagas_str and assinatura and horasinp:
                dataI = int(dataI_str)
                dataF = int(dataF_str)
                vagas = int(vagas_str)
                quantPart = int(quantPart_str)
                horarioI = int(horarioI_str)
                horarioF = int(horarioF_str)
                
                if horasinp and horasinp.isdigit():
                    horas = int(horasinp)
                else:
                    horas = horarioF - horarioI 
                
                if dataI < 1 or dataI > 31 or dataF < 1 or dataF > 31:
                    return HttpResponse("A data inicial e final devem estar entre os dias 1 e 31.")
                
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
                evento.horas = horas
                evento.assinatura = assinatura 
                evento.save()

                return redirect("even")

        except UnboundLocalError:
            return HttpResponse("Todas as caixas devem ser preenchidas.")

        else:
            return HttpResponse("Nenhum dos campos pode estar vazio.")

    return render(request, "usuarios/editar_evento.html", {"evento" : evento})
#Funcoes para inscricoes------------------------------------------------------------------------------------------------

def home_inscricao(request):
    usuario_id = request.session.get("usuario_id")

    if not usuario_id:
        return redirect("login")

    usuario = Usuario.objects.get(id_usuario=usuario_id)
    eventos = Evento.objects.all()
    
    inscritos = Inscrito.objects.filter(usuario_id=usuario).values_list("evento_id", flat=True)

    return render(request, "usuarios/eventosU.html", {
        "usuario": usuario,
        "eventos": eventos,
        "inscritos": inscritos
    })

def inscricao_evento(request, usuario_id, evento_id):
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
        
        messages.success(request, f"Você foi inscrito com sucesso no seguinte evento: {evento.nome}!")
        return redirect("inscricao")
        

    return render(request,"usuarios/meus_eventos.html", {"usuarios": Usuario.objects.all(), "eventos": Evento.objects.all()}) 

def usuario_eventos(request, usuario_id):
    user = get_object_or_404(Usuario, id_usuario = usuario_id)
    inscricoes = Inscrito.objects.filter(usuario_id = user)
    
    eventos = [inscricao.evento_id for inscricao in inscricoes]
    
    return render(request, "usuarios/meus_eventos.html", {"usuario" : user, "eventos" : eventos})

#Funcoes para certificados----------------------------------------------------------------------------------------------

def ver_certificados(request):
    eventos = {
        'eventos' : Evento.objects.filter(emitido = False)
    }
    
    return render(request, "usuarios/certificados.html", eventos)

def emitir_certificados(request, evento_id):
    with transaction.atomic():
        try:
            evento = get_object_or_404(Evento, pk = evento_id)

            inscricoes = Inscrito.objects.filter(evento_id = evento.pk)

            if not inscricoes.exists():
                return HttpResponse("Não há inscritos para este evento.")
            
            for inscricao in inscricoes:
                Certificado.objects.create(usuario_id = inscricao.usuario_id, evento_id = inscricao.evento_id, assinatura = inscricao.evento_id.assinatura, horas = inscricao.evento_id.horas)
            
            Inscrito.objects.filter(evento_id = evento.pk).delete()        
            
            evento.emitido = True
            evento.save()
            
        except Exception as e:
            return HttpResponse(f"Erro na emissão de certificados: {e}")
            
    return redirect("/certificados/")

def meus_certificados(request):
    usuario_id = request.session.get("usuario_id")
    
    try:
        usuario = get_object_or_404(Usuario, id_usuario = usuario_id)
        certs = Certificado.objects.filter(usuario_id = usuario)
    
    except Exception:
        return HttpResponse("Erro ao buscar certificados.")
    
    return render(request, "usuarios/meus_certificados.html", {"usuario" : usuario, "certificados" : certs})

