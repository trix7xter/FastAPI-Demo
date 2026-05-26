from datetime import date

from app.bookings.dao import BookingDAO


async def test_add_and_get_booking():
    new_booking = await BookingDAO.add(
        user_id=1,
        room_id=2,
        date_from=date(2030, 3, 10),
        date_to=date(2030, 3, 15),
    )

    assert new_booking is not None
    assert new_booking.user_id == 1
    assert new_booking.room_id == 2

    fetched = await BookingDAO.find_by_id(new_booking.id)
    assert fetched is not None
