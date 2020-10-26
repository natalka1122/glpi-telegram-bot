STATUS = {
    1: 'Новый',
    2: 'В работе'
}

def show_ticket(ticket, max_len=2000):
    result = []
    result.append('ID: {}'.format(ticket['id']))
    result.append('Заголовок: {}'.format(ticket['name']))
    result.append('Дата открытия: {}'.format(ticket['date']))
    if ticket['status'] in STATUS:
        result.append('Статус: {}'.format(STATUS[ticket['status']]))
    else:
        result.append('Статус: {} Мама, это какой-то неизвестный статус!'.format(ticket['status']))
    return (result[i:i+max_len] for i in range(0, len(result), max_len))