import matplotlib.pyplot as plt
import os
import json
from collections import defaultdict
import numpy as np

def get_info_from_json(dir_path):
    metrics = defaultdict(list)
    servers = list()
    policies = list()
    metrics_file_counter = 0
    for metrics_file in os.listdir(dir_path):
        if not metrics_file.endswith('.json'):
            continue
        file_path = f'{dir_path}/{metrics_file}'
        policies.append(metrics_file.rpartition('_')[0])
        with open(file_path, 'r') as f:
            data = json.load(f)
            first = True
            for server in data.keys():
                if server not in servers:
                    servers.append(server)
                server_metrics = data[server]
                for metric in server_metrics.keys():
                    if first:
                        metrics[metric].append(list())
                    metrics[metric][metrics_file_counter].append(server_metrics[metric])
                first = False
        metrics_file_counter += 1

    return [metrics, servers, policies]

def create_plot(x_labels, y_values, legends, dir_name, file_name):
    print(f'Plotando metricas do diretorio {dir_name}')
    metrics = y_values.keys()
    num_metrics = len(metrics)

    fig, ax = plt.subplots(num_metrics, 1, layout='constrained', figsize=(num_metrics * 3, num_metrics * 3))

    for i, metric in enumerate(metrics):
        x = np.arange(len(x_labels))
        multiplier = 0
        width = 0.25
        max_y = 0
        for j, policy in enumerate(legends):
            values = y_values[metric][j]
            max_value = max(values)
            if max_value > max_y: max_y = max_value
            offset = width * multiplier
            rects = ax[i].bar(x + offset, values, width, label=policy)
            ax[i].bar_label(rects, padding=3)
            multiplier += 1

        ax[i].set_title(metric)
        ax[i].set_ylabel('Time (seconds)')
        ax[i].set_ylim(0, 1.7 * max_y)
        ax[i].set_xticks(x + width, x_labels)
        ax[i].legend()

    fig.suptitle(f"{dir_name.split('/')[-1]} metrics:")
    plt.savefig(f'{dir_name}/{file_name}')

def main():
    output_dir_path = './simulations/output'
    if not os.path.exists(output_dir_path):
        print(f"Diretório {output_dir_path} não encontrado")
    
    for request_type in os.listdir(output_dir_path):
        dir_path = f'{output_dir_path}/{request_type}'
        metrics, servers, policies = get_info_from_json(dir_path)
        create_plot(servers, metrics, policies, dir_path, 'metrics.png')

if __name__ == '__main__':
    main()