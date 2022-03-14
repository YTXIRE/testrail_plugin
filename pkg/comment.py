def create_comment(result, mode):
    comment = [f'**Режим запуска**: {"Локальный" if mode == "local" else "Удаленный"}\n\n', ]
    if result["case_name"] != '':
        comment.append(f'**Название теста**: {result["case_name"]}\n')
    if result["case_description"] != '':
        comment.append(f'**Описание**: {result["case_description"]}\n')
    if result["case_status"] != '':
        comment.append(f'**Статус теста**: {result["case_status"]}\n\n')
    if len(result['params']):
        comment.append(''.join(result['params']))
    if len(result['steps']):
        comment.append(f'**Шаги**:\n\n')
    for key, item in enumerate(result['steps']):
        comment.append(f'{key + 1}.\tНазвание: {item["name"]}\n')
        comment.append(f'\tСтатус: {item["status"]}\n')
        comment.append(f'\tВремя выполнения: {item["time"]}\n\n')
    if result['error']['message'] != '' and result['error']['trace'] != '':
        comment.append('\n\n\n##Ошибка:\n\n')
        comment.append(f'Сообщение: {result["error"]["message"]}\n\n')
        comment.append(f'Расположение: \n`{result["error"]["trace"]}`\n\n')
    # if len(result['attachments']):
    #     comment.append('\nЛоги:\n')
    # for key, item in enumerate(result['attachments']):
    #     comment.append(f'{key + 1}.\t{item["name"]}\n')
    return ''.join(comment)
