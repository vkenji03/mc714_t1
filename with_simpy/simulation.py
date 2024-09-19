import random
import simpy
import json

from load_balancer import LoadBalancer
from server import Server

class TrafficSimulator:
    def __init__(self, env, load_balancer, inter_request_delay=2):
        self.env = env
        self.inter_request_delay = inter_request_delay
        self.load_balancer = load_balancer
        self.request_id = 0

        # Faz com que generate_requests seja incluido no ambiente de simulacao (nao tenho certeza)
        # self.action = env.process(self.generate_requests())
    
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

    def send_requests_from_json(self, json_filename):
        print(f"Início da simulação do arquivo {json_filename}...")

        # Lê a lista de requisições do arquivo JSON
        with open(json_filename, 'r') as file:
            requests_list = json.load(file)

        # Ordena as requisições por tempo de chegada
        sorted_requests = sorted(requests_list, key=lambda r: r['arrival_time'])

        for request in sorted_requests:
            arrival_time = request['arrival_time']
            
            # Aguarda até o tempo de chegada da requisição
            yield self.env.timeout(arrival_time - self.env.now)
            
            # Cria e envia a requisição para o load balancer
            new_request = {
                "id": request['id'],
                "cpu_time": request['cpu_time'],
                "io_time": request['io_time'],
            }
            self.load_balancer.balance_request(new_request)

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
    # env.process(traffic_simulator.generate_requests())
    env.process(traffic_simulator.send_requests_from_json('1_long_999_short.json'))
    env.run(until=args.time_to_run_simulation)

    print('Simulacao encerrada')

    for server in servers:
        server.print_metrics()

if __name__ == "__main__":
    main()