import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
import random
from matplotlib import rcParams

# 设置中文字体
rcParams['font.sans-serif'] = ['SimHei']  # 使用黑体 SimHei
rcParams['axes.unicode_minus'] = False  # 正常显示负号

# 创建复杂网络拓扑
def create_network():
    G = nx.Graph()
    G.add_edges_from([
        (1, 2, {"value": 10, "attack_cost": 3, "defense_cost": 2}),
        (1, 3, {"value": 20, "attack_cost": 6, "defense_cost": 4}),
        (2, 4, {"value": 15, "attack_cost": 5, "defense_cost": 3}),
        (3, 5, {"value": 12, "attack_cost": 4, "defense_cost": 3}),
        (4, 5, {"value": 25, "attack_cost": 8, "defense_cost": 5}),
        (4, 6, {"value": 30, "attack_cost": 10, "defense_cost": 6}),
        (5, 7, {"value": 18, "attack_cost": 7, "defense_cost": 4}),
        (6, 8, {"value": 22, "attack_cost": 9, "defense_cost": 5}),
        (7, 9, {"value": 35, "attack_cost": 12, "defense_cost": 7}),
        (8, 10, {"value": 40, "attack_cost": 15, "defense_cost": 10}),
    ])
    return G

# 展示网络拓扑
def plot_network(G, attack_paths=None, round_num=None):
    pos = nx.spring_layout(G)
    edge_labels = nx.get_edge_attributes(G, 'value')
    nx.draw(G, pos, with_labels=True, node_color='lightblue', node_size=800, font_size=10)
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)
    if attack_paths:
        nx.draw_networkx_edges(
            G, pos,
            edgelist=attack_paths,
            edge_color='red',
            width=2.0,
            label='攻击路径'
        )
    plt.title(f"网络拓扑（第 {round_num} 轮）" if round_num else "网络拓扑")
    plt.legend()
    plt.show()

# 防御者动态分配资源
def dynamic_defense_strategy(G, defense_budget, attack_history):
    edges = sorted(G.edges(data=True), key=lambda x: attack_history.get((x[0], x[1]), 0) * x[2]['value'], reverse=True)
    defense_allocation = {}
    for u, v, data in edges:
        allocation = min(defense_budget, data['defense_cost'])
        defense_allocation[(u, v)] = allocation
        defense_budget -= allocation
        if defense_budget <= 0:
            break
    return defense_allocation

# 攻击者多样化策略
def diverse_attack(G, defense_allocation, num_paths, randomness_factor):
    edges = sorted(G.edges(data=True),
                   key=lambda x: x[2]['value'] - x[2]['attack_cost'] - defense_allocation.get((x[0], x[1]), 0),
                   reverse=True)
    chosen_paths = random.sample(edges[:min(num_paths, len(edges))], k=max(1, int(num_paths * randomness_factor)))
    return [(u, v) for u, v, _ in chosen_paths]

# 模拟多轮动态博弈
def simulate_dynamic_game(G, defense_budget, rounds, num_paths, randomness_factor):
    attack_history = {}
    total_attacker_profit = []
    total_defender_loss = []

    for round_num in range(1, rounds + 1):
        print(f"\n=== 第 {round_num} 轮博弈 ===")

        # 防御者策略
        defense_allocation = dynamic_defense_strategy(G, defense_budget, attack_history)
        print(f"防御资源分配: {defense_allocation}")

        # 攻击者策略
        attack_paths = diverse_attack(G, defense_allocation, num_paths, randomness_factor)
        print(f"攻击者选择路径: {attack_paths}")

        # 更新拓扑图，显示攻击路径
        plot_network(G, attack_paths, round_num)

        # 记录历史攻击路径
        for path in attack_paths:
            if path in attack_history:
                attack_history[path] += 1
            else:
                attack_history[path] = 1

        # 计算收益和损失
        attacker_profit = 0
        defender_loss = 0
        for path in attack_paths:
            if defense_allocation.get(path, 0) < G.edges[path]['defense_cost']:
                profit = G.edges[path]['value'] - G.edges[path]['attack_cost']
                if profit < 0:
                    print(f"路径 {path} 收益为负: {profit}")
                attacker_profit += profit
            defender_loss += defense_allocation.get(path, 0)

        total_attacker_profit.append(attacker_profit)
        total_defender_loss.append(defender_loss)

        print(f"本轮攻击者收益: {attacker_profit}")
        print(f"本轮防御者损失: {defender_loss}")

    return total_attacker_profit, total_defender_loss

# 动态可视化
def plot_dynamic_results(rounds, attacker_profits, defender_losses):
    plt.figure(figsize=(8, 5))
    plt.plot(range(1, rounds + 1), attacker_profits, label="攻击者收益")
    plt.plot(range(1, rounds + 1), defender_losses, label="防御者损失")
    plt.xlabel("轮次")
    plt.ylabel("收益/损失")
    plt.title("多轮动态博弈收益变化")
    plt.legend()
    plt.grid()
    plt.show()

# 主程序
if __name__ == "__main__":
    G = create_network()

    # 多轮动态博弈
    print("\n=== 多轮动态博弈 ===")
    rounds = 5
    defense_budget = 20
    num_paths = 3
    randomness_factor = 0.5  # 攻击策略的随机化因子（0.0 完全固定，1.0 完全随机）

    attacker_profits, defender_losses = simulate_dynamic_game(
        G,
        defense_budget,
        rounds,
        num_paths,
        randomness_factor
    )

    # 动态可视化
    plot_dynamic_results(rounds, attacker_profits, defender_losses)
