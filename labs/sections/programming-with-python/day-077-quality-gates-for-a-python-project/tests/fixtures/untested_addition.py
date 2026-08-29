

def split_evenly(amount: Money, people: int) -> list[Money]:
    """Split an amount between people, giving the remainder cents to the first."""
    if isinstance(people, bool) or not isinstance(people, int):
        raise InvalidMoney(f"people must be a whole number, got {people!r}")
    if people < 1:
        raise InvalidMoney(f"cannot split between {people} people")
    share = amount.cents // people
    remainder = amount.cents - share * people
    shares = [Money(share, amount.currency) for _ in range(people)]
    shares[0] = Money(share + remainder, amount.currency)
    return shares
