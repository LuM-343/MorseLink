class MotorAFND:
    def __init__(self):
        """Inicializa la tupla formal y la tabla de transiciones."""
        self.alfabeto = {'.', '-'}
        self.estados_aceptacion = {'q0', 'q4', 'q5', 'q6'}
        self.estados_activos = {'q0'}  # Arranca en el estado inicial
        
        # Diccionario para la ramificación no determinista
        self.transiciones = {
            'q0': {'.': {'q0', 'q1'}, '-': {'q2'}},
            'q1': {                   '-': {'q4'}},  # Sin ruta para '.'
            'q2': {'.': {'q5'},       '-': {'q6'}},
            'q4': {'.': {'q0', 'q1'}, '-': {'q2'}},
            'q5': {'.': {'q0', 'q1'}, '-': {'q2'}},
            'q6': {'.': {'q0', 'q1'}, '-': {'q2'}}
        }

    def avanzarPaso(self, simbolo):
        """Procesa un símbolo y avanza todas las ramas activas."""
        if simbolo not in self.alfabeto:
            raise ValueError("Símbolo inválido.")

        nuevos_estados = set()
        for estado in self.estados_activos:
            if simbolo in self.transiciones.get(estado, {}):
                nuevos_estados |= self.transiciones[estado][simbolo]
        
        self.estados_activos = nuevos_estados
        return self.estados_activos

    def procesarCadena(self, cadena):
        """Evalúa una secuencia completa (útil para batería de pruebas)."""
        self.reiniciar()
        for sim in cadena:
            self.avanzarPaso(sim)
        return self.evaluarVeredicto()

    def evaluarVeredicto(self):
        """Retorna True si hay rutas válidas en estados de aceptación."""
        return bool(self.estados_activos & self.estados_aceptacion)

    def reiniciar(self):
        """Restablece el autómata al estado inicial."""
        self.estados_activos = {'q0'}

    def obtenerEstadosActivos(self):
        """Retorna los nodos activos para actualizar la GUI."""
        return self.estados_activos


if __name__ == "__main__":
    # Prueba rápida de funcionamiento
    motor = MotorAFND()
    
    # Prueba con cadena aceptada: [.-] (letra A)
    resultado = motor.procesarCadena(".-")
    print(f"Cadena '.-': {'Aceptada' if resultado else 'Rechazada'} | Activos: {motor.obtenerEstadosActivos()}")
    
    # Prueba con cadena rechazada: [-]
    resultado = motor.procesarCadena("-")
    print(f"Cadena '-': {'Aceptada' if resultado else 'Rechazada'} | Activos: {motor.obtenerEstadosActivos()}")