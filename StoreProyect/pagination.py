from flask_paginate import Pagination

def paginar_resultados(data, page, per_page):
    start = (page -1) * per_page
    end = start + per_page
    data_paginada = data[start:end]

    pagination = Pagination(page=page, per_page=per_page, total=len(data), record_name='elementos')

    return data_paginada, pagination