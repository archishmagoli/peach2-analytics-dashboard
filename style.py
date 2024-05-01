# The style arguments for the sidebar. We use position:fixed and a fixed width
SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "22rem",
    "padding": "2rem 1rem",
    "marginRight" : '1em',
    "backgroundColor": "#f8f9fa",
    "overflow": "auto",
    "border": "1px solid black"
}

# The styles for the main content position to the right of the sidebar
CONTENT_STYLE = {
    "position" : "relative",
    "marginLeft": "24rem",
    "width": "calc(100% - 24rem)",
    "textAlign": "center",
    "padding": "2rem 1rem",
    "alignItems": "flex-start",
    "overflow" : "auto"
}