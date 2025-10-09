from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from .models import Usuario,Evento, Inscrito, Certificado

#funcao para renderizar a pagina home
#def home(request):
# return render(request, 'usuarios/home.html')

#Funcoes para usuarios--------------------------------------------------------------------------------------------------

#funcao para deletar usuario de acordo com o id
def delete_user(request, pk):
    usuario = get_object_or_404(Usuario, pk=pk)
    if request.method == "GET":
        usuario.delete()
        return redirect('usuarios/')






#Funcoes para eventos--------------------------------------------------------------------------------------------------
#Funcoes para inscricoes-----------------------------------------------------------------------------------------------
#Funcoes para certificados----------------------------------------------------------------------------------------------
