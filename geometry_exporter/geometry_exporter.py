# -*- coding: utf-8 -*-
"""
/***************************************************************************
 GeometryExporter
                                 Um plugin do QGIS
 Exporta a geometria de feições para WKT, EWKT, GeoJSON, GML, KML, GeoHash,
 GeoPackage e ESRI Shapefile.
                             -------------------
        início               : 19-11-2015
        copyright            : (C) 2015 por Juergen Weichand
        email                : juergen@weichand.de
 ***************************************************************************/
"""

import os
import os.path
import webbrowser
from osgeo import ogr

from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication
from qgis.PyQt.QtWidgets import QAction, QMessageBox, QFileDialog, QPushButton
from qgis.PyQt.QtGui import QIcon
from qgis.core import (
    QgsProject,
    QgsCoordinateTransform,
    QgsGeometry,
    QgsCoordinateReferenceSystem,
    QgsVectorFileWriter,
    Qgis
)

# Tradutor interno (pt-BR / en / es)
from .i18n import Translator

# Compatibilidade QGIS 3.x e 4.x para níveis de mensagem
try:
    MSG_SUCCESS = Qgis.MessageLevel.Success
    MSG_WARNING = Qgis.MessageLevel.Warning
    MSG_CRITICAL = Qgis.MessageLevel.Critical
except AttributeError:
    MSG_SUCCESS = Qgis.Success
    MSG_WARNING = Qgis.Warning
    MSG_CRITICAL = Qgis.Critical


def point_to_geohash(lon, lat, precision=12):
    """Calcula a string GeoHash para um ponto (longitude, latitude)."""
    base32 = '0123456789bcdefghjkmnpqrstuvwxyz'
    lat_interval = [-90.0, 90.0]
    lon_interval = [-180.0, 180.0]
    geohash = []
    bits = [16, 8, 4, 2, 1]
    bit = 0
    ch = 0
    even = True

    while len(geohash) < precision:
        if even:
            mid = (lon_interval[0] + lon_interval[1]) / 2
            if lon >= mid:
                ch |= bits[bit]
                lon_interval[0] = mid
            else:
                lon_interval[1] = mid
        else:
            mid = (lat_interval[0] + lat_interval[1]) / 2
            if lat >= mid:
                ch |= bits[bit]
                lat_interval[0] = mid
            else:
                lat_interval[1] = mid

        even = not even
        if bit < 4:
            bit += 1
        else:
            geohash.append(base32[ch])
            bit = 0
            ch = 0

    return "".join(geohash)


