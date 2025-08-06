from django.contrib import admin
from .models import Tema, Proposicao, HistoricoAtualizacao


@admin.register(Tema)
class TemaAdmin(admin.ModelAdmin):
    """
    Configuração do admin para o modelo Tema.
    
    Permite gerenciar temas de interesse para organização das proposições legislativas.
    """
    
    list_display = ['nome', 'created_at', 'updated_at']
    list_filter = ['created_at', 'updated_at']
    search_fields = ['nome']
    ordering = ['nome']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('nome',)
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
    
    list_display = ['identificador_completo', 'tema', 'created_at', 'updated_at']
    list_filter = ['tema', 'tipo', 'ano', 'created_at', 'updated_at']
    search_fields = ['tipo', 'numero', 'tema__nome']
    ordering = ['tema__nome', 'ano', 'numero']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Identificação', {
            'fields': ('tipo', 'numero', 'ano')
        }),
        ('Organização', {
            'fields': ('tema',)
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


@admin.register(HistoricoAtualizacao)
class HistoricoAtualizacaoAdmin(admin.ModelAdmin):
    """
    Configuração do admin para o modelo HistoricoAtualizacao.
    
    Permite visualizar o histórico de atualizações das proposições legislativas.
    """
    
    list_display = ['proposicao', 'data_atualizacao']
    list_filter = ['data_atualizacao', 'proposicao__tema']
    search_fields = ['proposicao__tipo', 'proposicao__numero', 'proposicao__tema__nome']
    ordering = ['-data_atualizacao']
    readonly_fields = ['data_atualizacao']
    
    fieldsets = (
        ('Proposição', {
            'fields': ('proposicao',)
        }),
        ('Dados da Atualização', {
            'fields': ('dados_atualizados',)
        }),
        ('Metadados', {
            'fields': ('data_atualizacao',),
            'classes': ('collapse',)
        }),
    )
