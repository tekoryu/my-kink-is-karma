from django.db import models


class Tema(models.Model):
    """
    Modelo para representar temas de interesse para organização de proposições legislativas.
    
    Os temas são utilizados para agrupar e categorizar proposições legislativas
    de acordo com áreas de interesse específicas (ex: Educação, Segurança Pública).
    Cada tema deve ter um nome único para evitar duplicação.
    """
    
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
        ordering = ['nome']
    
    def __str__(self):
        return self.nome


class Proposicao(models.Model):
    """
    Modelo para representar proposições legislativas que serão monitoradas pelo sistema.
    
    Cada proposição está associada a um tema e possui identificadores únicos
    (tipo, número e ano) que a distinguem de outras proposições. O sistema
    monitora o andamento destas proposições através de APIs públicas.
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
    
    # Campos da API do Senado Federal
    sf_id = models.BigIntegerField(
        null=True,
        blank=True,
        help_text="ID do processo no sistema do Senado Federal"
    )
    
    sf_codigo_materia = models.BigIntegerField(
        null=True,
        blank=True,
        help_text="Código da matéria no sistema do Senado Federal"
    )
    
    papel_sf = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        help_text="Objetivo do processo no Senado Federal (ex: Revisora)"
    )
    
    tipo_conteudo = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        help_text="Tipo de conteúdo do processo (ex: Norma Geral)"
    )
    
    ementa = models.TextField(
        null=True,
        blank=True,
        help_text="Ementa da proposição"
    )
    
    tipo_documento = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        help_text="Tipo de documento do processo (ex: Projeto de Lei Ordinária)"
    )
    
    sf_data_apresentacao = models.DateField(
        null=True,
        blank=True,
        help_text="Data de apresentação do processo no Senado Federal"
    )
    
    sf_autoria = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        help_text="Autoria do processo (ex: Câmara dos Deputados)"
    )
    
    sf_tramitando = models.CharField(
        max_length=10,
        null=True,
        blank=True,
        help_text="Indica se o processo está tramitando (ex: Sim, Não)"
    )
    
    sf_last_info = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        help_text="Última informação atualizada do processo (ex: EVENTO_LEGISLATIVO)"
    )
    
    sf_lastupdate_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Data da última atualização do processo no Senado Federal"
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


class HistoricoAtualizacao(models.Model):
    """
    Modelo para rastrear o histórico de atualizações de proposições legislativas.
    
    Armazena os dados recebidos da API externa a cada atualização, permitindo
    acompanhar as mudanças ao longo do tempo e manter um registro completo
    das alterações nas proposições.
    """
    
    proposicao = models.ForeignKey(
        Proposicao,
        on_delete=models.CASCADE,
        related_name='historicos_atualizacao',
        help_text="Proposição à qual este histórico pertence"
    )
    
    dados_atualizados = models.JSONField(
        help_text="Dados recebidos da API externa na atualização"
    )
    
    data_atualizacao = models.DateTimeField(
        auto_now_add=True,
        help_text="Data e hora da atualização"
    )
    
    class Meta:
        verbose_name = "Histórico de Atualização"
        verbose_name_plural = "Históricos de Atualização"
        ordering = ['-data_atualizacao']
    
    def __str__(self):
        return f"Atualização de {self.proposicao} em {self.data_atualizacao.strftime('%d/%m/%Y %H:%M')}"
