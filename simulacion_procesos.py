import simpy
import random
import statistics
import matplotlib.pyplot as plt

# Parámetros de la simulación
RANDOM_SEED = 42    # Semilla para los números aleatorios
RAM_CAPACITY = 100  # Capacidad total de RAM
ARRIVAL_INTERVAL = 10  # Intervalo de llegada de los procesos
CPU_INSTRUCTIONS = 3 # Cantidad de instrucciones que el CPU atiende por unidad

tiempos_ejecucion = []

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
            if instruction_left > 0:
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
    
    