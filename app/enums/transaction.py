from enum import Enum 

class TransactionType(str, Enum):
        INCOMING = "incoming"
        OUTGOING = "outgoing"


class TransactionStatus(str, Enum):
        UNREVIEWED = "unreviewed"
        CONFIRMED = "confirmed"
        DUPLICATE = "duplicate"
        REJECTED = "rejected"