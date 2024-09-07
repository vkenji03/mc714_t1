import random
import time
import threading

from load_balancer import LoadBalancer
from server import Server

class TrafficSimulator:
    def __init__(self, load_balancer, num_blocks, requests_per_block, inter_block_delay=2):
        self.load_balancer = load_balancer
        self.num_blocks = num_blocks
        self.requests_per_block = requests_per_block
        self.inter_block_delay = inter_block_delay
        self.request_id = 0
    
    def generate_requests(self):
        for block in range(1, self.num_blocks + 1):
            print(f"\n--- Iniciando bloco {block} ---")
            for _ in range(self.requests_per_block):
                request = {
                    "id": self.request_id,
                    "cpu_time": random.uniform(1, 5),
                    "io_time": random.uniform(1, 5),
                }
                self.load_balancer.balance_request(request)
                self.request_id += 1
                # Intervalo entre requisições dentro do bloco
                time.sleep(random.uniform(0.1, 0.5))
            print(f"--- Bloco {block} concluído ---\n")
            # Espera antes de iniciar o próximo bloco
            time.sleep(self.inter_block_delay)
        print("Todas as requisições foram geradas.")

def all_servers_done(servers):
    return all(server.queue.empty() for server in servers)

def main():
    import argparse

    parser = argparse.ArgumentParser(description="Simulação de Balanceador de Carga")
    parser.add_argument('--policy', type=str, choices=['random', 'round_robin', 'shortest_queue'], default='random',
                        help='Política de balanceamento de carga: random, round_robin, shortest_queue')
    parser.add_argument('--num_blocks', type=int, required=True, help='Número de blocos de requisições')
    parser.add_argument('--requests_per_block', type=int, required=True, help='Número de requisições por bloco')
    parser.add_argument('--inter_block_delay', type=float, default=2.0, help='Atraso entre blocos (em segundos)')
    
    args = parser.parse_args()
    
    # Inicializando servidores
    servers = [Server(i) for i in range(3)]
    
    # Inicializando balanceador com a política especificada
    load_balancer = LoadBalancer(servers, mode=args.policy)
    
    # Iniciando processamento dos servidores em threads
    for server in servers:
        threading.Thread(target=server.process_request, daemon=True).start()
    
    # Iniciando o simulador de tráfego com os parâmetros fornecidos
    traffic_simulator = TrafficSimulator(load_balancer, args.num_blocks, args.requests_per_block, args.inter_block_delay)
    traffic_thread = threading.Thread(target=traffic_simulator.generate_requests, daemon=True)
    traffic_thread.start()
    
    # Espera até que todas as requisições sejam geradas e processadas
    try:
        while traffic_thread.is_alive():
            traffic_thread.join(timeout=1)
    except KeyboardInterrupt:
        print("Simulação interrompida pelo usuário.")
    finally:        
        # Aguarda até que todas as filas estejam vazias
        while not all_servers_done(servers):
            time.sleep(1)
        time.sleep(5)

        for server in servers:
            server.stop()
        print("Simulação encerrada.")

if __name__ == "__main__":
    main()