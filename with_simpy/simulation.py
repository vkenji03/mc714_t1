import random
import simpy

from load_balancer import LoadBalancer
from server import Server

class TrafficSimulator:
    def __init__(self, env, load_balancer, inter_request_delay=2):
        self.env = env
        self.inter_request_delay = inter_request_delay
        self.load_balancer = load_balancer
        self.request_id = 0

        # Faz com que generate_requests seja incluido no ambiente de simulacao (nao tenho certeza)
        self.action = env.process(self.generate_requests())
    
    def generate_requests(self):
        print("Iniício da simulação...")
        while True:
            request = {
                "id": self.request_id,
                "cpu_time": random.uniform(1.0, 10.0),
                "io_time": random.uniform(1.0, 5.0),
            }
            self.load_balancer.balance_request(request)
            self.request_id += 1
            yield self.env.timeout(self.inter_request_delay)

def main():
    import argparse

    parser = argparse.ArgumentParser(description="Simulação de Balanceador de Carga")
    parser.add_argument('--policy', type=str, choices=['random', 'round_robin', 'shortest_queue'], default='random',
                        help='Política de balanceamento de carga: random, round_robin, shortest_queue')
    parser.add_argument('--time_to_run_simulation', type=int, required=True, help='Por quantos segundos ira rodar a simulacao')
    parser.add_argument('--inter_request_delay', type=float, default=2.0, help='Atraso entre requisicoes (em segundos)')
    
    args = parser.parse_args()

    # Inicializando o ambiente de simulacao
    env = simpy.Environment()
    
    # Inicializando servidores
    servers = [Server(env, i) for i in range(3)]
    
    # Inicializando balanceador com a política especificada
    load_balancer = LoadBalancer(servers, mode=args.policy)
    
    # Iniciando o simulador de tráfego com os parâmetros fornecidos
    traffic_simulator = TrafficSimulator(env, load_balancer, args.inter_request_delay)

    env.run(until=args.time_to_run_simulation)

    print('Simulacao encerrada')

    for server in servers:
        server.print_metrics()

if __name__ == "__main__":
    main()