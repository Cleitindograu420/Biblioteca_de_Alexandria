from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator

class Usuario(models.Model):
    id_usuario = models.AutoField(primary_key=True, unique=True)
    nome = models.TextField(max_length=150)
    telefone = models.CharField(max_length=15, null=True)
    instEnsino = models.TextField(max_length=100, null= True)
    senha = models.CharField(max_length=200, null=False)
    email = models.EmailField(max_length=254, unique=True)
    tipo = models.CharField(max_length=50, choices=[("estudante", "Estudante"), ("professor", "Professor"), ("organizador", "Organizador")], default= "Estudante")
class Evento (models.Model):
    id_evento = models.AutoField(primary_key=True, unique=True)
    nome = models.TextField(max_length=100, null= True)
    tipoEvento = models.TextField(max_length=200)
    dataIni = models.DateField()
    dataFin = models.DateField()
    horarioIni = models.TimeField()
    horarioFin = models.TimeField()
    horasDura = models.TimeField(null=True, blank=True)
    local = models.TextField(max_length=200)
    quantPart = models.IntegerField(validators=[MinValueValidator(0)])
    organizador = models.TextField(max_length=200)
    vagas = models.IntegerField(validators=[MinValueValidator(0)], null=False)
    certificado = models.BooleanField(default=False)
class Inscrito(models.Model):
    id_inscricao = models.AutoField(primary_key=True, unique=True)
    usuario_id = models.ForeignKey(Usuario, on_delete = models.CASCADE)
    evento_id = models.ForeignKey(Evento, on_delete= models.CASCADE)
    data_inscricao = models.DateTimeField(auto_now_add= True)
class Certificado(models.Model):
    id_carrinho = models.AutoField(primary_key=True)
    usuario_id = models.ForeignKey(Usuario, on_delete= models.CASCADE)
    evento_id = models.ForeignKey(Evento, on_delete= models.CASCADE, related_name="certificados")
    dataEmissao = models.DateField(default= timezone.now)
    horas = models.IntegerField(validators=[MinValueValidator(0)], null=True, blank=True)
