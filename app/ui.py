from typing import Any

from htpy import (
    Element,
    a,
    div,
    h1,
    head,
    html,
    link,
    main,
    meta,
    p,
    script,
    body,
    span,
    title,
)


def root(el: Element):
    return html(lang="en")[
        head[
            meta(charset="UTF-8"),
            meta(name="viewport", content="width=device-width, initial-scale=1.0"),
            script(
                {"type": "module"},
                src="https://cdn.jsdelivr.net/gh/starfederation/datastar@v1.0.0-RC.7/bundles/datastar.js",
            ),
            link(href="/static/output.css", rel="stylesheet"),
            title["Insider Daily"],
            body(class_="text-gray-500")[
                div(
                    class_="mt-8 max-w-6xl mx-auto border border-gray-200 rounded-lg p-4 sm:p-6 min-h-screen"
                )[el]
            ],
        ]
    ]


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


def main_body() -> Element:
    return main(class_="mx-auto w-full max-w-5xl")[
        h1(class_="font-bold text-3xl underline underline-offset-8")["Insider Filings"],
        div({"data-init": "@get('/form4')"}, class_="my-8")[
            div({"data-indicator:fetching": True}, id="form4_feed"),
            div({"data-show": "$fetching"})["Loading..."],
        ],
    ]


def form4_row(item) -> Element:
    """Render a single Form 4 filing as a feed row."""
    ticker = item["ticker"]
    company = item["company_name"]
    insider = item["insider_name"]
    date = item["filing_date"]
    filing_url = item["filing_url"]
    net_shares = item["net_shares"]
    total_value = item["total_value"]

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

    return div(
        class_="grid grid-cols-[1fr_auto_auto_auto_auto] gap-3 items-center border-b border-gray-100 py-3 px-2 hover:bg-blue-50 rounded transition"
    )[
        div(class_="min-w-0")[
            a(
                class_="font-semibold text-gray-900 hover:text-blue-600",
                href=f"/company/{ticker}",
            )[company],
            div(class_="text-xs text-gray-400 truncate")[insider],
        ],
        span(
            class_=f"inline-block {action_color} text-xs font-semibold px-2 py-1 rounded whitespace-nowrap"
        )[action, " ", shares_display],
        span(class_="text-sm text-gray-500 tabular-nums")[value_display],
        span(class_="text-sm text-gray-400")[date],
        a(
            class_="text-xs text-blue-500 hover:text-blue-700 underline whitespace-nowrap",
            target="_blank",
            href=f"{filing_url}",
        )["SEC"],
    ]
