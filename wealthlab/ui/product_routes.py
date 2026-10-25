"""Choose one editable product workbench while preserving independent result namespaces."""


def show(name):
    if name == "Conditional private fund":
        from wealthlab.ui.private_funds import show as display
    elif name == "Traditional exchange funds":
        from wealthlab.ui.exchange_fund import show as display
    elif name == "Drilling partnerships":
        from wealthlab.ui.drilling import show as display
    else:
        from wealthlab.ui.products import long_short as display
    display()
