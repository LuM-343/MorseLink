import sys
import time

from PyQt6.QtCore import Qt, QEvent
from PyQt6.QtGui import QFont, QKeyEvent
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton, QLineEdit, QFrame, QDialog, QSizePolicy
)

from motor_ANDF_Braille import MotorAFND

UMBRAL_PULSADOR_MS = 300

TABLA_MORSE = {
    ".-": "A", "-...": "B", "-.-.": "C", "-..": "D", ".": "E",
    "..-.": "F", "--.": "G", "....": "H", "..": "I", ".---": "J",
    "-.-": "K", ".-..": "L", "--": "M", "-.": "N", "---": "O",
    ".--.": "P", "--.-": "Q", ".-.": "R", "...": "S", "-": "T",
    "..-": "U", "...-": "V", ".--": "W", "-..-": "X", "-.--": "Y",
    "--..": "Z",
}
ORDEN_ESTADOS = ["q0", "q1", "q2", "q4", "q5", "q6"]

PALETA_CLARA = {
    "fondo": "#f5f3ee",
    "panel": "#ffffff",
    "borde": "#d8d3c7",
    "texto": "#2b2822",
    "texto_secundario": "#7a7468",
    "acento": "#c98a2b",
    "acento_hover": "#b87a1f",
    "acento_texto": "#ffffff",
    "exito": "#2f9e5c",
    "peligro": "#c9432b",
    "info": "#2b7fa6",
    "estado_inactivo": "#e3ded2",
    "estado_activo": "#c98a2b",
    "estado_final": "#2b7fa6",
}

PALETA_OSCURA = {
    "fondo": "#1c1b19",
    "panel": "#262420",
    "borde": "#3a372f",
    "texto": "#f0ece1",
    "texto_secundario": "#a39c8a",
    "acento": "#e0a53c",
    "acento_hover": "#f0b552",
    "acento_texto": "#1c1b19",
    "exito": "#4cc484",
    "peligro": "#e2624a",
    "info": "#4fa8d8",
    "estado_inactivo": "#33312b",
    "estado_activo": "#e0a53c",
    "estado_final": "#4fa8d8",
}


def construir_qss(p):
    return f"""
    QMainWindow, QWidget#raiz {{
        background-color: {p['fondo']};
    }}
    QLabel {{
        color: {p['texto']};
    }}
    QLabel#titulo {{
        font-size: 26px;
        font-weight: 700;
        letter-spacing: 1px;
    }}
    QLabel#subtitulo, QLabel#etiquetaSeccion, QLabel#ayuda {{
        color: {p['texto_secundario']};
        font-size: 12px;
    }}
    QLabel#etiquetaSeccion {{
        font-size: 11px;
        font-weight: 700;
    }}
    QFrame#panel {{
        background-color: {p['panel']};
        border: 1px solid {p['borde']};
        border-radius: 10px;
    }}
    QLabel#cadena {{
        background-color: {p['panel']};
        border: 1px solid {p['borde']};
        border-radius: 12px;
        padding: 18px;
        font-size: 22px;
        font-weight: 700;
        color: {p['texto_secundario']};
    }}
    QLabel#veredicto {{
        font-size: 17px;
        font-weight: 700;
    }}
    QPushButton {{
        border-radius: 8px;
        padding: 9px 14px;
        font-size: 13px;
        font-weight: 600;
        border: 1px solid {p['borde']};
        background-color: {p['panel']};
        color: {p['texto']};
    }}
    QPushButton:hover {{
        border: 1px solid {p['acento']};
    }}
    QPushButton#primario {{
        background-color: {p['acento']};
        color: {p['acento_texto']};
        border: none;
    }}
    QPushButton#primario:hover {{
        background-color: {p['acento_hover']};
    }}
    QPushButton#peligro {{
        color: {p['peligro']};
        border: 1px solid {p['peligro']};
        background-color: transparent;
    }}
    QPushButton#peligroSolido {{
        background-color: {p['peligro']};
        color: white;
        border: none;
    }}
    QPushButton#info {{
        background-color: {p['info']};
        color: white;
        border: none;
    }}
    QPushButton#pulsador {{
        background-color: {p['acento']};
        color: {p['acento_texto']};
        border-radius: 65px;
        font-size: 14px;
        font-weight: 800;
        border: none;
    }}
    QPushButton#pulsador:pressed {{
        background-color: {p['acento_hover']};
        border: 3px solid {p['texto']};
    }}
    QLineEdit {{
        border: 1px solid {p['borde']};
        border-radius: 6px;
        padding: 8px;
        font-size: 15px;
        background-color: {p['panel']};
        color: {p['texto']};
    }}
    QLineEdit:focus {{
        border: 1px solid {p['acento']};
    }}
    QLabel#mensajeError {{
        color: {p['peligro']};
        font-size: 12px;
    }}
    """


