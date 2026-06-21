from typing import Any


def header(body: str) -> str:
    return f"""\
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <script type="module" src="https://cdn.jsdelivr.net/gh/starfederation/datastar@v1.0.0-RC.7/bundles/datastar.js"></script>
  <link rel="stylesheet" href="/static/output.css">

  <title>Insider Daily</title>
</head>
<body class="text-gray-500">
  <div class="mt-8 max-w-6xl mx-auto border border-gray-200 rounded-lg p-4 sm:p-6 min-h-screen">
    {body}
  </div>
</body>
</html>
    """


def main_body():
    """
    The index page of the application, listing latest Form 4.
    """
    return """\
      <h1 class='font-bold text-3xl underline underline-offset-8'> Latest Insider Filings </h1>

      <main class="mx-auto w-full max-w-5xl">
        <div
          class="my-8"
          data-init="@get('/form4')"
        >
          <div id="form4_feed">
            <p class="text-gray-400">Loading...</p>
          </div>
        </div>
      </main>
    """


def form4_row(item: dict[str, Any]) -> str:
    """Render a single Form 4 filing as a feed row."""
    ts = item["transaction_summary"]
    ticker = ts.issuer_ticker or "?"
    company = ts.issuer_name
    insider = ts.insider_name
    date = ts.reporting_date
    filing_url = item["filing_url"]

    # Compute net shares and total value from transactions
    net_shares = 0
    total_value = 0.0
    for t in ts.transactions:
        if t.transaction_type in ("purchase", "award"):
            net_shares += t.shares
        elif t.transaction_type in ("sale",):
            net_shares -= t.shares
        if t.value:
            total_value += t.value

    # Determine action label and color
    if net_shares > 0:
        action = "Bought"
        action_color = "bg-green-100 text-green-700"
    elif net_shares < 0:
        action = "Sold"
        action_color = "bg-red-100 text-red-700"
    else:
        action = "Held"
        action_color = "bg-gray-100 text-gray-600"

    shares_display = f"{abs(net_shares):,}"
    value_display = f"${total_value:,.0f}" if total_value > 0 else "—"

    return f"""\
    <div class="grid grid-cols-[1fr_auto_auto_auto_auto] gap-3 items-center border-b border-gray-100 py-3 px-2 hover:bg-blue-50 rounded transition">
      <div class="min-w-0">
        <a href="/company/{ticker}" class="font-semibold text-gray-900 hover:text-blue-600">{company}</a>
        <div class="text-xs text-gray-400 truncate">{insider}</div>
      </div>
      <span class="inline-block {action_color} text-xs font-semibold px-2 py-1 rounded whitespace-nowrap">{action} {shares_display}</span>
      <span class="text-sm text-gray-500 tabular-nums">{value_display}</span>
      <span class="text-sm text-gray-400">{date}</span>
      <a href="{filing_url}" target="_blank" class="text-xs text-blue-500 hover:text-blue-700 underline whitespace-nowrap">SEC</a>
    </div>
    """


def gen_list_items(id: str, items: list[Any], style: str = ""):
    lis = "".join([f"<li>{item}</li>" for item in items])

    return f"""
    <ul id="{id}" class="{style}">
      {lis}
    </ul>
    """
