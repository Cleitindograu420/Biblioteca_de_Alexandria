from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from .models import Usuario,Evento, Inscrito, Certificado

#funcao para renderizar a pagina home
def home(request):
 return render(request, 'usuarios/home.html')

#Funcoes para usuarios--------------------------------------------------------------------------------------------------

#funcao para deletar usuario de acordo com o id
def delete_user(request):
    usuario = request.session.get('usuario_id')

    if not usuario:
        return redirect('login')
    
    if request.method == 'GET':
       usuario = get_object_or_404(Usuario, id=usuario = usuario_id)
       return render(request, 'usuarios/delete_usuario.html', {'usuario': usuario})
    
    if request.method == 'POST':
       usuario = get_object_or_404(Usuario, id=usuario = usuario_id)
       senha = request.POST.get('senha')
       usuario.delete()
       return redirect('login')
    
    if usuario.senha != senha:
        return HttpResponse('Senha incorreta. Tente novamente.')
          
          
          




#Funcoes para eventos--------------------------------------------------------------------------------------------------
#Funcoes para inscricoes-----------------------------------------------------------------------------------------------
#Funcoes para certificados----------------------------------------------------------------------------------------------
