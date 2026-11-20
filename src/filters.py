from dataclasses import dataclass
import pandas as pd
import streamlit as st
from .config import ALL, area, bak

KEYS = ("fokus", "tipe", "bakorwil", "klaster")


def reset():
    for k in KEYS:
        select_filter(k, ALL)


def select_filter(key, value):
    st.session_state["selection_" + key] = value
    st.session_state[key] = value


def remember(key):
    st.session_state["selection_" + key] = st.session_state[key]


@dataclass
class Scope:
    all: pd.DataFrame
    group: pd.DataFrame
    focus: object
    label: str

    def rows(self, df):
        return df[df.ID_Wilayah.isin(self.group.ID_Wilayah)].copy()


def filters(idx):
    for k in KEYS:
        selected = st.session_state.setdefault("selection_" + k, ALL)
        if st.session_state.get(k) != selected:
            st.session_state[k] = selected
    with st.sidebar:
        st.markdown("**Filter wilayah**")
        focus = st.selectbox(
            "Fokus kabupaten/kota",
            [ALL, *sorted(idx.KabKota)],
            key="fokus",
            format_func=area,
            on_change=remember,
            args=("fokus",),
        )
        group = idx
        selected = []
        for key, col, title in [
            ("tipe", "Tipe", "Tipe wilayah"),
            ("bakorwil", "Bakorwil", "Bakorwil"),
            ("klaster", "Klaster", "Klaster"),
        ]:
            val = st.selectbox(
                title,
                [ALL, *sorted(idx[col].unique())],
                key=key,
                format_func=(bak if key == "bakorwil" else str),
                on_change=remember,
                args=(key,),
            )
            if val != ALL:
                group = group[group[col].eq(val)]
                selected.append(bak(val) if key == "bakorwil" else val)
        st.button(
            "Reset Semua",
            on_click=reset,
            width="stretch",
            icon=":material/restart_alt:",
        )
    focus_row = None if focus == ALL else idx[idx.KabKota.eq(focus)].iloc[0]
    return Scope(idx, group, focus_row, " · ".join(selected) or "Seluruh Jawa Timur")
