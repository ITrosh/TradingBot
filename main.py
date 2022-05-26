from tinkoff.invest import Client, OrderDirection, OrderType, Quotation, \
    RequestError, OrderExecutionReportStatus
from tokens import sandbox_token
import time

# 'BBG0013HRTL0' figi юаней
# 'BBG004731354' figi роснефть
# 'BBG00HTN2CQ3' figi virgin

# GRID STRATEGY BOT
accountId = '62aabcb1-c286-4eea-ad75-3e3867027c8c'
grid = {}
amount = 3  # сколько акций будем покупать/продавать
figi_chy = 'BBG00HTN2CQ3'
figi_rub = 'FG0000000000'  # похоже только для песка
orders_id_base = {}


def GetBalance(token1, id):
    with Client(token1) as client:
        for pos in client.sandbox.get_sandbox_portfolio(account_id=id).positions:
            if pos.figi == 'FG0000000000':
                return ToNormPrice(pos.quantity)


def StopProcess():
    exit(777)


def CheckPrice(token1):
    with Client(token1) as client:
        return ToNormPrice(client.market_data.get_last_prices(figi=[figi_chy]).last_prices[0].price)


def CheckToken(token1):
    try:
        with Client(token1) as client:
            print(client.sandbox.get_sandbox_accounts())
        return True
    except Exception:
        return False


def CheckAccountId(token1, account):
    try:
        with Client(token1) as client:
            print(client.sandbox.get_sandbox_portfolio(account_id=account))
        return True
    except Exception:
        return False


def ReBuildGrid(client):
    for i in orders_id_base:
        time.sleep(2)
        order_state = client.sandbox.get_sandbox_order_state(account_id=accountId, order_id=orders_id_base[i])

        if order_state != OrderExecutionReportStatus.EXECUTION_REPORT_STATUS_NEW:
            current_price = client.market_data.get_last_prices(figi=[figi_chy]).last_prices[0].price
            if i > ToNormPrice(current_price):

                id = client.sandbox.post_sandbox_order(figi=figi_chy, price=ToShitPrice(i), quantity=amount,
                                                       direction=OrderDirection.ORDER_DIRECTION_SELL,
                                                       account_id=accountId, order_type=OrderType.ORDER_TYPE_LIMIT)

                orders_id_base[i] = id

            elif i < ToNormPrice(current_price):
                id = client.sandbox.post_sandbox_order(figi=figi_chy, price=ToShitPrice(i), quantity=amount,
                                                       direction=OrderDirection.ORDER_DIRECTION_BUY,
                                                       account_id=accountId, order_type=OrderType.ORDER_TYPE_LIMIT)

                orders_id_base[i] = id


def GetOrdersState(client):
    # for i in orders_id_base:
    #     order_state = client.sandbox.get_sandbox_order_state(account_id=accountId, order_id=orders_id_base[i])
    #     print(i, order_state.execution_report_status)
    orders = client.sandbox.get_sandbox_orders(account_id=accountId)


def ToNormPrice(Quotation):
    return Quotation.units + Quotation.nano / 1e9


def ToShitPrice(price1):
    price = float("{0:.4f}".format(price1))
    units = int(str(price).split('.')[0])
    nano = int(str(price).split('.')[1])
    return Quotation(units=units, nano=nano)


# Функция проверки наличия денег, акций, и тд.
def IsHaveCash(figi):
    a = client.sandbox.get_sandbox_portfolio(account_id=accountId).positions
    for i in a:
        if figi == i.figi:
            return ToNormPrice(i.quantity)
    return False


