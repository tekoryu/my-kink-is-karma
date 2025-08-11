from django.db import models


class Eixo(models.Model):
    """
    Modelo para representar eixos estratégicos que agrupam temas relacionados.
    
    Os eixos são utilizados para organizar temas em categorias estratégicas
    mais amplas, facilitando a navegação e compreensão da agenda legislativa.
    """
    
    id = models.IntegerField(
        primary_key=True,
        help_text="Identificador numérico do eixo"
    )
    
    nome = models.CharField(
        max_length=255,
        unique=True,
        null=False,
        blank=False,
        help_text="Nome descritivo do eixo estratégico"
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Data e hora de criação do eixo"
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Data e hora da última atualização do eixo"
    )
    
    class Meta:
        verbose_name = "Eixo"
        verbose_name_plural = "Eixos"
        ordering = ['id']
    
    def __str__(self):
        return f"Eixo {self.id}: {self.nome}"


class Tema(models.Model):
    """
    Modelo para representar temas de interesse para organização de proposições legislativas.
    
    Os temas são utilizados para agrupar e categorizar proposições legislativas
    de acordo com áreas de interesse específicas (ex: Educação, Segurança Pública).
    Cada tema deve ter um nome único para evitar duplicação.
    """
    
    eixo = models.ForeignKey(
        Eixo,
        on_delete=models.CASCADE,
        related_name='temas',
        help_text="Eixo ao qual este tema pertence"
    )
    
    nome = models.CharField(
        max_length=255,
        unique=True,
        null=False,
        blank=False,
        help_text="Nome do tema para organização das proposições (ex: Educação, Segurança Pública)"
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Data e hora de criação do tema"
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Data e hora da última atualização do tema"
    )
    
    class Meta:
        verbose_name = "Tema"
        verbose_name_plural = "Temas"
        ordering = ['eixo__id', 'nome']
    
    def __str__(self):
        return self.nome


class Proposicao(models.Model):
    """
    Modelo para representar proposições legislativas que serão monitoradas pelo sistema.
    
    Cada proposição está associada a um tema e possui identificadores únicos
    (tipo, número e ano) que a distinguem de outras proposições.
    """
    
    tema = models.ForeignKey(
        Tema,
        on_delete=models.CASCADE,
        related_name='proposicoes',
        help_text="Tema ao qual esta proposição pertence"
    )
    
    tipo = models.CharField(
        max_length=10,
        help_text="Tipo da proposição (ex: PL, PEC, MPV)"
    )
    
    numero = models.IntegerField(
        help_text="Número da proposição"
    )
    
    ano = models.IntegerField(
        help_text="Ano da proposição"
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Data e hora de criação da proposição no sistema"
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Data e hora da última atualização da proposição"
    )
    
    class Meta:
        verbose_name = "Proposição"
        verbose_name_plural = "Proposições"
        ordering = ['tema__nome', 'ano', 'numero']
        unique_together = ['tipo', 'numero', 'ano']
    
    def __str__(self):
        return f"{self.tipo} {self.numero}/{self.ano}"
    
    @property
    def identificador_completo(self):
        """
        Retorna o identificador completo da proposição no formato padrão.
        
        Returns:
            str: Identificador no formato "TIPO NUMERO/ANO"
        """
        return f"{self.tipo} {self.numero}/{self.ano}"