class IndicadorEstado(QWidget):
    def __init__(self, nombre, es_aceptacion, paleta, parent=None):
        super().__init__(parent)
        self.nombre = nombre
        self.es_aceptacion = es_aceptacion
        self.paleta = paleta
        self.activo = False

        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(6)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.circulo = QLabel()
        self.circulo.setFixedSize(50, 50)
        self.circulo.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.etiqueta = QLabel(nombre)
        self.etiqueta.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.etiqueta.setFont(QFont("Consolas", 10, QFont.Weight.Bold))

        self.marca_final = QLabel("F" if es_aceptacion else "")
        self.marca_final.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.marca_final.setFont(QFont("Consolas", 9))

        layout.addWidget(self.circulo, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.etiqueta)
        layout.addWidget(self.marca_final)

        self.actualizar_paleta(paleta)

    def actualizar_paleta(self, paleta):
        self.paleta = paleta
        self.marca_final.setStyleSheet(f"color: {paleta['estado_final']};")
        self._repintar()

    def set_activo(self, activo):
        self.activo = activo
        self._repintar()

    def _repintar(self):
        p = self.paleta
        if self.activo:
            color = p["estado_final"] if self.es_aceptacion else p["estado_activo"]
            borde = "3px solid " + p["texto"]
        else:
            color = p["estado_inactivo"]
            borde = f"1px solid {p['borde']}"
        self.circulo.setStyleSheet(
            f"background-color: {color}; border-radius: 25px; border: {borde};"
        )


class DialogoSalir(QDialog):
    def __init__(self, paleta, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Salir")
        self.setFixedSize(460, 220)
        self.setStyleSheet(construir_qss(paleta))

        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 28, 28, 24)

        titulo = QLabel("¿Cerrar sesión de MorseLink?")
        titulo.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        titulo.setWordWrap(True)

        subtitulo = QLabel("Se perderá la cadena capturada actualmente.")
        subtitulo.setObjectName("subtitulo")
        subtitulo.setWordWrap(True)

        layout.addWidget(titulo)
        layout.addWidget(subtitulo)
        layout.addStretch()

        fila_botones = QHBoxLayout()
        fila_botones.addStretch()

        btn_cancelar = QPushButton("Cancelar")
        btn_cancelar.clicked.connect(self.reject)

        btn_salir = QPushButton("Sí, salir")
        btn_salir.setObjectName("peligroSolido")
        btn_salir.clicked.connect(self.accept)

        fila_botones.addWidget(btn_cancelar)
        fila_botones.addWidget(btn_salir)
        layout.addLayout(fila_botones)


