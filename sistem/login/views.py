from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from .models import Usuario,Evento, Inscrito, Certificado
from django.core.validators import RegexValidator, EmailValidator
from django.core.exceptions import ValidationError

#funcao para renderizar a pagina home
def home(request):
 return render(request, 'usuarios/home.html')

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
        usuario = get_object_or_404(Usuario, id=usuario = usuario_id)
       
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
        
    return render(request, 'usuarios/home.html')

          
          




#Funcoes para eventos--------------------------------------------------------------------------------------------------
#Funcoes para inscricoes-----------------------------------------------------------------------------------------------
#Funcoes para certificados----------------------------------------------------------------------------------------------
