from django.contrib import admin
from .models import Eixo, Tema, Proposicao


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
    
    list_display = ['identificador_completo', 'tema', 'autor', 'casa_inicial', 'tem_dados_api', 'ultima_sincronizacao']
    list_filter = ['tema', 'tipo', 'ano', 'casa_inicial', 'ultima_sincronizacao', 'created_at', 'updated_at']
    search_fields = ['tipo', 'numero', 'tema__nome', 'autor']
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
            'fields': ('sf_id', 'cd_id', 'autor', 'data_apresentacao', 'casa_inicial')
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