def GridBuild(start_cost, grid, client):
    sector_numbers = []
    min = float(input('Введите минимум сетки: '))
    max = float(input('Введите максимум сеточки: '))

    while min > max or start_cost < min or start_cost > max:
        if min > max:
            print('min не может быть больше max')
        else:
            print('Сетка не покрывает текущую стоимость')

        min = float(input('Введите минимум сетки: '))
        max = float(input('Введите максимум сетки: '))

    count = int(input('Введите количество делений сетки: '))
    min_grid_step = max * 0.0008

    while (max - min) / count < min_grid_step:
        print('Комиссия все схавает!')
        count = int(input('Введите количество делений сетки: '))

    for i in range(count):
        temp = i + 1
        sector_numbers.append(temp)
        if i * (max - min) / (count - 1) + min > start_cost:
            grid[i * (max - min) / (count - 1) + min] = 'sell'
            norm_price = ToShitPrice(i * (max - min) / (count - 1) + min)
            print(norm_price)
            # перед каждым ордером делаем проверку на наличие денег и акций, также использовать try
            if IsHaveCash(figi_chy) > amount:
                id = client.sandbox.post_sandbox_order(figi=figi_chy, price=norm_price, quantity=amount,
                                                       direction=OrderDirection.ORDER_DIRECTION_SELL,
                                                       account_id=accountId, order_type=OrderType.ORDER_TYPE_LIMIT,
                                                       order_id=str(i * (max - min) / (count - 1) + min))

                orders_id_base[i * (max - min) / (count - 1) + min] = id.order_id

            else:
                print('GridBuild: Не хватает акций/иностранной валюты для их продажи')
                # a = client.sandbox.get_sandbox_portfolio(account_id=accountId).positions
                exit(-11)

        else:
            grid[i * (max - min) / (count - 1) + min] = 'buy'
            norm_price = ToShitPrice(i * (max - min) / (count - 1) + min)
            print(norm_price)

            if IsHaveCash(figi_rub) > amount * ToNormPrice(
                    client.market_data.get_last_prices(figi=[figi_chy]).last_prices[0].price):
                id = client.sandbox.post_sandbox_order(figi=figi_chy, price=norm_price, quantity=amount,
                                                       direction=OrderDirection.ORDER_DIRECTION_BUY,
                                                       account_id=accountId, order_type=OrderType.ORDER_TYPE_LIMIT,
                                                       order_id=str(i * (max - min) / (count - 1) + min))

                orders_id_base[i * (max - min) / (count - 1) + min] = id.order_id

            else:
                print('GridBuild: Не хватает рублей для покупки акций/иностранной валюты')
                # a = client.sandbox.get_sandbox_portfolio(account_id=accountId).positions
                exit(-11)

    print("GridBuild: Выводим построенную сетку", grid)
    return count, sector_numbers


def FindSector(grid, cost, sector_numbers):
    keys = list(grid.keys())
    left_border = keys[0]
    cur_sector_number = sector_numbers[0]

    if cost > keys[-1]:
        print('FindSector: выход за пределы максимума сетки')
        return -1, -1
    elif cost < keys[0]:
        print('FindSector: выход за пределы минимума сетки')
        return -1, -1

    for key in keys[1:]:

        if key == keys[-1]:
            sector = [keys[-1], keys[-1]]
            cur_sector_number = sector_numbers[-1]
            print('FindSector: Выводим текущий сектор', sector)
            return sector, cur_sector_number
        else:
            right_border = key
            if left_border <= cost < right_border:
                sector = [left_border, right_border]
                print('FindSector: Выводим текущий сектор', sector)
                return sector, cur_sector_number
            left_border = key
            cur_sector_number += 1

    # print('FindSector: выход за пределы минимума сетки')
    # return -1  # возвращает в случае выхода за пределы сетки


