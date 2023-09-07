import logging
from rocketry import Rocketry
from app.app.api.api_v1.services.schedule import get_active_borrow_objects, reduce_borrow_fee_from_user_balance

logging.basicConfig(format="%(asctime)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__file__)


# Create Rocketry app
app = Rocketry(execution="async")


# Create a task
@app.task("every 5 seconds")
async def test_rocketry():
    logger.info("------rocketry run Borrow schedule-------")
    borrow_objs = await get_active_borrow_objects()
    await reduce_borrow_fee_from_user_balance(borrow_objs)


if __name__ == "__main__":
    app.run()
