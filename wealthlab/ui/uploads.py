"""Bounded UTF-8 text and explicit source changes for editable financial case forms.

A file can have the same contents as a starter yet still be a new selection.
Keep its upload identity separate from editor text so loading it replaces a
modified draft. Reruns with the same selected file must preserve manual edits.
"""

import streamlit as st

from wealthlab.household.storage import MAX_BYTES


def read(uploaded):
    raw = uploaded.getvalue()
    if len(raw) > MAX_BYTES:
        raise ValueError("Import exceeds the 2 MB limit.")
    try:
        return raw.decode("utf-8-sig")
    except UnicodeDecodeError as error:
        raise ValueError("Use a UTF-8 text file, optionally with a byte-order mark.") from error


def source(uploaded, default, namespace):
    """Prepare a keyed editor; invalid files never reach the editable form."""
    try:
        text = read(uploaded) if uploaded is not None else default
    except ValueError as error:
        invalid(error, namespace)
        return None
    identity = ("default", text)
    if uploaded is not None:
        identity = ("upload", getattr(uploaded, "file_id", id(uploaded)), text)
    select(namespace, identity, text)
    return text


def select(namespace, identity, text):
    key = f"{namespace}_editor"
    if st.session_state.get(f"{namespace}_source") != identity:
        clear(namespace)
        st.session_state[f"{namespace}_source"] = identity
        st.session_state[key] = text
    elif key not in st.session_state:
        # Streamlit removes widget keys when a workbench is not rendered. Restore
        # its last validated input so the returning form matches any shown result.
        st.session_state[key] = st.session_state.get(f"{namespace}_input", text)


def clear(namespace):
    for suffix in ("result", "input"):
        st.session_state.pop(f"{namespace}_{suffix}", None)


def invalid(error, namespace):
    clear(namespace)
    st.error(str(error))
