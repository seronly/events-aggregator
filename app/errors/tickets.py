class SeatNotAvailable(Exception):
    pass


class TicketNotFound(Exception):
    pass


class IdempotencyKeyConflict(Exception):
    pass

class DuplicateIdempotencyKey(Exception):
    pass