class GeometryExporter:
    """Implementação do Plugin QGIS Geometry Exporter."""

    def __init__(self, iface, forced_locale=None):
        """Construtor.

        :param iface: Interface do QGIS.
        :param forced_locale: (Opcional) Código do idioma forçado.
                              Ex.: 'en', 'es', 'pt'.
                              Se None, detecta automaticamente do QGIS.
        """
        self.iface = iface
        self.plugin_dir = os.path.dirname(__file__)

        # -----------------------------------------------------------
        # Define o idioma: forçado ou automático
        # -----------------------------------------------------------
        if forced_locale:
            locale = forced_locale
        else:
            locale = QSettings().value('locale/userLocale', 'pt')

        self.i18n = Translator(locale)

        # (Opcional) Carrega arquivo .qm do Qt, se existir
        locale_short = (locale or 'pt')[:2]
        locale_path = os.path.join(
            self.plugin_dir, 'i18n', f'GeometryExporter_{locale_short}.qm')
        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        self.dlg = None
        self.actions = []
        self.menu = self.i18n.tr('menu_name')

        self.toolbar = self.iface.addToolBar('GeometryExporter')
        self.toolbar.setObjectName('GeometryExporter')

        self.feature = None
        self.layer = None
        self.layer_crs = None

    # ------------------------------------------------------------------
    def tr(self, key, **kwargs):
        """Atalho para self.i18n.tr()."""
        return self.i18n.tr(key, **kwargs)

    # ------------------------------------------------------------------
    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):

        icon = QIcon(icon_path) if (icon_path and os.path.exists(icon_path)) else QIcon()
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToVectorMenu(self.menu, action)

        self.actions.append(action)
        return action

    # ------------------------------------------------------------------
    def initGui(self):
        from .geometry_exporter_dialog import GeometryExporterDialog
        self.dlg = GeometryExporterDialog(i18n=self.i18n)

        existing_items = [self.dlg.cmbFormat.itemText(i)
                          for i in range(self.dlg.cmbFormat.count())]
        if "GeoPackage" not in existing_items:
            self.dlg.cmbFormat.addItem("GeoPackage")
        if "ESRI Shapefile" not in existing_items:
            self.dlg.cmbFormat.addItem("ESRI Shapefile")

        if not hasattr(self.dlg, 'btnSaveFile'):
            self.dlg.btnSaveFile = QPushButton(
                self.tr('save_button'), self.dlg)
            parent_layout = self.dlg.btnCopy.parentWidget().layout()
            if parent_layout:
                parent_layout.addWidget(self.dlg.btnSaveFile)

        icon_path = os.path.join(self.plugin_dir, 'geometry_exporter.svg')
        if not os.path.exists(icon_path):
            icon_path = os.path.join(self.plugin_dir, 'icon.png')

        self.add_action(
            icon_path,
            text=self.tr('plugin_name'),
            callback=self.run,
            add_to_menu=True,
            add_to_toolbar=True,
            parent=self.iface.mainWindow())

        help_icon_path = os.path.join(
            self.plugin_dir, 'geometry_exporter_help.svg')
        if not os.path.exists(help_icon_path):
            help_icon_path = icon_path

        self.add_action(
            help_icon_path,
            text=self.tr('help'),
            callback=self.open_help,
            add_to_menu=True,
            add_to_toolbar=False,
            parent=self.iface.mainWindow())

        self.dlg.cmbFormat.currentIndexChanged.connect(self.populate)
        self.dlg.cmbConversion.currentIndexChanged.connect(self.populate)
        self.dlg.proj.crsChanged.connect(self.populate)
        self.dlg.btnCopy.clicked.connect(self.on_copy_clicked)
        self.dlg.btnSaveFile.clicked.connect(self.on_save_file_clicked)

    # ------------------------------------------------------------------
    def unload(self):
        for action in self.actions:
            self.iface.removePluginVectorMenu(
                self.i18n.tr('menu_name'), action)
            self.iface.removeToolBarIcon(action)
        del self.toolbar

    def open_help(self):
        """Abre a documentação HTML do plugin no navegador padrão.
    
        Grava o idioma atual em help/lang.js para que o HTML leia
        e se traduza automaticamente, sem depender de hash ou navegador.
        """
        help_dir = os.path.join(self.plugin_dir, 'help')
        help_path = os.path.join(help_dir, 'index.html')
    
        if not os.path.exists(help_path):
            QMessageBox.warning(
                self.iface.mainWindow(),
                self.tr('plugin_name'),
                self.tr('help_not_found', path=help_path)
            )
            return
    
        # Descobre o idioma atual do plugin
        lang = getattr(self.i18n, 'lang', 'en')
        print(f"[GeometryExporter] Idioma atual: {lang}")
    
        # Grava o idioma em help/lang.js
        try:
            lang_js_path = os.path.join(help_dir, 'lang.js')
            with open(lang_js_path, 'w', encoding='utf-8') as f:
                f.write(f"window.__LANG__ = '{lang}';\n")
            print(f"[GeometryExporter] Escrito: {lang_js_path}")
        except Exception as e:
            print(f"[GeometryExporter] Erro ao gravar lang.js: {e}")
    
        # Abre o HTML
        url = f"file:///{help_path}"
        print(f"[GeometryExporter] Abrindo: {url}")
        webbrowser.open(url)

    # ------------------------------------------------------------------
    def on_copy_clicked(self):
        text = self.dlg.txtGeometryExport.toPlainText()
        if text:
            self.iface.messageBar().pushMessage(
                self.tr('plugin_name'),
                self.tr('copy_success'),
                level=MSG_SUCCESS,
                duration=3
            )

    # ------------------------------------------------------------------
    def on_save_file_clicked(self):
        if not self.layer or not self.feature:
            return

        fmt = self.dlg.cmbFormat.currentText()
        ext_map = {
            'GeoPackage': ('GeoPackage (*.gpkg)', 'GPKG'),
            'ESRI Shapefile': ('ESRI Shapefile (*.shp)', 'ESRI Shapefile'),
            'KML': ('KML (*.kml)', 'KML'),
            'GeoJSON': ('GeoJSON (*.geojson)', 'GeoJSON'),
            'GML 2': ('GML (*.gml)', 'GML'),
            'GML 3': ('GML (*.gml)', 'GML')
        }

        if fmt in ext_map:
            filter_str, driver_name = ext_map[fmt]
            filename, _ = QFileDialog.getSaveFileName(
                self.dlg, self.tr('save_feature_title'), "", filter_str
            )

            if not filename:
                return

            target_crs = self.dlg.proj.crs()
            options = QgsVectorFileWriter.SaveVectorOptions()
            options.driverName = driver_name
            options.fileEncoding = "UTF-8"
            options.onlySelectedFeatures = True

            if fmt == 'KML':
                options.ct = QgsCoordinateTransform(
                    self.layer_crs,
                    QgsCoordinateReferenceSystem("EPSG:4326"),
                    QgsProject.instance()
                )
            elif target_crs.isValid() and target_crs != self.layer_crs:
                options.ct = QgsCoordinateTransform(
                    self.layer_crs, target_crs, QgsProject.instance()
                )

            res = QgsVectorFileWriter.writeAsVectorFormatV3(
                self.layer,
                filename,
                QgsProject.instance().transformContext(),
                options
            )

            error = res[0]
            message = res[1]

            if error == QgsVectorFileWriter.NoError:
                self.iface.messageBar().pushMessage(
                    self.tr('plugin_name'),
                    self.tr('export_success', filename=filename),
                    level=MSG_SUCCESS,
                    duration=4
                )
            else:
                QMessageBox.critical(
                    self.dlg,
                    self.tr('export_error_title'),
                    self.tr('export_error', message=message)
                )
        else:
            filename, _ = QFileDialog.getSaveFileName(
                self.dlg,
                self.tr('save_text_title'),
                "",
                self.tr('text_file_filter')
            )
            if filename:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(self.dlg.txtGeometryExport.toPlainText())
                self.iface.messageBar().pushMessage(
                    self.tr('plugin_name'),
                    self.tr('text_save_success', filename=filename),
                    level=MSG_SUCCESS,
                    duration=4
                )

    # ------------------------------------------------------------------
    def run(self):
        self.layer = self.iface.activeLayer()

        if not self.layer:
            QMessageBox.critical(
                self.iface.mainWindow(),
                self.tr('error_title'),
                self.tr('error_no_layer')
            )
            return

        if self.layer.selectedFeatureCount() != 1:
            QMessageBox.critical(
                self.iface.mainWindow(),
                self.tr('error_title'),
                self.tr('error_no_feature')
            )
            return

        self.feature = list(self.layer.getSelectedFeatures())[0]
        self.layer_crs = self.layer.crs()

        self.dlg.proj.setCrs(self.layer_crs)
        self.dlg.show()
        self.populate()

    # ------------------------------------------------------------------
    def export_ogr_format(self, geom, format_type):
        try:
            if format_type == 'KML':
                target_crs = self.dlg.proj.crs()
                crs_wgs84 = QgsCoordinateReferenceSystem("EPSG:4326")

                geom_kml = QgsGeometry(geom)
                if target_crs != crs_wgs84 and target_crs.isValid():
                    trans = QgsCoordinateTransform(
                        target_crs, crs_wgs84, QgsProject.instance()
                    )
                    geom_kml.transform(trans)

                ogr_geom = ogr.CreateGeometryFromWkt(geom_kml.asWkt())
                if ogr_geom:
                    return ogr_geom.ExportToKML()

            ogr_geom = ogr.CreateGeometryFromWkt(geom.asWkt())
            if ogr_geom:
                if format_type == 'GML 2':
                    return ogr_geom.ExportToGML(['FORMAT=GML2'])
                elif format_type == 'GML 3':
                    return ogr_geom.ExportToGML(['FORMAT=GML3'])
        except Exception:
            pass

        return geom.asWkt()

    # ------------------------------------------------------------------
    def populate(self):
        if not self.feature or not self.feature.hasGeometry():
            return

        geom = QgsGeometry(self.feature.geometry())
        target_crs = self.dlg.proj.crs()

        if target_crs.isValid() and target_crs != self.layer_crs:
            transform = QgsCoordinateTransform(
                self.layer_crs, target_crs, QgsProject.instance()
            )
            geom.transform(transform)

        conversion = self.dlg.cmbConversion.currentText()
        if conversion in ('Envelope', 'Retângulo Envolvente', 'Rectángulo Envolvente'):
            geom = QgsGeometry.fromRect(geom.boundingBox())
        elif conversion in ('Centroid', 'Centroide'):
            geom = geom.centroid()
        elif conversion in ('Boundary', 'Limite/Fronteira', 'Límite/Frontera'):
            geom = geom.boundary()
        elif conversion in ('ConvexHull', 'Envoltória Convexa', 'Envolvente Convexa'):
            geom = geom.convexHull()

        fmt = self.dlg.cmbFormat.currentText()
        geom_export = ''

        if fmt in ['GML 2', 'GML 3', 'KML']:
            geom_export = self.export_ogr_format(geom, fmt)
        elif fmt in ['GeoJSON', 'GeoPackage', 'ESRI Shapefile']:
            geom_export = geom.asJson()
        elif fmt == 'GeoHash':
            crs_wgs84 = QgsCoordinateReferenceSystem("EPSG:4326")
            if target_crs != crs_wgs84 and target_crs.isValid():
                trans = QgsCoordinateTransform(
                    target_crs, crs_wgs84, QgsProject.instance()
                )
                geom_gh = QgsGeometry(geom)
                geom_gh.transform(trans)
                pt = geom_gh.centroid().asPoint()
            else:
                pt = geom.centroid().asPoint()
            geom_export = point_to_geohash(pt.x(), pt.y(), precision=12)
        elif fmt == 'EWKT':
            srid = target_crs.postgisSrid() if target_crs.isValid() else 0
            if srid > 0:
                geom_export = f"SRID={srid};{geom.asWkt()}"
            else:
                geom_export = geom.asWkt()
        else:
            geom_export = geom.asWkt()

        if target_crs.isValid():
            auth_id = target_crs.authid() if target_crs.authid() \
                else f"EPSG:{target_crs.postgisSrid()}"
            crs_title = f"{auth_id} - {target_crs.description()}"
        else:
            crs_title = self.tr('crs_unknown')

        full_output = f"{crs_title}\n\n{geom_export}"
        self.dlg.txtGeometryExport.setText(full_output)
        