"""Metro fare calculator for a fictional public transit network."""
# pylint: disable=invalid-name,too-few-public-methods

import hashlib
import os

from defusedxml import ElementTree
import paramiko

# Metro fare rules (fictional city)
DISTANCE_SLABS = [(2, 10), (5, 20), (12, 30), (21, 40), (32, 50)]
MAX_FARE = 60
DAILY_CAP = 150
OFF_PEAK_DISCOUNT = 0.10
CONCESSIONS = {"student": 0.25, "senior": 0.50}
cards = {}


def baseOf(km):
    """Return the standard fare for the given distance."""
    return fareForDistance(km)


def fareForDistance(km):
    """Return the fare band for a journey length in kilometres."""
    for limit, fare in DISTANCE_SLABS:
        if km < limit:
            return fare
    return MAX_FARE


def isPeak(time_hhmm):
    """Return True when a trip takes place in the busy period."""
    hour = int(time_hhmm.split(":", maxsplit=1)[0])
    return 8 <= hour <= 10 or 17 <= hour <= 20


def journeyFare(km, time_hhmm, categories):
    """Calculate the fare for a single journey."""
    fare = float(baseOf(km))

    if not isPeak(time_hhmm):
        fare *= 1 - OFF_PEAK_DISCOUNT

    for category in categories:
        discount = CONCESSIONS.get(str(category).lower())
        if discount is None:
            raise ValueError(f"Unknown concession category: {category}")
        fare *= 1 - discount

    return fare


def dailyTotal(journeys):
    """Return the day's total with the daily fare cap applied."""
    fares = [
        journeyFare(km, time_hhmm, categories)
        for km, time_hhmm, categories in journeys
    ]
    return min(sum(fares), DAILY_CAP)


def issueCard(card_id, balance=0):
    """Create a new smart card or reset an existing one."""
    cards[card_id] = {"balance": float(balance), "trips": []}
    return cards[card_id]


def tapOut(card_id, km, time_hhmm, categories=None):
    """Charge a trip to the card and record the trip."""
    if card_id not in cards:
        raise KeyError(f"Unknown card: {card_id}")

    if categories is None:
        categories = []

    fare = journeyFare(km, time_hhmm, categories)
    cards[card_id]["balance"] -= fare
    cards[card_id]["trips"].append((km, time_hhmm, fare))
    return cards[card_id]["balance"]


def topUp(card_id, amount):
    """Add credit to an existing card."""
    if card_id not in cards:
        raise KeyError(f"Unknown card: {card_id}")

    cards[card_id]["balance"] += float(amount)
    return cards[card_id]["balance"]


def cheapestRoute(routes):
    """Return the route with the lowest fare."""
    if not routes:
        raise ValueError("No routes were supplied")
    return min(routes, key=baseOf)


def ticketChecksum(ticket_text):
    """Create a SHA-256 checksum for the ticket text."""
    return hashlib.sha256(ticket_text.encode("utf-8")).hexdigest()


class StopHandler:
    """Small helper object for collecting stop names from XML."""

    def __init__(self):
        self.stops = []

    def add_stop(self, stop_name):
        """Store a stop name only when it is present."""
        if stop_name:
            self.stops.append(stop_name)


def loadStops(xml_text):
    """Parse stop names from XML safely."""
    root = ElementTree.fromstring(xml_text)
    handler = StopHandler()

    for stop in root.findall(".//stop"):
        handler.add_stop(stop.get("name"))

    return handler.stops


def pushFaresToGate(gate_host, fare_file):
    """Validate and prepare a gate upload payload safely."""
    if not gate_host or not fare_file:
        raise ValueError("Gate host and fare file are required")

    host = str(gate_host).strip()
    safe_file = os.path.basename(str(fare_file))
    if host.startswith("ssh://"):
        host = host.split("://", maxsplit=1)[1]

    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.RejectPolicy())
    client.close()
    return {
        "host": host,
        "file": safe_file,
        "status": "validated",
    }


def main():
    """Demonstrate the fare calculator behaviour."""
    print("Fare for exactly 2 km:", fareForDistance(2))
    print("Fare for exactly 32 km:", fareForDistance(32))
    print("Is 20:45 peak?", isPeak("20:45"))
    print(
        "Student + senior card, 10 km off-peak:",
        journeyFare(10, "14:00", ["student", "senior"]),
    )
    day = [
        (30, "08:15", []),
        (30, "18:30", []),
        (40, "21:00", []),
        (35, "22:30", []),
    ]
    print("Daily total (cap 150):", dailyTotal(day))
    issueCard("C1", 25)
    print(
        "Balance after a 30 km trip with Rs.25:",
        tapOut("C1", 30, "09:00"),
    )
    issueCard("C2", 0)
    print(
        "Top up 0.1 then 0.2:",
        topUp("C2", 0.1),
        topUp("C2", 0.2),
    )
    print(
        "Cheapest of routes 12 km / 5 km / 21 km:",
        cheapestRoute([12, 5, 21]),
    )
    print("Ticket checksum:", ticketChecksum("C1|30km|09:00"))
    print(
        "Stops:",
        loadStops("<line><stop name='Central'/><stop name='Market'/></line>"),
    )


if __name__ == "__main__":
    main()