class InterfazMorseLink(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MorseLink - Panel de Señales (AFND)")
        self.setMinimumSize(900, 800)

        self.motor = MotorAFND()
        self.cadena_acumulada = ""
        self.indice_paso = 0
        self._tiempo_presion = None
        self.tema_oscuro = True
        self.paleta = PALETA_OSCURA

        self.indicadores_estado = {}
        self._construir_layout()
        self.setStyleSheet(construir_qss(self.paleta))
        self._refrescar()

        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setFocus()

        QApplication.instance().installEventFilter(self)

        self.showFullScreen()

    def _construir_layout(self):
        raiz = QWidget()
        raiz.setObjectName("raiz")
        self.setCentralWidget(raiz)

        contenedor = QVBoxLayout(raiz)
        contenedor.setContentsMargins(24, 20, 24, 20)
        contenedor.setSpacing(6)

        header = QHBoxLayout()
        titulo = QLabel("MORSELINK")
        titulo.setObjectName("titulo")
        titulo.setFont(QFont("Consolas", 26, QFont.Weight.Bold))
        header.addWidget(titulo)
        header.addStretch()

        self.btn_tema = QPushButton("☀ claro")
        self.btn_tema.setFixedWidth(130)
        self.btn_tema.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.btn_tema.clicked.connect(self._alternar_tema)
        header.addWidget(self.btn_tema)
        contenedor.addLayout(header)

        subtitulo = QLabel("Panel de señales · captura de código Morse por pulsador único (AFND)")
        subtitulo.setObjectName("subtitulo")
        subtitulo.setFont(QFont("Segoe UI", 12))
        contenedor.addWidget(subtitulo)
        contenedor.addSpacing(12)

        etiqueta_cadena = QLabel("CADENA ACUMULADA")
        etiqueta_cadena.setObjectName("etiquetaSeccion")
        etiqueta_cadena.setFont(QFont("Consolas", 11, QFont.Weight.Bold))
        contenedor.addWidget(etiqueta_cadena)

        self.lbl_cadena = QLabel("· · ·  sin símbolos aún  · · ·")
        self.lbl_cadena.setObjectName("cadena")
        self.lbl_cadena.setFont(QFont("Consolas", 22, QFont.Weight.Bold))
        self.lbl_cadena.setAlignment(Qt.AlignmentFlag.AlignCenter)
        contenedor.addWidget(self.lbl_cadena)
        contenedor.addSpacing(14)

        etiqueta_estados = QLabel("ESTADOS ACTIVOS (Q_activos)")
        etiqueta_estados.setObjectName("etiquetaSeccion")
        etiqueta_estados.setFont(QFont("Consolas", 11, QFont.Weight.Bold))
        contenedor.addWidget(etiqueta_estados)

        panel_estados = QFrame()
        panel_estados.setObjectName("panel")
        fila_estados = QGridLayout(panel_estados)
        fila_estados.setContentsMargins(16, 16, 16, 16)
        fila_estados.setSpacing(16)
        for i in range(len(ORDEN_ESTADOS)):
            fila_estados.setColumnStretch(i, 1)
        for i, estado in enumerate(ORDEN_ESTADOS):
            es_aceptacion = estado in self.motor.estados_aceptacion
            indicador = IndicadorEstado(estado, es_aceptacion, self.paleta)
            fila_estados.addWidget(indicador, 0, i)
            self.indicadores_estado[estado] = indicador
        contenedor.addWidget(panel_estados)
        contenedor.addSpacing(12)

        self.lbl_veredicto = QLabel("ESPERANDO CADENA")
        self.lbl_veredicto.setObjectName("veredicto")
        self.lbl_veredicto.setFont(QFont("Consolas", 17, QFont.Weight.Bold))
        self.lbl_veredicto.setAlignment(Qt.AlignmentFlag.AlignCenter)
        contenedor.addWidget(self.lbl_veredicto)
        contenedor.addSpacing(8)

        fila_pulsador = QHBoxLayout()
        fila_pulsador.addStretch()
        self.btn_pulsador = QPushButton("⬤\nPULSADOR")
        self.btn_pulsador.setObjectName("pulsador")
        self.btn_pulsador.setFixedSize(130, 130)
        self.btn_pulsador.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        fila_pulsador.addWidget(self.btn_pulsador)
        fila_pulsador.addStretch()
        contenedor.addLayout(fila_pulsador)

        self.btn_pulsador.pressed.connect(self._iniciar_pulso)
        self.btn_pulsador.released.connect(self._finalizar_pulso)

        ayuda = QLabel(
            f"toque corto = punto  ·  toque prolongado (>{UMBRAL_PULSADOR_MS}ms) = raya\n"
            "también funciona con [espacio] sostenido, en cualquier parte de la ventana  ·  [Esc] para salir de pantalla completa"
        )
        ayuda.setObjectName("ayuda")
        ayuda.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ayuda.setFont(QFont("Segoe UI", 12))
        contenedor.addWidget(ayuda)
        contenedor.addSpacing(12)

        fila_manual = QHBoxLayout()
        fila_manual.addStretch()
        self.entrada_manual = QLineEdit()
        self.entrada_manual.setFixedWidth(100)
        self.entrada_manual.setFont(QFont("Consolas", 15))
        self.entrada_manual.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.entrada_manual.returnPressed.connect(self._agregar_simbolo_manual)
        fila_manual.addWidget(self.entrada_manual)

        btn_agregar = QPushButton("Agregar")
        btn_agregar.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        btn_agregar.clicked.connect(self._agregar_simbolo_manual)
        fila_manual.addWidget(btn_agregar)

        btn_borrar = QPushButton("⌫ Borrar último")
        btn_borrar.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        btn_borrar.clicked.connect(self._borrar_ultimo)
        fila_manual.addWidget(btn_borrar)
        fila_manual.addStretch()
        contenedor.addLayout(fila_manual)
        contenedor.addSpacing(12)

        fila_botones = QHBoxLayout()
        fila_botones.addStretch()

        btn_procesar = QPushButton("Procesar")
        btn_procesar.setObjectName("primario")
        btn_procesar.setFixedWidth(140)
        btn_procesar.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        btn_procesar.clicked.connect(self._procesar)
        fila_botones.addWidget(btn_procesar)

        btn_paso = QPushButton("Paso a paso")
        btn_paso.setObjectName("info")
        btn_paso.setFixedWidth(140)
        btn_paso.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        btn_paso.clicked.connect(self._paso_a_paso)
        fila_botones.addWidget(btn_paso)

        btn_reiniciar = QPushButton("Reiniciar")
        btn_reiniciar.setFixedWidth(140)
        btn_reiniciar.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        btn_reiniciar.clicked.connect(self._reiniciar)
        fila_botones.addWidget(btn_reiniciar)

        btn_salir = QPushButton("Salir")
        btn_salir.setObjectName("peligro")
        btn_salir.setFixedWidth(140)
        btn_salir.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        btn_salir.clicked.connect(self._salir)
        fila_botones.addWidget(btn_salir)

        fila_botones.addStretch()
        contenedor.addLayout(fila_botones)

        self.lbl_mensaje = QLabel("")
        self.lbl_mensaje.setObjectName("mensajeError")
        self.lbl_mensaje.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_mensaje.setFont(QFont("Segoe UI", 12))
        contenedor.addWidget(self.lbl_mensaje)
        contenedor.addStretch()

    def _alternar_tema(self):
        self.tema_oscuro = not self.tema_oscuro
        self.paleta = PALETA_OSCURA if self.tema_oscuro else PALETA_CLARA
        self.setStyleSheet(construir_qss(self.paleta))
        self.btn_tema.setText("☀ claro" if self.tema_oscuro else "🌙 oscuro")
        for indicador in self.indicadores_estado.values():
            indicador.actualizar_paleta(self.paleta)
        self._refrescar()

    def _iniciar_pulso(self):
        if self._tiempo_presion is not None:
            return
        self._tiempo_presion = time.time()
        self.btn_pulsador.setDown(True)

    def _finalizar_pulso(self):
        if self._tiempo_presion is None:
            return
        duracion_ms = (time.time() - self._tiempo_presion) * 1000
        self._tiempo_presion = None
        self.btn_pulsador.setDown(False)
        self._registrar_simbolo("." if duracion_ms < UMBRAL_PULSADOR_MS else "-")

    def eventFilter(self, obj, event):
        tipo = event.type()
        if tipo in (QEvent.Type.KeyPress, QEvent.Type.KeyRelease):
            if isinstance(event, QKeyEvent) and event.key() == Qt.Key.Key_Space and not event.isAutoRepeat():
                if tipo == QEvent.Type.KeyPress:
                    self._iniciar_pulso()
                else:
                    self._finalizar_pulso()
                return True
        return super().eventFilter(obj, event)

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key.Key_Escape:
            if self.isFullScreen():
                self.showNormal()
            else:
                self.showFullScreen()
        else:
            super().keyPressEvent(event)

    def _agregar_simbolo_manual(self):
        texto = self.entrada_manual.text().strip()
        if texto == "":
            self.lbl_mensaje.setText("Campo vacío: escribí un símbolo ('.' o '-') antes de agregarlo.")
            return
        invalidos = sorted(set(c for c in texto if c not in self.motor.alfabeto))
        if invalidos:
            self.lbl_mensaje.setText(f"Alfabeto formal Σ = {{'.', '-'}}. No permitido: {', '.join(invalidos)}")
            self.entrada_manual.clear()
            return
        self.lbl_mensaje.setText("")
        for simbolo in texto:
            self._registrar_simbolo(simbolo)
        self.entrada_manual.clear()

    def _borrar_ultimo(self):
        if not self.cadena_acumulada:
            return
        self.cadena_acumulada = self.cadena_acumulada[:-1]
        self.motor.procesarCadena(self.cadena_acumulada)
        self.indice_paso = len(self.cadena_acumulada)
        self._refrescar()

    def _registrar_simbolo(self, simbolo):
        self.cadena_acumulada += simbolo
        self.motor.procesarCadena(self.cadena_acumulada)
        self.indice_paso = len(self.cadena_acumulada)
        self._refrescar()

    def _procesar(self):
        if not self.cadena_acumulada:
            self.lbl_mensaje.setText("No hay ningún símbolo capturado todavía.")
            return
        self.lbl_mensaje.setText("")
        aceptada = self.motor.procesarCadena(self.cadena_acumulada)
        self.indice_paso = len(self.cadena_acumulada)
        self._refrescar()
        self._mostrar_veredicto(aceptada)

    def _paso_a_paso(self):
        if not self.cadena_acumulada:
            self.lbl_mensaje.setText("No hay ningún símbolo capturado todavía.")
            return
        self.lbl_mensaje.setText("")
        if self.indice_paso == 0:
            self.motor.reiniciar()
        if self.indice_paso >= len(self.cadena_acumulada):
            self.lbl_mensaje.setText("Ya se procesaron todos los símbolos. Reiniciá para repetir.")
            return
        simbolo = self.cadena_acumulada[self.indice_paso]
        self.motor.avanzarPaso(simbolo)
        self.indice_paso += 1
        self._refrescar_estados()
        if self.indice_paso == len(self.cadena_acumulada):
            self._mostrar_veredicto(self.motor.evaluarVeredicto())
        else:
            self.lbl_veredicto.setText(f"PASO {self.indice_paso}/{len(self.cadena_acumulada)} · símbolo '{simbolo}'")
            self.lbl_veredicto.setStyleSheet(f"color: {self.paleta['texto_secundario']};")

    def _mostrar_veredicto(self, aceptada):
        letra = TABLA_MORSE.get(self.cadena_acumulada, "?")
        if aceptada:
            self.lbl_veredicto.setText(f"✔ CADENA ACEPTADA  ≈ letra: {letra}")
            self.lbl_veredicto.setStyleSheet(f"color: {self.paleta['exito']};")
        else:
            self.lbl_veredicto.setText("✘ CADENA RECHAZADA")
            self.lbl_veredicto.setStyleSheet(f"color: {self.paleta['peligro']};")

    def _reiniciar(self):
        self.motor.reiniciar()
        self.cadena_acumulada = ""
        self.indice_paso = 0
        self.entrada_manual.clear()
        self.lbl_mensaje.setText("")
        self.lbl_veredicto.setText("ESPERANDO CADENA")
        self.lbl_veredicto.setStyleSheet(f"color: {self.paleta['texto_secundario']};")
        self._refrescar()

    def _salir(self):
        dialogo = DialogoSalir(self.paleta, self)
        if dialogo.exec() == QDialog.DialogCode.Accepted:
            self.close()

    def _refrescar(self):
        self.lbl_cadena.setText(self.cadena_acumulada if self.cadena_acumulada else "· · ·  sin símbolos aún  · · ·")
        self._refrescar_estados()

    def _refrescar_estados(self):
        activos = self.motor.obtenerEstadosActivos()
        for estado, indicador in self.indicadores_estado.items():
            indicador.set_activo(estado in activos)


def main():
    app = QApplication(sys.argv)
    ventana = InterfazMorseLink()
    ventana.show()
    sys.exit(app.exec())


main()