def ChangeGrid(grid_example, prev_sector, prev_sector_number, sector_number, current_cost, client):
    keys = list(grid_example.keys())
    if prev_sector_number < sector_number:
        while True:
            grid_example[prev_sector[0]] = 'buy'
            # меняем ордер с проверкой на существование в списке активных заявок на buy
            # if    in client.sandbox.get_sandbox_orders(account_id=accountId).orders проверка в словаре, затем удаление и в словаре и в списке заявок

            # если существует ключ с id prev_sector[0] на значение sell, то снимаем его, и создаем операцию на значение buy и меняем id операции в словаре
            if prev_sector[0] in orders_id_base.keys():

                a = client.sandbox.get_sandbox_orders(account_id=accountId).orders
                for i in a:
                    if i.order_id == orders_id_base[prev_sector[0]]:
                        if i.direction == OrderDirection.ORDER_DIRECTION_SELL:
                            client.sandbox.cancel_sandbox_order(account_id=accountId,
                                                                order_id=orders_id_base[prev_sector[0]])

                            norm_price = ToShitPrice(prev_sector[0])

                            if IsHaveCash(figi_rub) > amount * ToNormPrice(
                                    client.market_data.get_last_prices(figi=[figi_chy]).last_prices[0].price):
                                id = client.sandbox.post_sandbox_order(figi=figi_chy, price=norm_price, quantity=amount,
                                                                       direction=OrderDirection.ORDER_DIRECTION_BUY,
                                                                       account_id=accountId,
                                                                       order_type=OrderType.ORDER_TYPE_LIMIT)

                                orders_id_base[prev_sector[0]] = id.order_id

                            else:
                                print('ChangeGrid: Не хватает рублей для покупки акций/иностранной валюты')
                                a = client.sandbox.get_sandbox_portfolio(account_id=accountId).positions
                                return [i for i in a]




            # если не существует ключ с id prev_sector[0], то создаем операцию на значение buy и добавляем id в словарь
            else:
                norm_price = ToShitPrice(prev_sector[0])

                if IsHaveCash(figi_rub) > amount * ToNormPrice(
                        client.market_data.get_last_prices(figi=[figi_chy]).last_prices[0].price):
                    id = client.sandbox.post_sandbox_order(figi=figi_chy, price=norm_price, quantity=amount,
                                                           direction=OrderDirection.ORDER_DIRECTION_BUY,
                                                           account_id=accountId, order_type=OrderType.ORDER_TYPE_LIMIT)

                    orders_id_base[prev_sector[0]] = id.order_id

                else:
                    print('ChangeGrid: Не хватает рублей для покупки акций/иностранной валюты')
                    a = client.sandbox.get_sandbox_portfolio(account_id=accountId).positions
                    return [i for i in a]

            prev_sector_number += 1
            prev_sector = [keys[prev_sector_number - 1], keys[prev_sector_number]]
            if prev_sector_number == sector_number:
                grid_example[prev_sector[0]] = 'current'
                # prev_sector стал переменной sector использовать везде prev_sector
                # здесь необходимо проверить ордер на существование в списке активных заявок и если он существует, то снять заявку
                # проверка ордера с id prev_sector[0] на значение sell, то удаляем ее и удаляем id из словаря
                if prev_sector[0] in orders_id_base.keys():
                    a = client.sandbox.get_sandbox_orders(account_id=accountId).orders
                    for i in a:
                        if i.order_id == orders_id_base[prev_sector[0]]:
                            if i.direction == OrderDirection.ORDER_DIRECTION_SELL:
                                client.sandbox.cancel_sandbox_order(account_id=accountId,
                                                                    rder_id=orders_id_base[prev_sector[0]])
                                orders_id_base.pop(prev_sector[0], 404)  # 404 - ERROR

                return grid_example
    else:
        while True:
            grid_example[prev_sector[0]] = 'sell'
            # prev_sector[0] - значение цены
            # меняем ордер с проверкой на существование в списке активных заявок
            # если существует ключ с id prev_sector[0] на значение buy, то снимаем его, и создаем операцию на значение sell и меняем id операции в словаре
            if prev_sector[0] in orders_id_base.keys():

                a = client.sandbox.get_sandbox_orders(account_id=accountId).orders
                for i in a:
                    if i.order_id == orders_id_base[prev_sector[0]]:
                        if i.direction == OrderDirection.ORDER_DIRECTION_BUY:
                            client.sandbox.cancel_sandbox_order(account_id=accountId,
                                                                order_id=orders_id_base[prev_sector[0]])

                            norm_price = ToShitPrice(prev_sector[0])

                            if IsHaveCash(figi_chy) > amount:
                                id = client.sandbox.post_sandbox_order(figi=figi_chy, price=norm_price, quantity=amount,
                                                                       direction=OrderDirection.ORDER_DIRECTION_SELL,
                                                                       account_id=accountId,
                                                                       order_type=OrderType.ORDER_TYPE_LIMIT)

                                orders_id_base[prev_sector[0]] = id.order_id

                            else:
                                print('GridBuild: Не хватает акций/иностранной валюты для их продажи')
                                a = client.sandbox.get_sandbox_portfolio(account_id=accountId).positions
                                return [i for i in a]

            # если не существует ключ с id prev_sector[0], то создаем операцию на значение sell и добавляем id в словарь
            else:
                norm_price = ToShitPrice(prev_sector[0])

                if IsHaveCash(figi_chy) > amount:
                    id = client.sandbox.post_sandbox_order(figi=figi_chy, price=norm_price, quantity=amount,
                                                           direction=OrderDirection.ORDER_DIRECTION_SELL,
                                                           account_id=accountId,
                                                           order_type=OrderType.ORDER_TYPE_LIMIT)

                    orders_id_base[prev_sector[0]] = id.order_id

                else:
                    print('GridBuild: Не хватает акций/иностранной валюты для их продажи')
                    a = client.sandbox.get_sandbox_portfolio(account_id=accountId).positions
                    return [i for i in a]

            prev_sector_number -= 1
            prev_sector = [keys[prev_sector_number - 1], keys[prev_sector_number]]
            if prev_sector_number == sector_number:
                if current_cost == prev_sector[0]:
                    grid_example[prev_sector[1]] = 'sell'
                    grid_example[prev_sector[0]] = 'current'
                    # ??????????????????? три условия проверки?

                    # если в словаре существует ключ с prev_sector[1] на значение buy, то снимем его и устанавливаем с этой ценой на sell и меняем id операции в словаре
                    if prev_sector[1] in orders_id_base.keys():

                        a = client.sandbox.get_sandbox_orders(account_id=accountId).orders
                        for i in a:
                            if i.order_id == orders_id_base[prev_sector[1]]:
                                if i.direction == OrderDirection.ORDER_DIRECTION_BUY:
                                    client.sandbox.cancel_sandbox_order(account_id=accountId,
                                                                        order_id=orders_id_base[prev_sector[1]])

                                    norm_price = ToShitPrice(prev_sector[1])

                                    if IsHaveCash(figi_chy) > amount:
                                        id = client.sandbox.post_sandbox_order(figi=figi_chy, price=norm_price,
                                                                               quantity=amount,
                                                                               direction=OrderDirection.ORDER_DIRECTION_SELL,
                                                                               account_id=accountId,
                                                                               order_type=OrderType.ORDER_TYPE_LIMIT)

                                        orders_id_base[prev_sector[1]] = id.order_id

                                    else:
                                        print('GridBuild: Не хватает акций/иностранной валюты для их продажи')
                                        a = client.sandbox.get_sandbox_portfolio(account_id=accountId).positions
                                        return [i for i in a]

                    # если в словаре не существует ключ с prev_sector[1], то создаем операцию на значение sell и записываем id операции в словарь
                    else:
                        norm_price = ToShitPrice(prev_sector[1])

                        if IsHaveCash(figi_chy) > amount:
                            id = client.sandbox.post_sandbox_order(figi=figi_chy, price=norm_price,
                                                                   quantity=amount,
                                                                   direction=OrderDirection.ORDER_DIRECTION_SELL,
                                                                   account_id=accountId,
                                                                   order_type=OrderType.ORDER_TYPE_LIMIT)

                            orders_id_base[prev_sector[1]] = id.order_id

                        else:
                            print('GridBuild: Не хватает акций/иностранной валюты для их продажи')
                            a = client.sandbox.get_sandbox_portfolio(account_id=accountId).positions
                            return [i for i in a]

                    # если ордер с id prev_sector[0] на значение buy существует, то снимаем его и удаляем id операции из словаря
                    if prev_sector[0] in orders_id_base.keys():

                        a = client.sandbox.get_sandbox_orders(account_id=accountId).orders
                        for i in a:
                            if i.order_id == orders_id_base[prev_sector[0]]:
                                if i.direction == OrderDirection.ORDER_DIRECTION_BUY:
                                    client.sandbox.cancel_sandbox_order(account_id=accountId,
                                                                        order_id=orders_id_base[prev_sector[0]])
                                    orders_id_base.pop(prev_sector[0], 404)  # 404 - ERROR

                else:
                    grid_example[prev_sector[1]] = 'current'
                    # проверка ордера с id prev_sector[1] на значение buy, то удаляем ее и удаляем id из словаря
                    if prev_sector[1] in orders_id_base.keys():

                        a = client.sandbox.get_sandbox_orders(account_id=accountId).orders
                        for i in a:
                            if i.order_id == orders_id_base[prev_sector[1]]:
                                if i.direction == OrderDirection.ORDER_DIRECTION_BUY:
                                    client.sandbox.cancel_sandbox_order(account_id=accountId,
                                                                        order_id=orders_id_base[prev_sector[1]])
                                    orders_id_base.pop(prev_sector[1], 404)  # 404 - ERROR
                return grid_example


