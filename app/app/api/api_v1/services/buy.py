from .... import crud


async def get_all_buy_objects(db):
    buys = await crud.buy.get_all_joined(db)
    return buys
