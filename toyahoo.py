import csv
import json
from dataclasses import asdict, dataclass
from datetime import date


@dataclass
class Lot:
    """Lot data in format roughly matching Yahoo Finance's"""

    symbol: str
    trade_date: date
    purchase_price: float
    quantity: int
    commission: float = 0.0
    comment: str = ""


def field_names_conversion(field: str) -> str:
    """Capitalize the field names"""
    # TODO: make this a mapping so the internal representation can be different
    return field.replace("_", " ").title()


def lot_to_line(lot: Lot) -> dict:
    """Convert a Lot object to a dictionary"""
    entry: dict = {field_names_conversion(k): v for (k, v) in asdict(lot).items()}
    # Yahoo Finance requires the date in the format YYYYMMDD
    entry["Trade Date"] = lot.trade_date.strftime("%Y%m%d")
    # Yahoo Finance stores stock info differently from Bloomberg
    # TODO: do more robust conversion
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


def main():
    """Process the watchlist JSON file"""
    with open("watchlists.json", "r") as watchlist:
        data = json.load(watchlist)

    portfolio = data["port"]
    positions = portfolio["positions"]

    holdings: list[Lot] = []

    # TODO: break out data extraction to a separate function
    for position in positions:
        lots = position["lots"]
        for lot in lots:
            entry = Lot(
                symbol=position["security"]["ticker"],
                trade_date=date.fromtimestamp(lot["shares"]["buydate"] / 1000),
                purchase_price=lot["shares"]["buyprice"],
                quantity=lot["shares"]["number"],
                comment="Import from Bloomberg",
            )
            holdings.append(entry)

    export(holdings, "upload.csv")


if __name__ == "__main__":
    main()
