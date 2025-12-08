from rest_framework import serializers
from django.contrib.auth.models import User
from login.models import Evento


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'


class EventoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Evento
        # include the main fields useful for clients
        fields = [
            'id_evento',
            'nome',
            'tipoEvento',
            'dataIni',
            'dataFin',
            'horasIni',
            'horasFin',
            'horasDura',
            'local',
            'quantPart',
            'organizador',
            'vagas',
            'certificado',
        ]