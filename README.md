# MorseLink — Decodificador de Código Morse Accesible (AFND)

Aplicación con interfaz gráfica desarrollada en Python que implementa un **Autómata Finito No Determinista (AFND)**. El sistema modela la 
captura de código Morse mediante pulsador único para usuarios con movilidad reducida, resolviendo la incertidumbre temporal mediante la evaluación
concurrente de múltiples ramas activas.

---

## Características y Fundamentos Teóricos

- **Modelo Formal:** Definición matemática de la 5-tupla $M = (Q, \Sigma, \delta, q_0, F)$ con ramificaciones no deterministas y ciclos.
- **Evaluación Concurrente:** Procesamiento de múltiples estados activos en paralelo ante cada pulso recibido.
- **Interfaz Interactiva:** Captura por pulsador temporizado (toque corto/prolongado), avance paso a paso, procesamiento completo y reinicio.
- **Validación Formal:** Aceptación si al menos una rama activa converge en un estado de aceptación ($F \cap Q_{activos} \neq \emptyset$).

---

## Tecnologías y Prerrequisitos

- **Python 3.10 o superior**
- Entorno de ejecución estándar (incluye soporte para librerías GUI locales)

---

## Instalación y Ejecución

1. **Clonar el repositorio:**
   ```bash
   git clone [https://github.com/LuM-343/MorseLink.git](https://github.com/LuM-343/MorseLink.git)
   cd MorseLink
Ejecutar la interfaz gráfica principal:
  python "UI USUARIO.py"

Ejecutar la suite de pruebas del motor en consola:
  python motor_ANDF_Braille.py

👥 Equipo de Desarrollo
Andres Sebastián Aguilón Cardona — Dev 1: Backend Core y Motor Lógico AFND

Carlos Andrés Cholotío Mendoza — Dev 2: Frontend GUI y Manejo de Eventos

Luis Manuel Velásquez Gonsález — Dev 3: Representación Gráfica e Integración

Dan Mahli Soberanis Galindo — Dev 4: QA, Documentación Técnica y Control de Entregables

Moshé Arenz Pelaez Virula — Control y Pruebas
