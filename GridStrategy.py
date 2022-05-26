import numpy as np
import pandas as pd

StockInfo = pd.read_csv('historic_data.csv', delimiter=',')
grid = {}
stocks = start_stocks = 100  # количество акций
balance = start_balance = 1000  # свободные деньги для покупок
amount = 3  # сколько акций будем покупать/продавать


def GridBuild(start_cost, grid):
    sector_numbers = []
    min = float(input('Введите минимум сетки:'))
    max = float(input('Введите максимум сетки:'))

    while min > max or start_cost < min or start_cost > max:
        if min > max:
            print('min не может быть больше max')
        else:
            print('Сетка не покрывает текущую стоимость')

        min = float(input('Введите минимум сетки:'))
        max = float(input('Введите максимум сетки:'))

    count = int(input('Введите количество делений сетки:'))
    for i in range(count):
        temp = i + 1
        sector_numbers.append(temp)
        if i * (max - min) / (count - 1) + min > start_cost:
            grid[i * (max - min) / (count - 1) + min] = 'sell'
        else:
            grid[i * (max - min) / (count - 1) + min] = 'buy'

    return count, sector_numbers


def FindSector(grid, cost, sector_numbers):
    keys = list(grid.keys())
    left_border = keys[0]
    cur_sector_number = sector_numbers[0]

    if cost > keys[-1]:
        print('Цена больше максимума сетки!')
        return -1, -1
    elif cost < keys[0]:
        print('Цена меньше минимума сетки!')
        return -1, -1

    for key in keys[1:]:
        if key == keys[-1]:
            sector = [keys[-1], keys[-1]]
            cur_sector_number = sector_numbers[-1]
            return sector, cur_sector_number
        else:
            right_border = key
            if left_border <= cost < right_border:
                sector = [left_border, right_border]
                return sector, cur_sector_number
            left_border = key
            cur_sector_number += 1


def ChangeGrid(grid_example, prev_sector, prev_sector_number, sector_number): # поменял метод ChangeSector на ChangeGrid
    keys = list(grid.keys())
    if prev_sector_number < sector_number:
        while True:
            grid_example[prev_sector[0]] = 'buy'
            prev_sector_number += 1
            if prev_sector_number == sector_number:
                return grid
            prev_sector = [keys[prev_sector_number - 1], keys[prev_sector_number]]
    else:
        while True:
            grid_example[prev_sector[0]] = 'sell'
            prev_sector_number -= 1
            if prev_sector_number == sector_number:
                return grid
            prev_sector = [keys[prev_sector_number - 1], keys[prev_sector_number]]


def ChangeGridSell(grid_example, sector):
    grid_example[sector[0]] = 'buy'
    grid_example[sector[1]] = 'current'


def ChangeGridBuy(grid_example, sector):
    grid_example[sector[1]] = 'sell'
    grid_example[sector[0]] = 'current'


def StrategyProcess(costs, grid, stocks, balance, node_count, sector_numbers):
    prev_cost = costs[0]
    prev_sector, prev_sector_number = FindSector(grid, prev_cost, sector_numbers)

    for cost in costs[1:]:  # В идеале должен быть while True, потому что итерирования по списку не будет
        # с этого момента оставляем как есть
        sector, sector_number = FindSector(grid, cost, sector_numbers)

        if prev_sector != sector and sector != -1:
            if prev_cost < cost:
                if grid[sector[0]] != 'current':
                    grid[sector[0]] = 'current'
                    grid = ChangeGrid(grid, prev_sector, prev_sector_number, sector_number)

                    if cost == sector[0]:
                        if stocks >= amount:
                            balance += cost * amount
                            stocks -= amount
                            # функция продажи акций
                        else:
                            print('Акции закончились, закрываем лавочку')
                            return stocks, balance, cost

                prev_sector_number = sector_number
                prev_sector = sector

            elif prev_cost > cost:
                if grid[sector[1]] != 'current':
                    grid = ChangeGrid(grid, prev_sector, prev_sector_number, sector_number)
                    grid[sector[1]] = 'current'

                    if cost == sector[0]:
                        grid[sector[1]] = 'sell'
                        grid[sector[0]] = 'current'
                        if balance >= cost * amount:
                            balance -= cost * amount
                            stocks += amount
                            # функция покупки акций
                        else:
                            print('Нужно золото, милорд')
                            return stocks, balance, cost

                prev_sector_number = sector_number
                prev_sector = sector

        elif sector == -1:
            if cost < min(costs):
                print('Вышли за минимум сетки, соболезную')
            else:
                print('Вышли за максимум сетки. Фиксируем прибыль')

            balance += stocks * cost
            stocks = 0
            # функция продажи всех акций
            return stocks, balance, cost

        prev_cost = cost

    return stocks, balance, costs[-1]


# costs = list(itertools.chain(*zip(StockInfo['open'], StockInfo['close'])))
# print(costs)
# print(min(costs), max(costs))
#
# node_count, sector_numbers = GridBuild(costs[0], grid)
# stocks, balance, last_cost = StrategyProcess(costs, grid, stocks, balance, node_count, sector_numbers)
#
# profit = (balance + stocks * last_cost) - (start_balance + start_stocks * costs[0])
# print(balance, stocks, profit)

