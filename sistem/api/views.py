from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from login.models import Usuario, Evento, Inscrito, Log
from django.db import transaction
from .serializer import UserSerializer, EventoSerializer
from django.contrib.auth.models import User

@api_view(['GET'])
def get_users(request):
    users = User.objects.all()
    serializer = UserSerializer(users, many=True)
    return Response(serializer.data)

@api_view(['POST'])
def create_user(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
def user_detail(request, pk):
    try:
        user = User.objects.get(pk=pk)
    except User.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = UserSerializer(user)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = UserSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
def eventos_list(request):
    """Retorna todos os eventos do banco de dados."""
    eventos = Evento.objects.all()
    serializer = EventoSerializer(eventos, many=True)
    return Response(serializer.data)
    
@api_view(['POST'])
def inscrever_evento(request):
    """API endpoint to register an existing Usuario in a specific Evento.

    Expects JSON payload: {"usuario_id": <int>, "evento_id": <int>}.
    """
    usuario_id = request.data.get('usuario_id')
    evento_id = request.data.get('evento_id')

    if usuario_id is None or evento_id is None:
        return Response({"detail": "Both 'usuario_id' and 'evento_id' are required."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        usuario = Usuario.objects.get(id_usuario=usuario_id)
    except Usuario.DoesNotExist:
        return Response({"detail": "Usuario not found."}, status=status.HTTP_404_NOT_FOUND)

    try:
        # lock the event row to avoid race conditions on vagas
        with transaction.atomic():
            evento = Evento.objects.select_for_update().get(id_evento=evento_id)

            # already registered?
            if Inscrito.objects.filter(usuario_id=usuario, evento_id=evento).exists():
                return Response({"detail": "Usuario ja inscrito neste evento."}, status=status.HTTP_400_BAD_REQUEST)

            if evento.vagas <= 0:
                return Response({"detail": "Nao ha mais vagas disponiveis."}, status=status.HTTP_400_BAD_REQUEST)

            # create inscription and decrement vagas
            inscricao = Inscrito.objects.create(usuario_id=usuario, evento_id=evento)
            evento.vagas = evento.vagas - 1
            evento.save()

            # create log entry
            Log.objects.create(
                id_evento=evento,
                usuario_id=usuario,
                acao=f"Usuario {usuario.nome} inscrito no evento {evento.nome} via API"
            )

    except Evento.DoesNotExist:
        return Response({"detail": "Evento not found."}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"detail": f"Erro interno: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return Response({"detail": "Inscricao criada com sucesso.", "id_inscricao": inscricao.id_inscricao}, status=status.HTTP_201_CREATED)
