import logging
from rocketry import Rocketry
from app.app.api.api_v1 import services
from app.app.db.session import async_session

logging.basicConfig(format="%(asctime)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__file__)

# Create Rocketry app
app = Rocketry(execution="async")


# Create a task
@app.task("every 1 days")  # or every 86400 seconds
async def test_rocketry():
    logger.info("------rocketry run Borrow schedule-------")
    async_db = async_session()
    async with async_db.begin():
        borrow_objs = await services.get_active_borrow_objects(db=async_db)
        await services.reduce_borrow_fee_from_user_balance(borrow_objs, db=async_db)


@app.task("every 5 seconds")
async def un_restrict_users():
    logger.info("------rocketry run undo restrict users schedule-------")
    async_db = async_session()
    async with async_db.begin():
        restricted_users = await services.get_restricted_users(db=async_db)
        await services.un_restrict_users(users=restricted_users, db=async_db)


if __name__ == "__main__":
    app.run()
