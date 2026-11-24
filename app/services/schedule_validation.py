
from fastapi import HTTPException


def validate_stop_schedule(stops):
    ordered_stops = sorted(stops, key=lambda stop: stop.stop_order)

    if not ordered_stops:
        raise HTTPException(400, "Train route has no stops")

    previous_order = None
    previous_departure_abs = None
    day_offset = 0

    for stop in ordered_stops:
        if (
            previous_order is not None
            and stop.stop_order <= previous_order
        ):
            raise HTTPException(
                400,
                "Stop order must be strictly increasing",
            )

        arrival = stop.arrival_time
        departure = stop.departure_time

        if arrival is not None and departure is not None:
            if departure < arrival:
                raise HTTPException(
                    400,
                    f"Departure precedes arrival at stop {stop.stop_order}",
                )

        arrival_abs = None

        if arrival is not None:
            arrival_minutes = arrival.hour * 60 + arrival.minute
            arrival_abs = day_offset + arrival_minutes

            while (
                previous_departure_abs is not None
                and arrival_abs < previous_departure_abs
            ):
                day_offset += 1440
                arrival_abs += 1440

        if departure is not None:
            departure_minutes = (
                departure.hour * 60 + departure.minute
            )
            departure_abs = day_offset + departure_minutes

            while (
                previous_departure_abs is not None
                and departure_abs < previous_departure_abs
            ):
                day_offset += 1440
                departure_abs += 1440

            if arrival_abs is not None and departure_abs < arrival_abs:
                raise HTTPException(
                    400,
                    f"Invalid schedule at stop {stop.stop_order}",
                )

            previous_departure_abs = departure_abs

        previous_order = stop.stop_order
