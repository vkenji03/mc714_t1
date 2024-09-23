import random
import simpy
import json
import os

from load_balancer import LoadBalancer
from server import Server

class TrafficSimulator:
    def __init__(self, env, load_balancer):
        self.env = env
        self.load_balancer = load_balancer
        self.request_id = 0

    def generate_requests(self):
        print("Início da simulação...")
        while True:
            request = {
                "id": self.request_id,
                "cpu_time": random.uniform(1.0, 10.0),
                "io_time": random.uniform(1.0, 5.0),
            }
            self.load_balancer.balance_request(request)
            self.request_id += 1
            yield self.env.timeout(1)

    def send_requests_from_json(self, json_filename):
        print(f"Início da simulação do arquivo {json_filename}...")

        with open(json_filename, 'r') as file:
            requests_list = json.load(file)

        sorted_requests = sorted(requests_list, key=lambda r: r['arrival_time'])

        for request in sorted_requests:
            arrival_time = request['arrival_time']
            yield self.env.timeout(arrival_time - self.env.now)

            new_request = {
                "id": request['id'],
                "cpu_time": request['cpu_time'],
                "io_time": request['io_time'],
            }
            self.load_balancer.balance_request(new_request)

def save_metrics(metrics, output_filename):
    with open(output_filename, 'w') as f:
        json.dump(metrics, f, indent=4)
    print(f"Métricas salvas em: {output_filename}")

def main():
    import argparse

    parser = argparse.ArgumentParser(description="Simulação de Balanceador de Carga")
    parser.add_argument('--policy', type=str, choices=['random', 'round_robin', 'shortest_queue'], default='random',
                        help='Política de balanceamento de carga: random, round_robin, shortest_queue')

    args = parser.parse_args()

    # Diretório com os arquivos JSON de requisições
    directory = "simulations"
    if not os.path.exists(directory):
        print(f"Diretório '{directory}' não encontrado.")
        return

    # Processar cada arquivo JSON no diretório
    for json_file in os.listdir(directory):
        if json_file.endswith('.json'):
            json_filepath = os.path.join(directory, json_file)

            env = simpy.Environment()
            servers = [Server(env, i) for i in range(3)]
            load_balancer = LoadBalancer(servers, mode=args.policy)
            traffic_simulator = TrafficSimulator(env, load_balancer)

            # Carregar e simular o tráfego a partir do arquivo JSON
            env.process(traffic_simulator.send_requests_from_json(json_filepath))
            env.run(until=3600)

            all_metrics = {}
            for server in servers:
                all_metrics[f"server_{server.server_id}"] =  server.get_metrics()

            output_dir = f"./simulations/output/{json_file.replace('.json', '')}"
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)

            # Nome do arquivo de saída com a política aplicada e o nome original do arquivo
            output_filename = f"{output_dir}/{args.policy}_metrics.json"
            
            # Salvar as métricas de todos os servidores
            save_metrics(all_metrics, output_filename)

    print("Simulação encerrada")

if __name__ == "__main__":
    main()
