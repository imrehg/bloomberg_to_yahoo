import csv
import json
from dataclasses import asdict, dataclass
from datetime import date


@dataclass
class Lot:
    symbol: str
    trade_date: date
    purchase_price: float
    quantity: int
    commission: float = 0.0
    comment: str = ""


def field_names_capitalize(field: str) -> str:
    """Capitalize the field names"""
    return field.replace("_", " ").title()


def lot_to_line(lot: Lot) -> dict:
    """Convert a Lot object to a dictionary"""
    entry: dict = {field_names_capitalize(k): v for (k, v) in asdict(lot).items()}
    entry["Trade Date"] = lot.trade_date.strftime("%Y%m%d")
    entry["Symbol"] = entry["Symbol"].replace(":", ".").replace("TT", "TW")
    return entry


def export(portfolio, output):
    """Export the portfolio to a JSON file"""
    with open(output, "w", newline="") as out:
        fieldnames = [
            "Symbol",
            "Trade Date",
            "Purchase Price",
            "Quantity",
            "Commission",
            "Comment",
        ]
        stockswriter = csv.DictWriter(
            out,
            fieldnames=fieldnames,
            delimiter=",",
            quotechar='"',
            quoting=csv.QUOTE_MINIMAL,
        )
        stockswriter.writeheader()
        for lot in portfolio:
            stockswriter.writerow(lot_to_line(lot))


def date_conversion(timestamp: int) -> date:
    """Convert the Bloomberg timestamp to an inner date object"""
    return date.fromtimestamp(timestamp / 1000)


def main():
    """Process the watchlist JSON file"""
    with open("watchlists.json", "r") as watchlist:
        data = json.load(watchlist)

    portfolio = data["port"]
    positions = portfolio["positions"]

    holdings: list[Lot] = []

    for position in positions:
        print(position["security"]["ticker"], len(position["lots"]))
        lots = position["lots"]
        for lot in lots:
            entry = Lot(
                symbol=position["security"]["ticker"],
                trade_date=date_conversion(lot["shares"]["buydate"]),
                purchase_price=lot["shares"]["buyprice"],
                quantity=lot["shares"]["number"],
                comment="Import from Bloomberg",
            )
            print(entry)
            holdings.append(entry)

    export(holdings, "upload.csv")


if __name__ == "__main__":
    main()
