from django.db import models

class Usuario(models.Model):
    id_usuario = models.AutoField(primary_key=True, unique=True)
    nome = models.TextField(max_length=150, null=False)
    senha = models.CharField(max_length=200, null=False)
    email = models.CharField(max_length=254, unique=True)
