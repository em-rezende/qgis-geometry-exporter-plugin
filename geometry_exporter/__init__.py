# -*- coding: utf-8 -*-
import os

# -----------------------------------------------------------
# Idioma forçado.
# - Em produção: use None (detecção automática pelo QGIS).
# - Para testes: defina a variável de ambiente GEOMETRY_EXPORTER_LOCALE
#   antes de abrir o QGIS. Ex.:
#     Windows:  set GEOMETRY_EXPORTER_LOCALE=en
#     Linux:    export GEOMETRY_EXPORTER_LOCALE=es
# -----------------------------------------------------------
FORCED_LOCALE = os.environ.get('GEOMETRY_EXPORTER_LOCALE', None)

def classFactory(iface):
    """Carrega a classe GeometryExporter do arquivo geometry_exporter."""
    from .geometry_exporter import GeometryExporter
    return GeometryExporter(iface, forced_locale=FORCED_LOCALE)
