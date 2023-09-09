from datetime import datetime
from typing import List
from ....models.user import Borrow, Buy, Category


def calculate_categories_profit(borrows: List[Borrow], buys: List[Buy], categories: List[Category]):
    category_profits = {}
    for category in categories:
        category_profits[category.name] = 0
    for borrow in borrows:
        if borrow.returned_date:
            days = (borrow.returned_date - borrow.borrowed_date).days
            category_profits[category.name] += days * borrow.book.category.daily_borrow_fee
        else:
            now = datetime.now(borrow.borrowed_date.tzinfo)
            days = (now - borrow.borrowed_date).days
            category_profits[category.name] += days * borrow.book.category.daily_borrow_fee

    for buy in buys:
        category_profits[category.name] += buy.book.price
    return category_profits
