"""Writes upload-ready demo PDFs to sample_docs/ (fictional data).

Run: python eval/make_demo_pdfs.py
"""
from pathlib import Path

from generate_samples import render
from samples import CONTRACT, INVOICE_1, INVOICE_2, PURCHASE_ORDER

OUT = Path(__file__).resolve().parents[1] / "sample_docs"

# Same invoice as INVOICE_1 but the total is wrong, so validation should flag it.
FLAWED_LINES = [line.replace("Total: 110.00", "Total: 150.00") for line in INVOICE_1["lines"]]

DEMOS = {
    "invoice_clean.pdf": INVOICE_1["lines"],
    "invoice_euro.pdf": INVOICE_2["lines"],
    "invoice_wrong_total.pdf": FLAWED_LINES,
    "purchase_order.pdf": PURCHASE_ORDER["lines"],
    "contract_service_agreement.pdf": CONTRACT["lines"],
}


def main() -> None:
    OUT.mkdir(exist_ok=True)
    for name, lines in DEMOS.items():
        png = OUT / (name + ".tmp.png")
        render(lines, png)
        from PIL import Image

        Image.open(png).save(OUT / name, "PDF", resolution=100)
        png.unlink()
    print(f"wrote {len(DEMOS)} PDFs to {OUT}")


if __name__ == "__main__":
    main()