def StrategyProcess(client, grid, sector_numbers):
    prev_cost = ToNormPrice(client.market_data.get_last_prices(figi=[figi_chy]).last_prices[0].price)  # Получаем последнюю (текущую) цену по бумаге
    print('StrategyProcess: Выводим начальную цену prev_cost', prev_cost)
    prev_sector, prev_sector_number = FindSector(grid, prev_cost, sector_numbers)


    # time.sleep(10) # ждем 10 секунд, для изменения цены

    while True:
        time.sleep(2)  # ждем 10 секунд, для изменения цены
        try:
            norm_price = client.market_data.get_last_prices(figi=[figi_chy]).last_prices[0].price  # Получаем новую цену бумаги
            cost = ToNormPrice(client.market_data.get_last_prices(figi=[figi_chy]).last_prices[0].price)
            #GetOrdersState(client)
            #ReBuildGrid(client)
            print('StrategyProcess: Выводим текущую цену', cost)
        except RequestError as e:
            print(str(e))

        sector, sector_number = FindSector(grid, cost, sector_numbers)

        if prev_sector != sector and sector != -1:
            if prev_cost < cost:
                if grid[sector[0]] != 'current':
                    grid = ChangeGrid(grid, prev_sector, prev_sector_number, sector_number,
                                      current_cost=cost, client=client)

                prev_sector_number = sector_number
                prev_sector = sector

            elif prev_cost > cost:
                if grid[sector[1]] != 'current':
                    grid = ChangeGrid(grid, prev_sector, prev_sector_number, sector_number, current_cost=cost,
                                      client=client)

                prev_sector_number = sector_number
                prev_sector = sector

        elif sector == -1:
            print('Вышли за пределы сетки')
            print('Фиксируем прибыль!')

            # Продаем все бумаги
            client.sandbox.post_sandbox_order(figi=figi_chy, quantity=30,
                                              direction=OrderDirection.ORDER_DIRECTION_SELL,
                                              account_id=accountId, order_type=OrderType.ORDER_TYPE_MARKET)
            print(cost, 'SELL ALL')

            a = client.sandbox.get_sandbox_portfolio(account_id=accountId).positions
            return [i for i in a]

        prev_cost = cost


