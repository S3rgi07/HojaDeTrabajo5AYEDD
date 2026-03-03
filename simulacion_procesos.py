import simpy
import random
import statistics
import matplotlib.pyplot as plt

# Parámetros de la simulación
RANDOM_SEED = 42    # Semilla para los números aleatorios
RAM_CAPACITY = 100  # Capacidad total de RAM
ARRIVAL_INTERVAL = 10  # Intervalo de llegada de los procesos
CPU_INSTRUCTIONS = 3 # Cantidad de instrucciones que el CPU atiende por unidad

execution_times = []

def proceso(env, name, ram, cpu, instructions_per_tick):
    #----- Estado: NEW -----
    
    arrival_time = env.now
    # Memoria requerida por el proceso; se genera aleatoriamente
    required_memory = random.randint(1, 10)
    # Contador del proceso con la cantidad de instrucciones totales a realizar
    instructions_left = random.randint(1, 10)
    
    # Solicita RAM para el proceso
    yield ram.get(required_memory)
    
    # ----- Estado: READY -----
    # Si hay memoria disponible, el proceso se mueve a READY
    while instructions_left > 0:
        # Solicita un turno al CPU para ejecutar las instrucciones
        with cpu.request() as turn:
            yield turn
            # ----- Estado: RUNNING -----
            # El CPU atiende al proceso por un tiempo limitado, suficiente para realizar solo n instruccions
            yield env.timeout(1)  # Usa una unidad, o tick, de tiempo
            
            if instructions_left > instructions_per_tick:
                instructions_left -= instructions_per_tick
            else:
                instructions_left = 0 # Libera de manera anticipada si tiene menos de 3
            
            #Si al finalizar la atención del CPU el proceso aún tiene instrucciones por ejecutar, vuelve a READY
            if instructions_left > 0:
                # Al dejar el CPU, se genera un número entero al azar entre 1 y 21
                action = random.randint(1, 21)
                
                if action == 1:
                    # ----- Estado: WAITING -----
                    # Si el resultado es 1, el proceso pasará a la cola de WAITING para hacer operaciones I/O
                    yield env.timeout(5)  # Simula el tiempo de espera por I/O
                
                elif action == 2:
                    # ----- Estado: READY -----
                    # Si el resultado es 2, el proceso se redirige a la cola de READY
                    pass
                else:
                    # Si cae entre 3 a 21, simplemente regresa a READY a esperar su turno de nuevo
                    pass
                
    # ----- Estado: TERMINATED -----
    # Si el proceso ya no tiene instrucciones por ejecutar, este pasa al estado TERMINATED y sale del sistema
    # Al finalizar el proceso, libera la memoria que estaba utilizando
    yield ram.put(required_memory)
    
    output_time = env.now
    total_time = output_time - arrival_time
    execution_times.append(total_time) # Se guarda el dato para hacer los cálculos del final
    
def generate_processes(env, process_amount, interval, ram, cpu, instructions_per_tick):
    # Genera los procesos espaciados en el tiempo según una distribución exponencial
    for i in range(process_amount):
        arrival_time = random.expovariate(1.0 / interval)
        yield env.timeout(arrival_time)
            
        # Le indicamos a Simpy que agregue un nuevo proceso al entorno
        env.process(proceso(env, f'Proceso-{i}', ram, cpu, instructions_per_tick))
            
def run_simulation(process_amount, interval, ram_capacity, instructions_per_tick, num_cpus):
    # Configura el entorno de Simpy y corre una simulación completa
    execution_times.clear()  # Limpiar los tiempos de ejecución antes de cada simulación
        
    # Reseteamos la semilla para asegurar que cada simulación sea reproducible
    random.seed(RANDOM_SEED)
        
    # Creamos el entorno de Simpy
    env = simpy.Environment()
        
    # Creamos los recursos de RAM y CPU
    ram = simpy.Container(env, init=ram_capacity, capacity=ram_capacity)
    cpu = simpy.Resource(env, capacity=num_cpus)  # CPU con capacidad para atender
        
    # Iniciamos el generador de procesos
    env.process(generate_processes(env, process_amount, interval, ram, cpu, instructions_per_tick))
        
    # Ejecuta la simulación
    env.run()
        
    # Calculamos los resultados
    mean = statistics.mean(execution_times)
    deviation = statistics.stdev(execution_times) if len(execution_times) > 1 else 0
        
    return mean, deviation
    
# --- BLOQUE PRINCIPAL (EXPERIMENTOS Y GRÁFICAS) ---
if __name__ == '__main__':
    cantidades_procesos = [25, 50, 100, 150, 200]
    intervalos = [10, 5, 1]
    
    # Definimos todas las estrategias que vamos a probar, reflejando sus respectivos parámetros
    estrategias = {
        "Base (RAM=100, Vel=3, CPU=1)": {"ram": 100, "vel": 3, "cpus": 1},
        "Estrategia A (RAM=200, Vel=3, CPU=1)": {"ram": 200, "vel": 3, "cpus": 1},
        "Estrategia B (RAM=100, Vel=6, CPU=1)": {"ram": 100, "vel": 6, "cpus": 1},
        "Estrategia C (RAM=100, Vel=3, CPU=2)": {"ram": 100, "vel": 3, "cpus": 2}
    }
    
    print("--- INICIANDO SIMULACIONES Y GENERANDO GRÁFICAS ---")
    
    # Creación de gráficas para cada intervalo de llegada
    for intervalo in intervalos:
        plt.figure(figsize=(10, 6))
        plt.title(f"Tiempo Promedio vs Cantidad de Procesos (Intervalo llegadas = {intervalo})")
        plt.xlabel("Cantidad de Procesos")
        plt.ylabel("Tiempo Promedio de Ejecución")
        
        # Iteración sobre cada estrategia para correr las simulaciones y recolectar los datos
        for nombre_estrategia, params in estrategias.items():
            promedios = []
            print(f"\n>> Corriendo: {nombre_estrategia} | Intervalo: {intervalo}")
            
            for cant in cantidades_procesos:
                # Se corre la simulación con los parámetros específicos de esta estrategia y se obtiene el promedio y desviación
                promedio, desv = run_simulation(cant, intervalo, params["ram"], params["vel"], params["cpus"])
                promedios.append(promedio)
                print(f"Procesos: {cant:3} | Promedio: {promedio:6.2f} | Desv: {desv:6.2f}")
                
            # Adición de la linea de esta estrategia a la gráfica
            plt.plot(cantidades_procesos, promedios, marker='o', label=nombre_estrategia)
            
        # Configuración de los detalles visuales de la gráfica
        plt.legend()
        plt.grid(True)
        
        # Guardar la gráfica en un archivo PNG con un nombre que refleje el intervalo de llegada
        nombre_archivo = f"grafica_intervalo_{intervalo}.png"
        plt.savefig(nombre_archivo)
        print(f"\n[!] Gráfica guardada como: {nombre_archivo}")
        
        # Muestra la ventana con la gráfica
        plt.show()