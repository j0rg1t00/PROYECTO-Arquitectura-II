class Estado:
    
    NUEVO = "nuevo"
    LISTO = "listo
    EJECUCION = "ejecutando"
    BLOQUEADO = "bloqueado"
    TERMINADO = "terminado"
    EN_SO = "en_so"

class Proceso:
    def __init__(self, nombre, tiempo_llegada, secuencia_ejecucion):
        self.nombre = nombre
        self.tiempo_llegada = tiempo_llegada
        self.secuencia_ejecucion = secuencia_ejecucion
        self.secuencia_original = secuencia_ejecucion.copy()
        self.indice_actual = 0
        self.tiempo_restante_fase = 0
        self.tiempo_bloqueo_restante = 0
        self.estado = Estado.NUEVO
        self.veces_en_so = 0

    def obtener_fase_actual(self):
        if self.indice_actual < len(self.secuencia_ejecucion):
            return self.secuencia_ejecucion[self.indice_actual]
        return None

    def avanzar_fase(self):
        self.indice_actual += 1
        if self.indice_actual < len(self.secuencia_ejecucion):
            self.tiempo_restante_fase = self.secuencia_ejecucion[self.indice_actual][1]
        else:
            self.tiempo_restante_fase = 0

    def esta_terminado(self):
        return self.indice_actual >= len(self.secuencia_ejecucion)

    def calcular_tiempo_total_cpu(self):
        return sum(t for tipo, t in self.secuencia_original if tipo == 'CPU')

    def calcular_tiempo_total_es(self):
        return sum(t for tipo, t in self.secuencia_original if tipo == 'ES')

def validar_multiplo_10(valor, mensaje):
    while True:
        try:
            v = int(valor)
            if v >= 0 and v % 10 == 0:
                return v
        except:
            pass
        print(f"ERROR: {mensaje} debe ser múltiplo de 10 y mayor o igual a 0")
        try:
            valor = int(input(f"Ingrese nuevamente {mensaje}: "))
        except:
            valor = -1