def testing(client):
    # получение количества инструмента в портфеле в штуках, но лучше получать количество лотов через .quantity_lots
    print(client.users.get_accounts())
    print(client.operations.get_portfolio(account_id='2062199969'))
    a = client.operations.get_portfolio(account_id='2062199969').positions
    for i in a:
        print(ToNormPrice(i.quantity))
        print(i)
    print(type(a))


with Client(sandbox_token) as client:
    # client.sandbox.sandbox_pay_in(account_id=accountId, amount=MoneyValue(currency='rub', units=2000000000, nano=0))
#     print(client.sandbox.get_sandbox_orders(account_id=accountId))
    # client.sandbox.open_sandbox_account()
    # r = client.sandbox.get_sandbox_accounts()
    # print(r)
    # client.sandbox.sandbox_pay_in(account_id=accountId, amount=MoneyValue(currency='usd', units=2000000000, nano=0))
    # print(client.sandbox.post_sandbox_order(figi=figi_chy, quantity=100, direction=OrderDirection.ORDER_DIRECTION_BUY,
    #                                       account_id=accountId, order_type=OrderType.ORDER_TYPE_MARKET))
    # testing(client)
    # print(IsHaveCash(figi=figi_rub))
    # print(client.market_data.get_last_prices(figi=[figi_chy]))
    # print(ToNormPrice(client.market_data.get_last_prices(figi=[figi_chy]).last_prices[0].price))
    # print(client.instruments.share_by(id_type=InstrumentIdType.INSTRUMENT_ID_TYPE_TICKER, class_code='TQBR', id='ROSN'))

    # STAAAART
    print('START')
    for pos in client.sandbox.get_sandbox_portfolio(account_id=accountId).positions:
        print(pos.quantity)
    cost = ToNormPrice(client.market_data.get_last_prices(figi=[figi_chy]).last_prices[0].price)
    node_count, sector_numbers = GridBuild(cost, grid, client)
    endProcess = StrategyProcess(client, grid, sector_numbers)
    print(endProcess)
