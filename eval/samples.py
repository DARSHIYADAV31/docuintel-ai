"""Sample documents and their known-correct labels (fictional data)."""

INVOICE_1 = {
    "file": "invoice_001.png", "doc_type": "invoice", "line_item_count": 2,
    "lines": [
        "INVOICE", "Invoice No: INV-2024-001", "Vendor: Acme Supplies Ltd",
        "Invoice Date: 2024-03-05", "Due Date: 2024-04-04", "Currency: USD", "",
        "Description        Qty   Unit Price   Amount",
        "Widget A            2      30.00       60.00",
        "Widget B            1      40.00       40.00", "",
        "Subtotal: 100.00", "Tax: 10.00", "Total: 110.00",
        "Bank Account: DE89370400440532013000",
    ],
    "fields": {
        "invoice_number": "INV-2024-001", "vendor_name": "Acme Supplies Ltd",
        "invoice_date": "2024-03-05", "due_date": "2024-04-04", "currency": "USD",
        "subtotal": "100.00", "tax": "10.00", "total": "110.00",
        "bank_account": "DE89370400440532013000",
    },
}

INVOICE_2 = {
    "file": "invoice_002.png", "doc_type": "invoice", "line_item_count": 3,
    "lines": [
        "INVOICE", "Invoice No: 88213", "Vendor: Northwind Traders",
        "Invoice Date: 2024-05-12", "Due Date: 2024-06-11", "Currency: EUR", "",
        "Description        Qty   Unit Price   Amount",
        "Office chair        4     120.00      480.00",
        "Desk lamp           2      25.50       51.00",
        "Delivery            1      19.00       19.00", "",
        "Subtotal: 550.00", "Tax: 104.50", "Total: 654.50",
    ],
    "fields": {
        "invoice_number": "88213", "vendor_name": "Northwind Traders",
        "invoice_date": "2024-05-12", "due_date": "2024-06-11", "currency": "EUR",
        "subtotal": "550.00", "tax": "104.50", "total": "654.50",
    },
}

PURCHASE_ORDER = {
    "file": "po_001.png", "doc_type": "po", "line_item_count": 2,
    "lines": [
        "PURCHASE ORDER", "PO Number: PO-5521", "Vendor: Globex Industrial",
        "Order Date: 2024-07-01", "Currency: USD", "",
        "Description        Qty   Unit Price   Amount",
        "Steel bolts        500      0.40       200.00",
        "Steel nuts         500      0.30       150.00", "",
        "Subtotal: 350.00", "Tax: 28.00", "Total: 378.00",
    ],
    "fields": {
        "po_number": "PO-5521", "vendor_name": "Globex Industrial",
        "order_date": "2024-07-01", "currency": "USD",
        "subtotal": "350.00", "tax": "28.00", "total": "378.00",
    },
}

CONTRACT = {
    "file": "contract_001.png", "doc_type": "contract", "line_item_count": 0,
    "lines": [
        "SERVICE AGREEMENT", "Between Initech LLC (Party A) and Hooli Corp (Party B)",
        "Effective Date: 2024-01-01", "End Date: 2025-12-31",
        "Contract Value: 250000.00 USD", "Payment Terms: Net 45 days",
        "Governing Law: State of California",
    ],
    "fields": {
        "contract_title": "Service Agreement", "party_a": "Initech LLC",
        "party_b": "Hooli Corp", "effective_date": "2024-01-01",
        "end_date": "2025-12-31", "contract_value": "250000.00",
        "payment_terms": "Net 45 days", "governing_law": "State of California",
    },
}

SAMPLES = [INVOICE_1, INVOICE_2, PURCHASE_ORDER, CONTRACT]
