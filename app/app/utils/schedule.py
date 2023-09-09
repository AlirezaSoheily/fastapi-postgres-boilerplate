import logging
from rocketry import Rocketry
from ..api.api_v1 import services
from datetime import datetime, timedelta

logging.basicConfig(format="%(asctime)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__file__)

# Create Rocketry app
app = Rocketry(execution="async")


# Create a task
@app.task("every 5 seconds")
async def test_rocketry():
    logger.info("------rocketry run Borrow schedule-------")
    borrow_objs = await services.get_active_borrow_objects()
    await services.reduce_borrow_fee_from_user_balance(borrow_objs)


@app.task("every 5 seconds")
async def un_restrict_users():
    logger.info("------rocketry run undo restrict users schedule-------")
    restricted_users = await services.get_restricted_users()
    await services.un_restrict_users(users=restricted_users)


if __name__ == "__main__":
    app.run()
