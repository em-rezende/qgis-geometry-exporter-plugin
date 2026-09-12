# -*- coding: utf-8 -*-
"""
Módulo de internacionalização simples para o plugin Geometry Exporter.
Suporta: pt-BR, en, es.
"""

TRANSLATIONS = {
    'pt': {
        'plugin_name': 'Exportador de Geometria',
        'menu_name': '&Exportador de Geometria',
        'help': 'Ajuda',
        'window_title': 'Exportador de Geometria',
        'copy_button': 'Copiar para Área de Transferência',
        'save_button': 'Salvar em Arquivo',
        'conversion_none': 'Sem conversão',
        'conversion_envelope': 'Retângulo Envolvente',
        'conversion_centroid': 'Centroide',
        'conversion_convexhull': 'Envoltória Convexa',
        'conversion_boundary': 'Limite/Fronteira',
        'error_no_layer': 'Por favor, selecione uma camada!',
        'error_no_feature': 'Por favor, selecione exatamente uma feição!',
        'error_title': 'Erro',
        'copy_success': 'Geometria copiada para a área de transferência com sucesso!',
        'export_success': 'Feição exportada com sucesso: {filename}',
        'text_save_success': 'Texto salvo com sucesso em: {filename}',
        'export_error': 'Não foi possível salvar o arquivo:\n{message}',
        'export_error_title': 'Erro ao exportar',
        'save_feature_title': 'Salvar Feição como Arquivo',
        'save_text_title': 'Salvar Geometria em Texto',
        'text_file_filter': 'Arquivo de Texto (*.txt);;Todos os Arquivos (*.*)',
        'crs_unknown': 'SRC Desconhecido',
        'help_not_found': 'O arquivo de ajuda não foi encontrado em:\n{path}',
    },
    'en': {
        'plugin_name': 'Geometry Exporter',
        'menu_name': '&Geometry Exporter',
        'help': 'Help',
        'window_title': 'Geometry Exporter',
        'copy_button': 'Copy to Clipboard',
        'save_button': 'Save to File',
        'conversion_none': 'No conversion',
        'conversion_envelope': 'Envelope',
        'conversion_centroid': 'Centroid',
        'conversion_convexhull': 'Convex Hull',
        'conversion_boundary': 'Boundary',
        'error_no_layer': 'Please select a layer!',
        'error_no_feature': 'Please select exactly one feature!',
        'error_title': 'Error',
        'copy_success': 'Geometry copied to clipboard successfully!',
        'export_success': 'Feature exported successfully: {filename}',
        'text_save_success': 'Text saved successfully to: {filename}',
        'export_error': 'Could not save file:\n{message}',
        'export_error_title': 'Export Error',
        'save_feature_title': 'Save Feature as File',
        'save_text_title': 'Save Geometry as Text',
        'text_file_filter': 'Text File (*.txt);;All Files (*.*)',
        'crs_unknown': 'Unknown CRS',
        'help_not_found': 'Help file not found at:\n{path}',
    },
    'es': {
        'plugin_name': 'Exportador de Geometría',
        'menu_name': '&Exportador de Geometría',
        'help': 'Ayuda',
        'window_title': 'Exportador de Geometría',
        'copy_button': 'Copiar al Portapapeles',
        'save_button': 'Guardar en Archivo',
        'conversion_none': 'Sin conversión',
        'conversion_envelope': 'Rectángulo Envolvente',
        'conversion_centroid': 'Centroide',
        'conversion_convexhull': 'Envolvente Convexa',
        'conversion_boundary': 'Límite/Frontera',
        'error_no_layer': '¡Por favor, seleccione una capa!',
        'error_no_feature': '¡Por favor, seleccione exactamente una entidad!',
        'error_title': 'Error',
        'copy_success': '¡Geometría copiada al portapapeles con éxito!',
        'export_success': 'Entidad exportada con éxito: {filename}',
        'text_save_success': 'Texto guardado con éxito en: {filename}',
        'export_error': 'No se pudo guardar el archivo:\n{message}',
        'export_error_title': 'Error de Exportación',
        'save_feature_title': 'Guardar Entidad como Archivo',
        'save_text_title': 'Guardar Geometría como Texto',
        'text_file_filter': 'Archivo de Texto (*.txt);;Todos los Archivos (*.*)',
        'crs_unknown': 'SRC Desconocido',
        'help_not_found': 'Archivo de ayuda no encontrado en:\n{path}',
    },
}


class Translator:
    """Tradutor simples baseado em dicionário."""

    def __init__(self, locale='pt'):
        # Normaliza: 'pt_BR' -> 'pt', 'en_US' -> 'en', 'es_ES' -> 'es'
        locale = (locale or 'pt').lower().replace('-', '_')
        lang = locale.split('_')[0]

        # Fallback para inglês se o idioma não for suportado
        if lang not in TRANSLATIONS:
            lang = 'en'

        self.lang = lang
        self.strings = TRANSLATIONS[lang]

    def tr(self, key, **kwargs):
        """Retorna a string traduzida. Aceita formatação via kwargs."""
        text = self.strings.get(key, key)
        if kwargs:
            try:
                text = text.format(**kwargs)
            except (KeyError, IndexError):
                pass
        return text