from django.contrib import admin
from .models import Eixo, Tema, Proposicao, SenadoActivityHistory, CamaraActivityHistory


@admin.register(Eixo)
class EixoAdmin(admin.ModelAdmin):
    """
    Configuração do admin para o modelo Eixo.
    
    Permite gerenciar eixos estratégicos que agrupam temas relacionados.
    """
    
    list_display = ['id', 'nome', 'created_at', 'updated_at']
    list_filter = ['created_at', 'updated_at']
    search_fields = ['nome']
    ordering = ['id']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('id', 'nome')
        }),
        ('Metadados', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Tema)
class TemaAdmin(admin.ModelAdmin):
    """
    Configuração do admin para o modelo Tema.
    
    Permite gerenciar temas de interesse para organização das proposições legislativas.
    """
    
    list_display = ['nome', 'eixo', 'created_at', 'updated_at']
    list_filter = ['eixo', 'created_at', 'updated_at']
    search_fields = ['nome', 'eixo__nome']
    ordering = ['eixo__id', 'nome']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('nome', 'eixo')
        }),
        ('Metadados', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Proposicao)
class ProposicaoAdmin(admin.ModelAdmin):
    """
    Configuração do admin para o modelo Proposicao.
    
    Permite gerenciar proposições legislativas associadas a temas específicos.
    """
    
    list_display = ['identificador_completo', 'tema', 'autor', 'casa_inicial', 'current_house', 'tem_dados_api', 'ultima_sincronizacao']
    list_filter = ['tema', 'tipo', 'ano', 'casa_inicial', 'current_house', 'ultima_sincronizacao', 'created_at', 'updated_at']
    search_fields = ['tipo', 'numero', 'tema__nome', 'autor', 'ementa']
    ordering = ['tema__nome', 'ano', 'numero']
    readonly_fields = ['created_at', 'updated_at', 'ultima_sincronizacao', 'erro_sincronizacao']
    
    fieldsets = (
        ('Identificação', {
            'fields': ('tipo', 'numero', 'ano')
        }),
        ('Organização', {
            'fields': ('tema',)
        }),
        ('Dados das APIs', {
            'fields': ('sf_id', 'cd_id', 'autor', 'data_apresentacao', 'casa_inicial', 'ementa', 'current_house')
        }),
        ('Sincronização', {
            'fields': ('ultima_sincronizacao', 'erro_sincronizacao'),
            'classes': ('collapse',)
        }),
        ('Metadados', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def identificador_completo(self, obj):
        """
        Retorna o identificador completo da proposição para exibição na lista.
        """
        return obj.identificador_completo
    identificador_completo.short_description = 'Identificador'
    identificador_completo.admin_order_field = 'tipo'
    
    def tem_dados_api(self, obj):
        """
        Indica se a proposição possui dados das APIs.
        """
        return obj.tem_dados_api
    tem_dados_api.boolean = True
    tem_dados_api.short_description = 'Dados API'


@admin.register(SenadoActivityHistory)
class SenadoActivityHistoryAdmin(admin.ModelAdmin):
    """
    Configuração do admin para o modelo SenadoActivityHistory.
    
    Permite gerenciar o histórico de atividades de proposições no Senado Federal.
    """
    
    list_display = ['proposicao', 'id_informe', 'data', 'colegiado_sigla', 'ente_administrativo_sigla', 'sigla_situacao_iniciada']
    list_filter = ['data', 'colegiado_sigla', 'ente_administrativo_sigla', 'sigla_situacao_iniciada', 'created_at']
    search_fields = ['proposicao__identificador_completo', 'descricao', 'colegiado_nome', 'ente_administrativo_nome']
    ordering = ['proposicao', '-data', '-id_informe']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'data'
    
    fieldsets = (
        ('Proposição', {
            'fields': ('proposicao',)
        }),
        ('Informações do Informe', {
            'fields': ('id_informe', 'data', 'descricao')
        }),
        ('Colegiado', {
            'fields': ('colegiado_codigo', 'colegiado_casa', 'colegiado_sigla', 'colegiado_nome'),
            'classes': ('collapse',)
        }),
        ('Ente Administrativo', {
            'fields': ('ente_administrativo_id', 'ente_administrativo_casa', 'ente_administrativo_sigla', 'ente_administrativo_nome'),
            'classes': ('collapse',)
        }),
        ('Situação', {
            'fields': ('id_situacao_iniciada', 'sigla_situacao_iniciada'),
            'classes': ('collapse',)
        }),
        ('Metadados', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(CamaraActivityHistory)
class CamaraActivityHistoryAdmin(admin.ModelAdmin):
    """
    Configuração do admin para o modelo CamaraActivityHistory.
    
    Permite gerenciar o histórico de atividades de proposições na Câmara dos Deputados.
    """
    
    list_display = ['proposicao', 'sequencia', 'data_hora', 'sigla_orgao', 'descricao_tramitacao', 'cod_tipo_tramitacao']
    list_filter = ['data_hora', 'sigla_orgao', 'cod_tipo_tramitacao', 'ambito', 'created_at']
    search_fields = ['proposicao__identificador_completo', 'despacho', 'descricao_tramitacao', 'descricao_situacao']
    ordering = ['proposicao', '-data_hora', '-sequencia']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'data_hora'
    
    fieldsets = (
        ('Proposição', {
            'fields': ('proposicao',)
        }),
        ('Informações da Tramitação', {
            'fields': ('sequencia', 'data_hora', 'sigla_orgao', 'uri_orgao', 'uri_ultimo_relator')
        }),
        ('Detalhes da Tramitação', {
            'fields': ('regime', 'descricao_tramitacao', 'cod_tipo_tramitacao', 'despacho')
        }),
        ('Situação', {
            'fields': ('descricao_situacao', 'cod_situacao'),
            'classes': ('collapse',)
        }),
        ('Informações Adicionais', {
            'fields': ('url', 'ambito', 'apreciacao'),
            'classes': ('collapse',)
        }),
        ('Metadados', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
