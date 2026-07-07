import re
from collections import defaultdict
import os


def parse_data(text):
    """解析单个txt文件的内容，提取服务名、CPU和内存数据"""
    data = defaultdict(list)
    # 匹配服务名（去掉末尾的hash和pod id，例如：emss-bcp-envcrossi-gtw-group-1-v9-85cb7484ff-b85ss → emss-bcp-envcrossi-gtw-group-1-v9）
    pattern = re.compile(r'^(.*?)-[a-z0-9]{8,10}-[a-z0-9]{5}$')

    tokens = text.split()
    i = 0
    while i < len(tokens) - 2:
        token = tokens[i]
        match = pattern.match(token)
        # 检查后续两个token是否为CPU（数字+m）和MEMORY（数字+Mi）
        if match and tokens[i + 1].endswith('m') and tokens[i + 2].endswith('Mi'):
            # 去掉服务名中的 "group-*" 部分（例如：emss-bcp-envcrossi-gtw-group-1-v9 → emss-bcp-envcrossi-gtw）
            service_name = match.group(1).split('-group-')[0]
            cpu = int(tokens[i + 1][:-1])
            mem = int(tokens[i + 2][:-2])
            data[service_name].append((cpu, mem))
            i += 3
        else:
            i += 1

    return data


def process_folder(folder_path, output_filename):
    """处理指定文件夹内的所有txt文件，合并数据并输出CSV"""
    all_data = defaultdict(list)

    # 遍历文件夹中的所有txt文件
    for filename in os.listdir(folder_path):
        if filename.endswith('.txt'):
            file_path = os.path.join(folder_path, filename)
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
            # 解析当前文件的数据
            file_data = parse_data(text)
            # 合并到总数据中
            for service, values in file_data.items():
                all_data[service].extend(values)

    # 统计计算（平均CPU、平均内存、最大CPU、最大内存）
    results = []
    for service, values in all_data.items():
        cpus = [v[0] for v in values]
        mems = [v[1] for v in values]
        avg_cpu = sum(cpus) / len(cpus)
        avg_mem = sum(mems) / len(mems)
        max_cpu = max(cpus)
        max_mem = max(mems)
        results.append({
            'service': service,
            'avg_cpu': f"{avg_cpu:.1f}m",
            'avg_mem': f"{avg_mem:.1f}Mi",
            'max_cpu': f"{max_cpu}m",
            'max_mem': f"{max_mem}Mi"
        })

    # 输出CSV文件（可直接粘贴到Excel/文本编辑器）
    with open(output_filename, 'w', encoding='utf-8') as f:
        f.write("服务名,平均CPU,平均内存,最大CPU,最大内存\n")
        for r in sorted(results, key=lambda x: x['service']):
            f.write(f"{r['service']},{r['avg_cpu']},{r['avg_mem']},{r['max_cpu']},{r['max_mem']}\n")

    print(f"✅ 结果已保存到 {output_filename}")


# 主程序
if __name__ == "__main__":
    # 定义文件夹路径（需与脚本在同一目录）
    inner_net_folder = "内网pod"  # 内网pod文件夹
    outer_net_folder = "外网pod"  # 外网pod文件夹

    # 处理内网pod文件夹中的所有txt文件
    process_folder(inner_net_folder, "平均_内.csv")
    # 处理外网pod文件夹中的所有txt文件
    process_folder(outer_net_folder, "平均_外.csv")