class TablaProcesos:
    def __init__(self):
        self.tiempo_actual = 0
        self.columnas_tiempo = []
        self.datos = {k: [] for k in ['BLOQUEADOS', 'P1', 'P2', 'P3', 'P4', 'LISTO', 'SO']}
        self.procesos = []
        self.algoritmo = None
        self.quantum = 0
        self.eventos_log = []

    def log_evento(self, evento):
        self.eventos_log.append(f"t={self.tiempo_actual}: {evento}")

    def agregar_tiempo(self, incremento=10):
        self.tiempo_actual += incremento
        self.columnas_tiempo.append(self.tiempo_actual)
        for fila in self.datos:
            self.datos[fila].append('')

    def configurar_simulacion(self, algoritmo, quantum=0):
        self.algoritmo = algoritmo
        self.quantum = validar_multiplo_10(quantum, "el quantum") if quantum > 0 else 0
        self.procesos = []
        self.eventos_log = []

    def pedir_rafagas_proceso(self, nombre):
        rafagas = []
        i = 1
        print(f"\n--- Ráfagas para Proceso {nombre} ---")
        print("Ingrese las ráfagas alternando CPU y E/S")
        print("Todas las duraciones deben ser múltiplos de 10")
        print("Ingrese 0 en una ráfaga CPU para terminar el proceso")
        while True:
            try:
                duracion_cpu = int(input(f"{nombre} - Duración RÁFAGA CPU {i} (múltiplo de 10, 0 para terminar): "))
                duracion_cpu = validar_multiplo_10(duracion_cpu, "la duración de CPU")
                if duracion_cpu == 0:
                    break
                rafagas.append(('CPU', duracion_cpu))
                respuesta = input(f"¿{nombre} tiene ráfaga de E/S después de CPU {i}? (s/n): ").lower()
                if respuesta == 's':
                    duracion_es = int(input(f"{nombre} - Duración RÁFAGA E/S {i} (múltiplo de 10): "))
                    duracion_es = validar_multiplo_10(duracion_es, "la duración de E/S")
                    rafagas.append(('ES', duracion_es))
                else:
                    break
                i += 1
            except ValueError:
                print("ERROR: Por favor ingrese un número válido")
        return rafagas

    def agregar_proceso_manual(self, nombre):
        print(f"\n{'='*50}")
        print(f"CONFIGURANDO PROCESO {nombre}")
        print(f"{'='*50}")
        try:
            llegada = int(input(f"{nombre} - Tiempo de llegada: "))
            llegada = validar_multiplo_10(llegada, "el tiempo de llegada")
        except:
            print("ERROR: Tiempo de llegada inválido")
            return False
        rafagas = self.pedir_rafagas_proceso(nombre)
        if rafagas:
            proceso = Proceso(nombre, llegada, rafagas)
            self.procesos.append(proceso)
            print(f"✅ Proceso {nombre} creado con {len(rafagas)} ráfagas")
            secuencia_str = " → ".join([f"{tipo}({tiempo})" for tipo, tiempo in rafagas])
            print(f"   Secuencia: {secuencia_str}")
            return True
        else:
            print(f"ADVERTENCIA: Proceso {nombre} no se creó (sin ráfagas)")
            return False

    def agregar_proceso_predefinido(self, nombre, tiempo_llegada, rafagas):
        proceso = Proceso(nombre, tiempo_llegada, rafagas)
        self.procesos.append(proceso)

    def ejecutar_simulacion(self):
        if not self.procesos or not self.algoritmo:
            print("ERROR: Configura la simulación primero")
            return
        self.tiempo_actual = 0
        self.columnas_tiempo = []
        self.eventos_log = []
        for fila in self.datos: self.datos[fila] = []
        for i in range(20):
            self.agregar_tiempo()
        print(f"🚀 Ejecutando simulación {self.algoritmo}...")
        if self.algoritmo == 'FIFO':
            self._simular(alg='FIFO')
        elif self.algoritmo == 'RR':
            self._simular(alg='RR')
        print("✅ Simulación completada!")
        self.mostrar_tabla_interactiva()

    def _expandir_tabla_si_necesario(self, tiempo_simulacion):
        while tiempo_simulacion >= len(self.columnas_tiempo):
            self.agregar_tiempo()
            for fila in self.datos:
                if len(self.datos[fila])>0:
                    self.datos[fila][-1] = ''

    def _limpiar_filas_tiempo(self, tiempo_simulacion, filas=None):
        if filas is None:
            filas = ['BLOQUEADOS','P1','P2','P3','P4','LISTO','SO']
        for fila in filas:
            if fila in self.datos and tiempo_simulacion < len(self.datos[fila]):
                self._actualizar_tabla(fila, tiempo_simulacion, '')

    def _simular(self, alg='FIFO'):
        cola_listos, cola_bloqueados = [], []
        proceso_actual = None
        tiempo_quantum_restante = 0
        tiempo_simulacion = 0
        procesos_esperando_so_a_listo = []
        procesos_ordenados = sorted(self.procesos, key=lambda p: p.tiempo_llegada)
        for p in procesos_ordenados:
            if p.secuencia_ejecucion:
                p.tiempo_restante_fase = p.secuencia_ejecucion[0][1]
        while True:
            tiempo_actual = (tiempo_simulacion + 1) * 10
            self._expandir_tabla_si_necesario(tiempo_simulacion)
            self._limpiar_filas_tiempo(tiempo_simulacion)
            for proceso in procesos_esperando_so_a_listo[:]:
                proceso.estado = Estado.LISTO
                cola_listos.append(proceso)
                procesos_esperando_so_a_listo.remove(proceso)
                self.log_evento(f"{proceso.nombre} SO → LISTO")
            if cola_listos:
                nombres_listos = [p.nombre for p in cola_listos if p.estado == Estado.LISTO]
                if nombres_listos:
                    self._actualizar_tabla('LISTO', tiempo_simulacion, ', '.join(nombres_listos))
            for proceso in procesos_ordenados:
                if proceso.tiempo_llegada == tiempo_actual and proceso.estado == Estado.NUEVO:
                    proceso.veces_en_so += 1
                    proceso.estado = Estado.EN_SO
                    procesos_esperando_so_a_listo.append(proceso)
                    info_so = f"{proceso.veces_en_so}{proceso.nombre}"
                    self._actualizar_tabla('SO', tiempo_simulacion, info_so)
                    self.log_evento(f"{proceso.nombre} NUEVO → SO ({info_so})")
            procesos_desbloqueados = []
            for proceso in cola_bloqueados[:]:
                proceso.tiempo_bloqueo_restante -= 10
                if proceso.tiempo_bloqueo_restante <= 0:
                    procesos_desbloqueados.append(proceso)
            for proceso in procesos_desbloqueados:
                cola_bloqueados.remove(proceso)
                proceso.avanzar_fase()
                if not proceso.esta_terminado():
                    proceso.veces_en_so += 1
                    proceso.estado = Estado.EN_SO
                    procesos_esperando_so_a_listo.append(proceso)
                    info_so = f"{proceso.veces_en_so}{proceso.nombre}"
                    self._actualizar_tabla('SO', tiempo_simulacion, info_so)
                    self.log_evento(f"{proceso.nombre} BLOQUEADO → SO ({info_so})")
                    fase = proceso.obtener_fase_actual()
                    if fase:
                        proceso.tiempo_restante_fase = fase[1]
                else:
                    proceso.estado = Estado.TERMINADO
                    self.log_evento(f"{proceso.nombre} BLOQUEADO → TERMINADO")
            if alg == 'RR' and proceso_actual and tiempo_quantum_restante <= 0:
                if not proceso_actual.esta_terminado():
                    proceso_actual.estado = Estado.LISTO
                    cola_listos.append(proceso_actual)
                    self.log_evento(f"{proceso_actual.nombre} EXPROPIADO (Quantum agotado) → LISTO")
                    if cola_listos:
                        nombres_listos = [p.nombre for p in cola_listos if p.estado == Estado.LISTO]
                        if nombres_listos:
                            self._actualizar_tabla('LISTO', tiempo_simulacion, ', '.join(nombres_listos))
                proceso_actual = None
                tiempo_quantum_restante = 0
            if proceso_actual is None and cola_listos:
                proceso_actual = cola_listos.pop(0)
                proceso_actual.estado = Estado.EJECUCION
                tiempo_quantum_restante = self.quantum if alg == 'RR' else 0
                self.log_evento(f"{proceso_actual.nombre} LISTO → EJECUCIÓN" + (f" (Quantum: {self.quantum})" if alg=='RR' else ""))
            if proceso_actual:
                fase_actual = proceso_actual.obtener_fase_actual()
                if fase_actual and fase_actual[0] == 'CPU':
                    self._actualizar_tabla(proceso_actual.nombre, tiempo_simulacion, 'x')
                    proceso_actual.tiempo_restante_fase -= 10
                    if alg == 'RR':
                        tiempo_quantum_restante -= 10
                    if proceso_actual.tiempo_restante_fase <= 0:
                        proceso_actual.avanzar_fase()
                        nueva_fase = proceso_actual.obtener_fase_actual()
                        if nueva_fase:
                            if nueva_fase[0] == 'ES':
                                proceso_actual.estado = Estado.BLOQUEADO
                                proceso_actual.tiempo_bloqueo_restante = nueva_fase[1]
                                cola_bloqueados.append(proceso_actual)
                                self.log_evento(f"{proceso_actual.nombre} EJECUCIÓN → BLOQUEADO (E/S: {nueva_fase[1]})")
                                proceso_actual = None
                                tiempo_quantum_restante = 0
                            else:
                                proceso_actual.tiempo_restante_fase = nueva_fase[1]
                        else:
                            proceso_actual.estado = Estado.TERMINADO
                            self.log_evento(f"{proceso_actual.nombre} EJECUCIÓN → TERMINADO")
                            proceso_actual = None
                            tiempo_quantum_restante = 0
            if cola_listos:
                nombres_listos = [p.nombre for p in cola_listos if p.estado == Estado.LISTO]
                if nombres_listos:
                    self._actualizar_tabla('LISTO', tiempo_simulacion, ', '.join(nombres_listos))
            if cola_bloqueados:
                nombres_bloqueados = [p.nombre for p in cola_bloqueados]
                self._actualizar_tabla('BLOQUEADOS', tiempo_simulacion, ', '.join(nombres_bloqueados))
            tiempo_simulacion += 1
            if (all(p.estado == Estado.TERMINADO for p in self.procesos) and not cola_listos and not cola_bloqueados and proceso_actual is None and not procesos_esperando_so_a_listo):
                break
            if tiempo_simulacion > 500:
                print("ADVERTENCIA: Simulación detenida: tiempo máximo alcanzado")
                break

    def _actualizar_tabla(self, fila, columna, valor):
        if fila in self.datos and columna < len(self.datos[fila]):
            self.datos[fila][columna] = valor

    def mostrar_tabla(self, inicio_col=0, cols_visibles=6):
        if not self.columnas_tiempo:
            print("ERROR: La tabla está vacía.")
            return
        ancho_fila = 12
        ancho_col = 10
        fin_col = min(inicio_col + cols_visibles, len(self.columnas_tiempo))
        columnas_mostrar = self.columnas_tiempo[inicio_col:fin_col]
        if not columnas_mostrar:
            print("ERROR: No hay más columnas para mostrar")
            return
        ancho_total = ancho_fila + (ancho_col + 1) * len(columnas_mostrar) + 1
        print("\n" + "="*ancho_total)
        titulo = f"ALGORITMO: {self.algoritmo}"
        if self.algoritmo == 'RR':
            titulo += f" (Quantum: {self.quantum})"
        print(f"{titulo:^{ancho_total}}")
        print("="*ancho_total)
        def fila_str(nombre):
            s = f"│{nombre:^{ancho_fila}}"
            for j in range(inicio_col, fin_col):
                if j < len(self.datos[nombre]):
                    valor = self.datos[nombre][j]
                    if valor == 'X': valor = 'x'
                    if nombre == 'LISTO' and len(str(valor)) > ancho_col:
                        valor = str(valor)[:ancho_col-2] + ".."
                else:
                    valor = ''
                s += f"│{str(valor):^{ancho_col}}"
            s += "│"
            return s
        print(fila_str('BLOQUEADOS'))
        print("├" + "─"*ancho_fila + "┼" + "┼".join(["─"*ancho_col]*len(columnas_mostrar)) + "┤")
        for p in ['P1','P2','P3','P4']:
            print(fila_str(p))
        print("├" + "─"*ancho_fila + "┼" + "┼".join(["─"*ancho_col]*len(columnas_mostrar)) + "┤")
        print(fila_str('LISTO'))
        print("├" + "─"*ancho_fila + "┼" + "┼".join(["─"*ancho_col]*len(columnas_mostrar)) + "┤")
        print(fila_str('SO'))
        print("├" + "─"*ancho_fila + "┼" + "┼".join(["─"*ancho_col]*len(columnas_mostrar)) + "┤")
        tiempo_str = f"│{'TIEMPO':^{ancho_fila}}"
        for tiempo in columnas_mostrar:
            tiempo_str += f"│{tiempo:^{ancho_col}}"
        tiempo_str += "│"
        print(tiempo_str)
        print("└" + "─"*ancho_fila + "┴" + "┴".join(["─"*ancho_col]*len(columnas_mostrar)) + "┘")
        if inicio_col > 0 or fin_col < len(self.columnas_tiempo):
            print(f"\n Mostrando columnas {inicio_col+1}-{fin_col} de {len(self.columnas_tiempo)}")

    def mostrar_tabla_interactiva(self):
        import os
        try:
            ancho_terminal = os.get_terminal_size().columns
            cols_visibles = max(3, (ancho_terminal - 15) // 12)
        except:
            cols_visibles = 6
        inicio_col = 0
        while True:
            limpiar_pantalla()
            print("╔" + "═"*70 + "╗")
            print("║" + " "*20 + "SIMULACIÓN DE PLANIFICACIÓN DE CPU" + " "*16 + "║")
            print("╚" + "═"*70 + "╝")
            self.mostrar_tabla(inicio_col, cols_visibles)
            if len(self.columnas_tiempo) <= cols_visibles:
                self._mostrar_menu_resultados()
                break
            print(f"\n{'─'*50}")
            print("CONTROLES:")
            print("  (a) ← Anterior | (d) → Siguiente | (c) Completa | (r) Resultados | (q) Salir")
            print("─"*50)
            tecla = input("Opción: ").lower().strip()
            if tecla == 'a' and inicio_col > 0:
                inicio_col = max(0, inicio_col - cols_visibles)
            elif tecla == 'd' and inicio_col + cols_visibles < len(self.columnas_tiempo):
                inicio_col = min(len(self.columnas_tiempo) - cols_visibles, inicio_col + cols_visibles)
            elif tecla == 'c':
                self._mostrar_tabla_completa()
            elif tecla == 'r':
                self._mostrar_menu_resultados()
                break
            elif tecla == 'q':
                break

    def _mostrar_tabla_completa(self):
        limpiar_pantalla()
        print("╔" + "═"*70 + "╗")
        print("║" + " "*25 + "TABLA COMPLETA" + " "*31 + "║")
        print("╚" + "═"*70 + "╝")
        cols_por_segmento = 8
        total_cols = len(self.columnas_tiempo)
        for inicio in range(0, total_cols, cols_por_segmento):
            fin = min(inicio + cols_por_segmento, total_cols)
            print(f"\n SEGMENTO: Columnas {inicio+1} - {fin}")
            self.mostrar_tabla(inicio, cols_por_segmento)
            if fin < total_cols:
                input("\n⏯️  Presiona Enter para ver el siguiente segmento...")
        input("\n Tabla completa mostrada. Presiona Enter para continuar...")

    def _mostrar_menu_resultados(self):
        while True:
            limpiar_pantalla()
            print("╔" + "═"*60 + "╗")
            print("║" + " "*20 + "ANÁLISIS DE RESULTADOS" + " "*17 + "║")
            print("╚" + "═"*60 + "╝")
            print("\n OPCIONES DE ANÁLISIS:")
            print("1.  Estadísticas por proceso")
            print("2.  Eventos importantes")
            print("3.  Línea de tiempo compacta")
            print("4.  Utilización del sistema")
            print("5.  Volver al menú principal")
            opcion = input("\nSelecciona opción (1-5): ").strip()
            if opcion == '1':
                self._mostrar_estadisticas_procesos()
            elif opcion == '2':
                self._mostrar_eventos_importantes()
            elif opcion == '3':
                self._mostrar_linea_tiempo()
            elif opcion == '4':
                self._mostrar_utilizacion_sistema()
            elif opcion == '5':
                break
            else:
                print("ERROR: Opción no válida")
                input("Presiona Enter para continuar...")

    def _mostrar_estadisticas_procesos(self):
        limpiar_pantalla()
        print("ESTADÍSTICAS POR PROCESO")
        print("="*50)
        for proceso in self.procesos:
            print(f"\n🔷 PROCESO {proceso.nombre}:")
            print(f"   • Tiempo de llegada: {proceso.tiempo_llegada}")
            print(f"   • Veces en SO: {proceso.veces_en_so}")
            print(f"   • Estado final: {proceso.estado}")
            print(f"   • Tiempo total CPU: {proceso.calcular_tiempo_total_cpu()}")
            tiempo_es = proceso.calcular_tiempo_total_es()
            if tiempo_es > 0:
                print(f"   • Tiempo total E/S: {tiempo_es}")
            secuencia_str = " → ".join([f"{tipo}({tiempo})" for tipo, tiempo in proceso.secuencia_original])
            print(f"   • Secuencia: {secuencia_str}")
        input("\n Presiona Enter para continuar...")

    def _mostrar_eventos_importantes(self):
        limpiar_pantalla()
        print("EVENTOS IMPORTANTES")
        print("="*50)
        if not self.eventos_log:
            print("ERROR: No hay eventos registrados")
            input("Presiona Enter para continuar...")
            return
        eventos_criticos = [e for e in self.eventos_log if any(x in e for x in ['LLEGA', 'TERMINADO', 'EXPROPIADO'])]
        if eventos_criticos:
            print("🎯 EVENTOS CRÍTICOS:")
            for evento in eventos_criticos[:20]:
                if 'LLEGA' in evento:
                    print(f"    {evento}")
                elif 'TERMINADO' in evento:
                    print(f"    {evento}")
                elif 'EXPROPIADO' in evento:
                    print(f"    {evento}")
        print(f"\n📋 TODOS LOS EVENTOS ({len(self.eventos_log)} total):")
        eventos_por_pagina = 15
        pagina = 0
        total_paginas = (len(self.eventos_log) + eventos_por_pagina - 1) // eventos_por_pagina
        while True:
            inicio = pagina * eventos_por_pagina
            fin = min(inicio + eventos_por_pagina, len(self.eventos_log))
            print(f"\n--- Página {pagina + 1} de {total_paginas} ---")
            for i in range(inicio, fin):
                print(f"   {i + 1:3}. {self.eventos_log[i]}")
            if total_paginas > 1:
                opciones = []
                if pagina > 0:
                    opciones.append("(a) anterior")
                if pagina < total_paginas - 1:
                    opciones.append("(s) siguiente")
                opciones.append("(q) salir")
                accion = input(f"\n{' | '.join(opciones)}: ").lower().strip()
                if accion == 'a' and pagina > 0:
                    pagina -= 1
                elif accion == 's' and pagina < total_paginas - 1:
                    pagina += 1
                elif accion == 'q':
                    break
            else:
                input("\n Presiona Enter para continuar...")
                break

    def _mostrar_linea_tiempo(self):
        limpiar_pantalla()
        print("⏱  LÍNEA DE TIEMPO COMPACTA")
        print("="*50)
        secuencia = []
        proceso_anterior = None
        tiempo_inicio = 0
        for i, tiempo in enumerate(self.columnas_tiempo):
            proceso_actual = "LIBRE"
            for nombre_proceso in ['P1', 'P2', 'P3', 'P4']:
                if (nombre_proceso in self.datos and i < len(self.datos[nombre_proceso]) and self.datos[nombre_proceso][i] == '█'):
                    proceso_actual = nombre_proceso
                    break
            if proceso_actual != proceso_anterior:
                if proceso_anterior is not None:
                    duracion = tiempo - tiempo_inicio
                    if proceso_anterior == "LIBRE":
                        secuencia.append(f"💤 CPU LIBRE: t={tiempo_inicio}-{tiempo} ({duracion})")
                    else:
                        secuencia.append(f"⚡ {proceso_anterior}: t={tiempo_inicio}-{tiempo} ({duracion})")
                tiempo_inicio = tiempo
                proceso_anterior = proceso_actual
        if proceso_anterior is not None:
            tiempo_final = self.columnas_tiempo[-1] if self.columnas_tiempo else 0
            duracion = tiempo_final - tiempo_inicio + 10
            if proceso_anterior == "LIBRE":
                secuencia.append(f"💤 CPU LIBRE: t={tiempo_inicio}-{tiempo_final + 10} ({duracion})")
            else:
                secuencia.append(f"⚡ {proceso_anterior}: t={tiempo_inicio}-{tiempo_final + 10} ({duracion})")
        for seg in secuencia:
            print(f"   {seg}")
        input("\n Presiona Enter para continuar...")

    def _mostrar_utilizacion_sistema(self):
        limpiar_pantalla()
        print("  UTILIZACIÓN DEL SISTEMA")
        print("="*50)
        tiempo_total = len(self.columnas_tiempo) * 10 if self.columnas_tiempo else 0
        tiempo_cpu_ocupado = 0
        for nombre_proceso in ['P1', 'P2', 'P3', 'P4']:
            if nombre_proceso in self.datos:
                tiempo_cpu_ocupado += sum(1 for x in self.datos[nombre_proceso] if x == 'x') * 10
        tiempo_cpu_libre = tiempo_total - tiempo_cpu_ocupado
        utilizacion_cpu = (tiempo_cpu_ocupado / tiempo_total * 100) if tiempo_total > 0 else 0
        print(f" MÉTRICAS GENERALES:")
        print(f"   • Tiempo total de simulación: {tiempo_total}")
        print(f"   • Tiempo CPU ocupado: {tiempo_cpu_ocupado}")
        print(f"   • Tiempo CPU libre: {tiempo_cpu_libre}")
        print(f"   • Utilización de CPU: {utilizacion_cpu:.1f}%")
        print(f"\n CONFIGURACIÓN:")
        print(f"   • Algoritmo: {self.algoritmo}")
        if self.algoritmo == 'RR':
            print(f"   • Quantum: {self.quantum}")
        print(f"   • Total de procesos: {len(self.procesos)}")
        procesos_terminados = sum(1 for p in self.procesos if p.estado == Estado.TERMINADO)
        throughput = (procesos_terminados / (tiempo_total / 10)) if tiempo_total > 0 else 0
        print(f"\n RENDIMIENTO:")
        print(f"   • Procesos terminados: {procesos_terminados}/{len(self.procesos)}")
        print(f"   • Throughput: {throughput:.3f} procesos/unidad de tiempo")
        input("\n Presiona Enter para continuar...")

def limpiar_pantalla():
    import os
    os.system('cls' if os.name == 'nt' else 'clear')

def menu_principal():
    tabla = TablaProcesos()
    while True:
        limpiar_pantalla()
        print("╔" + "═"*60 + "╗")
        print("║" + " "*15 + "SIMULADOR DE PLANIFICACIÓN DE CPU" + " "*12 + "║")
        print("╚" + "═"*60 + "╝")
        if tabla.algoritmo is None:
            print("\n CONFIGURACIÓN INICIAL:")
            print("1. Configurar simulación FIFO")
            print("2. Configurar simulación Round Robin")
            print("3. Usar ejemplo predefinido")
            print("4. Salir")
        elif len(tabla.procesos) == 0:
            print(f"\n Algoritmo configurado: {tabla.algoritmo}")
            if tabla.algoritmo == 'RR':
                print(f"   Quantum: {tabla.quantum}")
            print("\nCONFIGURACIÓN DE PROCESOS:")
            print("1. Agregar procesos manualmente")
            print("2. Cambiar algoritmo")
            print("3. Salir")
        else:
            print(f"\n✅ Configuración completada:")
            print(f"   • Algoritmo: {tabla.algoritmo}")
            if tabla.algoritmo == 'RR':
                print(f"   • Quantum: {tabla.quantum}")
            print(f"   • Procesos: {len(tabla.procesos)}")
            print("\n EJECUCIÓN:")
            print("1. Ejecutar simulación")
            print("2. Ver configuración actual")
            print("3. Reiniciar configuración")
            print("4. Salir")
        print("─"*62)
        try:
            opcion = input("Selecciona una opción: ").strip()
            if tabla.algoritmo is None:
                if opcion == '1':
                    tabla.configurar_simulacion('FIFO')
                    input(" Algoritmo FIFO configurado. Presiona Enter para continuar...")
                elif opcion == '2':
                    try:
                        quantum = int(input("Ingresa el quantum de tiempo (múltiplo de 10): "))
                        tabla.configurar_simulacion('RR', quantum)
                        input(f" Round Robin configurado con quantum {quantum}. Presiona Enter...")
                    except:
                        print("ERROR: Por favor ingresa un número válido para el quantum.")
                        input("Presiona Enter para continuar...")
                elif opcion == '3':
                    usar_ejemplo_predefinido(tabla)
                elif opcion == '4':
                    print("👋 ¡Hasta luego!")
                    break
            elif len(tabla.procesos) == 0:
                if opcion == '1':
                    configurar_procesos_manual(tabla)
                elif opcion == '2':
                    tabla.algoritmo = None
                    tabla.quantum = 0
                elif opcion == '3':
                    print(" ¡Hasta luego!")
                    break
            else:
                if opcion == '1':
                    tabla.ejecutar_simulacion()
                elif opcion == '2':
                    mostrar_configuracion_actual(tabla)
                elif opcion == '3':
                    confirmar = input("¿Estás seguro de reiniciar la configuración? (s/n): ").lower()
                    if confirmar == 's':
                        tabla = TablaProcesos()
                        input("✅ Configuración reiniciada. Presiona Enter...")
                elif opcion == '4':
                    print(" ¡Hasta luego!")
                    break
        except KeyboardInterrupt:
            print("\n\n ¡Adiós!")
            break
        except Exception as e:
            print(f"ERROR: {e}")
            input("Presiona Enter para continuar...")

def usar_ejemplo_predefinido(tabla):
    limpiar_pantalla()
    print("📖 EJEMPLO PREDEFINIDO - FIFO PUNTO 1")
    print("="*50)
    print("🔧 Configuración:")
    print("   • P1: Llegada=0, Secuencia=CPU(10)→E/S(10)→CPU(10)→E/S(30)→CPU(10)")
    print("   • P2: Llegada=0, Secuencia=CPU(10)→E/S(50)→CPU(10)→E/S(20)→CPU(10)")
    print("   • P3: Llegada=110, Secuencia=CPU(10)")
    algoritmo = input("\nSelecciona algoritmo (FIFO/RR): ").upper().strip()
    if algoritmo == 'RR':
        try:
            quantum = int(input("Ingresa quantum (múltiplo de 10): "))
            tabla.configurar_simulacion('RR', quantum)
        except:
            print("ERROR Quantum inválido, usando FIFO")
            tabla.configurar_simulacion('FIFO')
    else:
        tabla.configurar_simulacion('FIFO')
    tabla.agregar_proceso_predefinido('P1', 0, [('CPU', 10), ('ES', 10), ('CPU', 10), ('ES', 30), ('CPU', 10)])
    tabla.agregar_proceso_predefinido('P2', 0, [('CPU', 10), ('ES', 50), ('CPU', 10), ('ES', 20), ('CPU', 10)])
    tabla.agregar_proceso_predefinido('P3', 110, [('CPU', 10)])
    print(f"✅ Ejemplo cargado con algoritmo {tabla.algoritmo}")
    if tabla.algoritmo == 'RR':
        print(f"   Quantum: {tabla.quantum}")
    input("Presiona Enter para continuar...")

def configurar_procesos_manual(tabla):
    limpiar_pantalla()
    print("CONFIGURACIÓN MANUAL DE PROCESOS")
    print("="*50)
    print(f"Algoritmo: {tabla.algoritmo}")
    if tabla.algoritmo == 'RR':
        print(f"Quantum: {tabla.quantum}")
    nombres_disponibles = ['P1', 'P2', 'P3', 'P4']
    try:
        cantidad = int(input("\n¿Cuántos procesos quieres agregar? (1-4): "))
        if cantidad < 1 or cantidad > 4:
            print("ERROR Cantidad debe ser entre 1 y 4")
            input("Presiona Enter para continuar...")
            return
    except:
        print(" Por favor ingresa un número válido")
        input("Presiona Enter para continuar...")
        return
    procesos_agregados = 0
    for nombre in nombres_disponibles:
        if procesos_agregados >= cantidad:
            break
        if tabla.agregar_proceso_manual(nombre):
            procesos_agregados += 1
        else:
            break
    if procesos_agregados > 0:
        print(f"\n{'='*50}")
        print("---RESUMEN DE PROCESOS CONFIGURADOS---")
        print(f"{'='*50}")
        for p in tabla.procesos:
            secuencia_str = " → ".join([f"{tipo}({tiempo})" for tipo, tiempo in p.secuencia_original])
            print(f"  🔷 {p.nombre}: Llegada={p.tiempo_llegada}")
            print(f"      Secuencia: {secuencia_str}")
        print("="*50)
    input("Presiona Enter para continuar...")

def mostrar_configuracion_actual(tabla):
    limpiar_pantalla()
    print(" CONFIGURACIÓN ACTUAL")
    print("="*50)
    print(f"🔧 ALGORITMO: {tabla.algoritmo}")
    if tabla.algoritmo == 'RR':
        print(f"   Quantum: {tabla.quantum} unidades")
    print(f"\n PROCESOS ({len(tabla.procesos)} total):")
    for p in tabla.procesos:
        print(f"\n  🔷 {p.nombre}:")
        print(f"     • Tiempo de llegada: {p.tiempo_llegada}")
        secuencia_str = " → ".join([f"{tipo}({tiempo})" for tipo, tiempo in p.secuencia_original])
        print(f"     • Secuencia: {secuencia_str}")
        tiempo_cpu = p.calcular_tiempo_total_cpu()
        tiempo_es = p.calcular_tiempo_total_es()
        print(f"     • Tiempo CPU total: {tiempo_cpu}")
        if tiempo_es > 0:
            print(f"     • Tiempo E/S total: {tiempo_es}")
    print("="*50)
    input("Presiona Enter para continuar...")

if __name__ == "__main__":
    menu_principal()
