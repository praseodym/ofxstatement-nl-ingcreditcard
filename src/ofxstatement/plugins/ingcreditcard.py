import json
from datetime import datetime
from typing import Iterable

from ofxstatement.parser import StatementParser
from ofxstatement.plugin import Plugin
from ofxstatement.statement import Statement, StatementLine, Currency


class INGCreditCardPlugin(Plugin):
    """ofxstatement plugin for Dutch ING Creditcard"""

    def get_parser(self, filename: str) -> "INGCreditCard":
        return INGCreditCard(filename)


class INGCreditCard(StatementParser[str]):
    def __init__(self, filename: str) -> None:
        super().__init__()
        self.filename = filename

    def parse(self) -> Statement:
        with open(self.filename, 'r') as f:
            self.statement.bank_id = "INGBNL2A"
            self.statement.account_type = "CREDITLINE"
            data = json.load(f)
            for entry in data['log']['entries']:
                url = entry['request']['url']
                if url.startswith('https://api.mijn.ing.nl/nl/agreements/') \
                        and '/transactions?agreementType=CARD' in url:
                    # skip non-json responses (e.g. empty ones)
                    if entry['response']['content']['mimeType'] == 'application/json':
                        t = json.loads(entry['response']['content']['text'])
                        for t in t['transactions']:
                            if not self.statement.account_id and 'cardNumber' in t:
                                self.statement.account_id = t['cardNumber']
                            stmt_line = self.parse_record(t)
                            if stmt_line:
                                stmt_line.assert_valid()
                                self.statement.lines.append(stmt_line)
            return self.statement

    def split_records(self) -> Iterable[str]:
        pass

    def parse_record(self, t) -> StatementLine:
        """Parse given transaction line and return StatementLine object"""
        if t['reservation']:
            return None

        tid = t['id'] if 'id' in t else t['subject'] + '_' + t['executionDate']
        date = datetime.strptime(t['executionDate'], '%Y-%m-%d')
        memo = t['type']['description']
        amount = self.parse_decimal(t['amount']['value'])
        stmt_line = StatementLine(id=tid, date=date, memo=memo, amount=amount)
        stmt_line.currency = Currency(t['amount']['currency'])
        stmt_line.payee = t['subject']

        if 'sourceAmount' in t:
            sa = t['sourceAmount']
            currency = sa['currency']
            er = t['exchangeRate']
            rate = self.parse_decimal(er)
            stmt_line.currency = Currency(currency, rate)
            stmt_line.memo += f" {sa['value']} {sa['currency']}, exchange rate {er}," \
                              f" fee {t['fee']['value']} {t['fee']['currency']}"

        typeid = t['type']['id']
        if typeid == "AFSCHRIJVING":
            stmt_line.trntype = "DEBIT"
        elif typeid == "MAANDELIJKSE AFLOSSING" or typeid == "DIVERSEN":
            stmt_line.trntype = "CREDIT"
        elif typeid == "KOSTEN":
            stmt_line.trntype = "SRVCHG"
        else:
            print(f"unknown transaction type {typeid}")
            stmt_line.trntype = "OTHER"

        return stmt_line
