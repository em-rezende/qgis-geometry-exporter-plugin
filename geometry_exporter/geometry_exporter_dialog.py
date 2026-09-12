# -*- coding: utf-8 -*-
"""
/***************************************************************************
 GeometryExporterDialog
                                 Um plugin do QGIS
 Diálogo principal do Exportador de Geometria.
                             -------------------
        início               : 19-11-2015
        copyright            : (C) 2015 por Juergen Weichand
        email                : juergen@weichand.de
 ***************************************************************************/
"""

import os

from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import QDialog, QApplication

# Tradutor interno (pt-BR / en / es)
from .i18n import Translator


# Carrega o arquivo .ui gerado pelo Qt Designer
FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'geometry_exporter_dialog_base.ui'))


class GeometryExporterDialog(QDialog, FORM_CLASS):
    """Diálogo principal do plugin Geometry Exporter."""

    def __init__(self, parent=None, i18n=None):
        """Construtor.

        :param parent: Widget pai (opcional).
        :param i18n: Instância de Translator (opcional).
                     Se não for passado, cria um padrão em português.
        """
        super(GeometryExporterDialog, self).__init__(parent)
        self.setupUi(self)

        # ------------------------------------------------------------------
        # Tradutor: usa o que foi passado ou cria um padrão pt-BR
        # ------------------------------------------------------------------
        self.i18n = i18n or Translator('pt')

        # ------------------------------------------------------------------
        # Aplica os textos traduzidos aos widgets do diálogo
        # ------------------------------------------------------------------
        self.setWindowTitle(self.i18n.tr('window_title'))

        # Botão Copiar
        if hasattr(self, 'btnCopy'):
            self.btnCopy.setText(self.i18n.tr('copy_button'))
            self.btnCopy.clicked.connect(self.copy_to_clipboard)

        # ComboBox de conversão (mantém os textos internos em inglês,
        # mas exibe traduzidos para o usuário)
        if hasattr(self, 'cmbConversion'):
            self.cmbConversion.setItemText(0, self.i18n.tr('conversion_none'))
            self.cmbConversion.setItemText(1, self.i18n.tr('conversion_envelope'))
            self.cmbConversion.setItemText(2, self.i18n.tr('conversion_centroid'))
            self.cmbConversion.setItemText(3, self.i18n.tr('conversion_convexhull'))
            self.cmbConversion.setItemText(4, self.i18n.tr('conversion_boundary'))

    # ----------------------------------------------------------------------
    # Ações
    # ----------------------------------------------------------------------
    def copy_to_clipboard(self):
        """Copia o conteúdo do texto exportado para a área de transferência."""
        text = self.txtGeometryExport.toPlainText()
        if text:
            QApplication.clipboard().setText(text)

    # ----------------------------------------------------------------------
    # Utilitário: permite alterar o idioma em tempo de execução
    # ----------------------------------------------------------------------
    def retranslate_ui(self, i18n=None):
        """Reaplica as traduções na interface.

        Útil se você quiser permitir que o usuário troque o idioma
        sem reiniciar o QGIS.
        """
        if i18n is not None:
            self.i18n = i18n

        self.setWindowTitle(self.i18n.tr('window_title'))

        if hasattr(self, 'btnCopy'):
            self.btnCopy.setText(self.i18n.tr('copy_button'))

        if hasattr(self, 'btnSaveFile'):
            self.btnSaveFile.setText(self.i18n.tr('save_button'))

        if hasattr(self, 'cmbConversion'):
            self.cmbConversion.setItemText(0, self.i18n.tr('conversion_none'))
            self.cmbConversion.setItemText(1, self.i18n.tr('conversion_envelope'))
            self.cmbConversion.setItemText(2, self.i18n.tr('conversion_centroid'))
            self.cmbConversion.setItemText(3, self.i18n.tr('conversion_convexhull'))
            self.cmbConversion.setItemText(4, self.i18n.tr('conversion_boundary'))
            