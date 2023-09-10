from .... import crud


async def get_all_buy_objects(db):
    buys = await crud.buy.get_all_joined(db)
    return buys


async def get_buys_group_by_books(db):
    result = await crud.buy.group_by_books(db)
    return result
