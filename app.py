import html
import os
import re
import sqlite3
import unicodedata
from pathlib import Path
from typing import Optional

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

LOGO_URL = "https://raw.githubusercontent.com/tipografitoplulugu/tipografi-bulteni-arsivi/main/logo.png"

st.set_page_config(
    page_title="Tipografi Bülteni Arşivi",
    page_icon="T",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
    <style>
    :root {
        color-scheme: light;
        --paper: #f7f6f3;
        --surface: #fff;
        --ink: #1d1c1a;
        --muted: #716e68;
        --line: #e6e3dd;
        --accent: #81513e;
        --focus: #9b5e43;
    }
    html, body, [data-testid="stAppViewContainer"], [data-testid="stMain"] {
        background: var(--paper);
        color: var(--ink);
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }
    /* Hide Streamlit's in-app toolbar actions (Share, menu, and adjacent
       controls). The content links below are also left-aligned so they stay
       clear if the host renders its own toolbar outside the app. */
    [data-testid="stHeader"],
    [data-testid="stToolbar"],
    [data-testid="stAppToolbar"] { display: none !important; }
    [data-testid="stMain"] .block-container { max-width: 1120px; padding: 2rem 2.25rem 5rem; }
    h1, h2, h3, h4 {
        color: var(--ink) !important;
        font-family: "Iowan Old Style", "Palatino Linotype", Palatino, Georgia, serif !important;
        letter-spacing: -0.035em !important;
    }
    [data-testid="stHeadingWithActionElements"] h1 {
        font-size: clamp(2.8rem, 6vw, 5.25rem) !important;
        line-height: 1.02 !important;
        font-weight: 600 !important;
        margin: .4rem 0 .8rem !important;
    }
    [data-testid="stHeadingWithActionElements"] h2 { font-size: clamp(1.6rem, 3vw, 2.2rem) !important; }
    p, li, label, [data-testid="stMarkdownContainer"] { color: var(--ink); }
    p { line-height: 1.7; }
    a, [data-testid="stMarkdownContainer"] a { color: var(--accent) !important; text-underline-offset: 3px; }
    a:hover { color: #543426 !important; }
    .brand-logo {
        display: block; flex: 0 0 48px; width: 48px; height: 48px;
        border-radius: 11px; background: var(--ink); object-fit: cover;
    }
    .brand-header {
        display: flex;
        align-items: center;
        justify-content: flex-start;
        gap: 1rem;
        padding-bottom: .6rem;
    }
    .brand-identity { display: flex; align-items: center; gap: .8rem; }
    .brand-links {
        margin-left: 1rem;
        color: var(--muted);
        font-size: .88rem;
        white-space: nowrap;
    }
    .brand-name { font-size: 1.08rem; font-weight: 650; letter-spacing: .01em; }
    .hero-eyebrow, .section-eyebrow {
        color: var(--accent); font-size: .72rem; font-weight: 700;
        letter-spacing: .13em; text-transform: uppercase;
    }
    .hero-copy {
        max-width: 690px;
        padding-bottom: 2.6rem;
        color: #5f5c56;
        font-size: 1.08rem;
        line-height: 1.72;
    }
    .hero-rule { border: 0; border-top: 1px solid var(--line); margin: 1.8rem 0 1.5rem; }
    .stat-grid {
        display: grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        column-gap: 1.5rem;
        row-gap: 1.1rem;
    }
    .stat-item { min-width: 0; }
    .stat-label {
        margin-bottom: .2rem;
        color: var(--muted);
        font-size: .75rem;
        line-height: 1.4;
        letter-spacing: .04em;
        text-transform: uppercase;
    }
    .stat-value {
        color: var(--ink);
        font: 1.45rem/1.2 Georgia, serif;
        letter-spacing: -.03em;
        overflow-wrap: anywhere;
    }
    .archive-footer {
        margin-top: 1.6rem;
        border-top: 1px solid var(--line);
        padding: 1.05rem 0 .2rem;
        color: var(--muted);
        font-size: .88rem;
        line-height: 1.45;
    }
    .footer-content {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: .75rem 1.5rem;
    }
    .footer-name { color: var(--muted); font-size: inherit; font-weight: 500; }
    .footer-actions {
        display: flex;
        align-items: center;
        justify-content: flex-end;
        flex-wrap: wrap;
        gap: .75rem 1.1rem;
    }
    .footer-subscribe { color: var(--muted); font-size: inherit; }
    .footer-subscribe a { color: var(--accent) !important; font-weight: 550; }
    .footer-social {
        display: flex;
        align-items: center;
        justify-content: flex-end;
        flex-wrap: wrap;
        gap: .85rem;
    }
    .footer-social a {
        display: inline-flex;
        width: 1.2rem;
        height: 1.2rem;
        align-items: center;
        justify-content: center;
        color: var(--muted) !important;
        border-radius: 4px;
        text-decoration: none !important;
        transition: color 120ms ease;
    }
    .footer-social a:hover { color: var(--accent) !important; }
    .footer-social svg { display: block; width: 100%; height: 100%; }
    .footer-social .icon-fill { fill: currentColor; }
    .footer-social .icon-stroke {
        fill: none;
        stroke: currentColor;
        stroke-linecap: round;
        stroke-linejoin: round;
        stroke-width: 2;
    }
    [data-testid="stTextInput"] input,
    [data-testid="stSelectbox"] [role="combobox"],
    [data-testid="stFormSubmitButton"] button {
        box-sizing: border-box !important;
        height: 48px !important;
        min-height: 48px !important;
        max-height: 48px !important;
        border-radius: 12px !important;
        font-size: .98rem;
        line-height: 1.2;
    }
    [data-testid="stTextInput"] input,
    [data-testid="stSelectbox"] [role="combobox"] {
        border: 1px solid #d8d5ce !important;
        background: var(--surface) !important;
        color: var(--ink) !important;
    }
    /* Streamlit wraps text inputs in a theme-colored root that is separate
       from the input itself. Keep that wrapper the same size and surface. */
    [data-testid="stTextInputRootElement"] {
        box-sizing: border-box !important;
        height: 48px !important;
        min-height: 48px !important;
        max-height: 48px !important;
        border: 1px solid #d8d5ce !important;
        border-radius: 12px !important;
        background: var(--surface) !important;
        overflow: hidden;
    }
    [data-testid="stTextInputRootElement"] [data-testid="stTextInputField"] {
        box-sizing: border-box !important;
        height: 46px !important;
        min-height: 46px !important;
        max-height: 46px !important;
        border: 0 !important;
        border-radius: 0 !important;
        background: transparent !important;
        box-shadow: none !important;
    }
    [data-testid="stTextInputRootElement"]:focus-within,
    [data-testid="stSelectbox"] [role="group"]:focus-within {
        border-color: var(--focus) !important;
        box-shadow: 0 0 0 3px rgba(129, 81, 62, .15) !important;
    }
    [data-testid="stSelectbox"] [data-baseweb="select"] > div,
    [data-testid="stSelectbox"] [data-baseweb="select"] > div > div,
    [data-testid="stSelectbox"] [data-baseweb="select"] > div > div > div {
        background-color: var(--surface) !important;
        background-image: none !important;
    }
    [data-testid="stSelectbox"] [data-baseweb="select"] svg {
        color: var(--muted) !important;
        fill: var(--muted) !important;
    }
    /* Streamlit's current selectbox uses a React Aria group around its input
       and chevron button. Style that group directly; the input alone does
       not control the dark trailing segment. */
    [data-testid="stSelectbox"] [role="group"] {
        box-sizing: border-box !important;
        height: 48px !important;
        min-height: 48px !important;
        max-height: 48px !important;
        border: 1px solid #d8d5ce !important;
        border-radius: 12px !important;
        background: var(--surface) !important;
        overflow: hidden;
    }
    [data-testid="stSelectbox"] [role="group"] [role="combobox"] {
        box-sizing: border-box !important;
        height: 46px !important;
        min-height: 46px !important;
        max-height: 46px !important;
        border: 0 !important;
        border-radius: 0 !important;
        background: transparent !important;
        box-shadow: none !important;
    }
    [data-testid="stSelectbox"] [role="group"] button {
        box-sizing: border-box !important;
        width: 42px !important;
        height: 46px !important;
        min-height: 46px !important;
        border: 0 !important;
        border-radius: 0 !important;
        background: var(--surface) !important;
        color: var(--muted) !important;
        padding: 0 !important;
        box-shadow: none !important;
    }
    [data-testid="stSelectbox"] [role="group"] button:hover,
    [data-testid="stSelectbox"] [role="group"] button:focus {
        background: var(--surface) !important;
        color: var(--ink) !important;
    }
    [data-testid="stSelectbox"] [role="group"] svg {
        color: var(--muted) !important;
        fill: currentColor !important;
    }
    [data-testid="stTextInput"] input:focus,
    [data-testid="stSelectbox"] [role="combobox"]:focus {
        border-color: var(--focus); box-shadow: 0 0 0 3px rgba(129, 81, 62, .15);
    }
    [data-testid="stForm"] { border: 0; padding: 0; }
    [data-testid="stButton"] button {
        min-height: 40px; border: 1px solid #dedbd5; border-radius: 999px;
        background: #fff; color: #393733; font-size: .83rem; transition: border-color 120ms ease, background 120ms ease;
    }
    [data-testid="stButton"] button:hover { border-color: #b8a99e; background: #f2efeb; color: var(--ink); }
    [data-testid="stElementContainer"][class*="st-key-topic_"] [data-testid="stButton"] button {
        opacity: .56;
        transition: opacity 140ms ease, border-color 140ms ease, background 140ms ease;
    }
    [data-testid="stElementContainer"][class*="st-key-topic_"] [data-testid="stButton"] button:hover,
    [data-testid="stElementContainer"][class*="st-key-topic_"] [data-testid="stButton"] button:focus,
    [data-testid="stElementContainer"][class*="st-key-topic_"] [data-testid="stButton"] button:focus-visible,
    [data-testid="stElementContainer"][class*="st-key-topic_"] [data-testid="stButton"] button:active {
        opacity: 1;
    }
    [data-testid="stFormSubmitButton"] button {
        border: 1px solid var(--ink) !important;
        background: var(--ink) !important;
        color: white !important;
        font-weight: 600;
        padding: 0 1rem !important;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    [data-testid="stFormSubmitButton"] button p,
    [data-testid="stFormSubmitButton"] button span {
        color: #fff !important;
        margin: 0;
        line-height: 1.2;
    }
    [data-testid="stFormSubmitButton"] button:hover { border-color: #393733; background: #393733; color: white; }
    button:focus-visible, a:focus-visible, input:focus-visible, [role="combobox"]:focus-visible, summary:focus-visible {
        outline: 3px solid rgba(129, 81, 62, .55) !important; outline-offset: 2px !important;
    }
    [data-testid="stVerticalBlockBorderWrapper"] {
        border: 1px solid var(--line) !important; border-radius: 16px !important; background: var(--surface) !important;
    }
    .result-meta {
        display: flex; flex-wrap: wrap; justify-content: space-between; gap: .35rem 1rem;
        margin-bottom: .6rem; color: var(--muted); font-size: .78rem; letter-spacing: .015em;
    }
    .result-meta strong { color: var(--accent); font-weight: 650; }
    .result-excerpt { margin: .2rem 0 .8rem; color: #4f4d48; font-size: .96rem; line-height: 1.72; }
    mark.search-hit { border-radius: 3px; background: #f4e6d9; color: #442b20; padding: 0 .12em; }
    [data-testid="stExpander"] {
        border: 1px solid var(--line) !important;
        border-radius: 12px !important;
        background: var(--paper) !important;
        overflow: hidden;
    }
    [data-testid="stExpander"] details,
    [data-testid="stExpander"] summary,
    [data-testid="stExpander"] details > summary {
        background: #f7f6f3 !important;
        background-image: none !important;
    }
    [data-testid="stExpander"] summary,
    [data-testid="stExpander"] summary p {
        color: #1d1c1a !important;
        font-size: .9rem;
        font-weight: 560;
        padding: .45rem .75rem;
    }
    [data-testid="stExpander"] summary * { color: #1d1c1a !important; }
    [data-testid="stExpander"] summary:hover,
    [data-testid="stExpander"] summary:hover * {
        background: #f7f6f3 !important;
        background-image: none !important;
        color: #1d1c1a !important;
    }
    [data-testid="stExpander"] [data-testid="stExpanderDetails"] {
        border-top: 1px solid var(--line);
        padding: .8rem 1rem .9rem;
        background: var(--paper) !important;
    }
    .citation-box {
        border: 1px solid var(--line) !important;
        border-radius: 10px !important;
        background: #f7f6f3 !important;
        color: #1d1c1a !important;
        padding: .85rem 1rem;
        font-size: .94rem;
        line-height: 1.65;
        overflow-wrap: anywhere;
        word-break: normal;
    }
    [data-testid="stCaptionContainer"] { color: var(--muted); }
    hr { border-color: var(--line) !important; }
    @media (max-width: 760px) {
        [data-testid="stMain"] .block-container { padding: 1.15rem 1rem 3rem; }
        [data-testid="stHeadingWithActionElements"] h1 { font-size: clamp(2.45rem, 11vw, 3.6rem) !important; }
        .hero-copy { font-size: 1rem; }
        .brand-header { align-items: flex-start; flex-direction: column; }
        .brand-links { margin-left: 0; white-space: normal; }
        .footer-content { align-items: flex-start; flex-direction: column; }
        .footer-actions { justify-content: flex-start; }
        .footer-social { justify-content: flex-start; gap: .8rem; }
        .stat-grid { grid-template-columns: minmax(0, 1fr); row-gap: 1.05rem; }
        .result-meta { flex-direction: column; gap: .2rem; }
        [data-testid="stHorizontalBlock"] { flex-wrap: wrap; gap: .55rem; }
        [data-testid="stHorizontalBlock"] > [data-testid="column"] { min-width: min(100%, 180px); flex: 1 1 180px; }
    }
    @media (prefers-reduced-motion: reduce) {
        *, *::before, *::after { scroll-behavior: auto !important; transition: none !important; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# Original Medium and Substack links for the archive's 93 issues.
BULTEN_URLS = {
    "Ocak 2019": "https://medium.com/tipografi/tipografi-haberleri-ocak-2019-604f7ccb2b07",
    "Şubat 2019": "https://medium.com/tipografi/tipografi-haberleri-şubat-2019-20a4558cf898",
    "Mart 2019": "https://medium.com/tipografi/tipografi-haberleri-mart-2019-27f1060df7bc",
    "Nisan 2019": "https://medium.com/tipografi/tipografi-haberleri-nisan-2019-ad2ff81a02a7",
    "Mayıs 2019": "https://medium.com/tipografi/tipografi-haberleri-mayıs-2019-b0fe22fb7228",
    "Haziran 2019": "https://medium.com/tipografi/tipografi-haberleri-haziran-2019-cdcb17025b40",
    "Temmuz 2019": "https://medium.com/tipografi/tipografi-haberleri-temmuz-2019-153421028174",
    "Ağustos 2019": "https://medium.com/tipografi/tipografi-haberleri-ağustos-2019-f19b996e323f",
    "Eylül 2019": "https://medium.com/tipografi/tipografi-haberleri-eylül-2019-6c85e8d07d41",
    "Ekim 2019": "https://medium.com/tipografi/tipografi-haberleri-ekim-2019-9d95ca9dc851",
    "Kasım 2019": "https://medium.com/tipografi/tipografi-haberleri-kasım-2019-1068f7aba186",
    "Aralık 2019": "https://medium.com/tipografi/tipografi-haberleri-aralık-2019-b655b51e2939",
    "Ocak 2020": "https://medium.com/tipografi/tipografi-haberleri-ocak-2020-5cd73e88420c",
    "Şubat 2020": "https://medium.com/tipografi/tipografi-haberleri-şubat-2020-4942a3299f3e",
    "Mart 2020": "https://medium.com/tipografi/tipografi-haberleri-mart-2020-d4b96a791d32",
    "Nisan 2020": "https://medium.com/tipografi/tipografi-haberleri-nisan-2020-c3da4f9a1e28",
    "Mayıs 2020": "https://medium.com/tipografi/tipografi-haberleri-mayıs-2020-15f2875c5a19",
    "Haziran 2020": "https://medium.com/tipografi/tipografi-haberleri-haziran-2020-ba2a3e54fb51",
    "Temmuz 2020": "https://medium.com/tipografi/tipografi-haberleri-temmuz-2020-f398d60949d7",
    "Ağustos 2020": "https://medium.com/tipografi/tipografi-haberleri-ağustos-2020-6cd4fcbd9a3b",
    "Eylül 2020": "https://medium.com/tipografi/tipografi-haberleri-eylül-2020-7cb342277bd3",
    "Ekim 2020": "https://medium.com/tipografi/tipografi-haberleri-ekim-2020-a04d29bed91b",
    "Kasım 2020": "https://medium.com/tipografi/tipografi-haberleri-kasım-2020-e0d7c2fc6b9f",
    "Aralık 2020": "https://medium.com/tipografi/tipografi-haberleri-aralık-2020-d881afb1a230",
    "Ocak 2021": "https://medium.com/tipografi/tipografi-haberleri-ocak-2021-3429aabca4ed",
    "Şubat 2021": "https://medium.com/tipografi/tipografi-haberleri-şubat-2021-6b4d000da517",
    "Mart 2021": "https://medium.com/tipografi/tipografi-haberleri-mart-2021-2b733a4da85d",
    "Nisan 2021": "https://medium.com/tipografi/tipografi-haberleri-nisan-2021-fd6cdff4e9c4",
    "Mayıs 2021": "https://medium.com/tipografi/tipografi-haberleri-mayıs-2021-d8cf2966d3ea",
    "Haziran 2021": "https://medium.com/tipografi/tipografi-haberleri-haziran-2021-623c191197a7",
    "Temmuz 2021": "https://medium.com/tipografi/tipografi-haberleri-temmuz-2021-83e6b71d3f15",
    "Ağustos 2021": "https://medium.com/tipografi/tipografi-haberleri-ağustos-2021-b87f55e89171",
    "Eylül 2021": "https://medium.com/tipografi/tipografi-haberleri-eylül-2021-9ac0312435e3",
    "Ekim 2021": "https://medium.com/tipografi/tipografi-haberleri-ekim-2021-cfac56c9bf63",
    "Kasım 2021": "https://medium.com/tipografi/tipografi-haberleri-kasım-2021-315e190a2dca",
    "Aralık 2021": "https://medium.com/tipografi/tipografi-haberleri-aralık-2021-28519238bd95",
    "Ocak 2022": "https://medium.com/tipografi/tipografi-haberleri-ocak-2022-c3389a6d20f7",
    "Şubat 2022": "https://medium.com/tipografi/tipografi-haberleri-şubat-2022-9d9bcbc58c9c",
    "Mart 2022": "https://medium.com/tipografi/tipografi-haberleri-mart-2022-8b40ca83e307",
    "Nisan 2022": "https://medium.com/tipografi/tipografi-haberleri-nisan-2022-23a68f22d53",
    "Mayıs 2022": "https://medium.com/tipografi/tipografi-haberleri-mayıs-2022-c258249bd466",
    "Haziran 2022": "https://medium.com/tipografi/tipografi-haberleri-haziran-2022-55f6efe264b",
    "Temmuz 2022": "https://medium.com/tipografi/tipografi-haberleri-temmuz-2022-5bef2d0161ed",
    "Ağustos 2022": "https://medium.com/tipografi/tipografi-haberleri-ağustos-2022-16cd48b4cf42",
    "Eylül 2022": "https://medium.com/tipografi/tipografi-haberleri-eylül-2022-971dc3981ffd",
    "Ekim 2022": "https://medium.com/tipografi/tipografi-haberleri-ekim-2022-a5a2414d62b8",
    "Kasım 2022": "https://medium.com/tipografi/tipografi-haberleri-kasım-2022-4f991e4c973b",
    "Aralık 2022": "https://medium.com/tipografi/tipografi-haberleri-aralık-2022-812bc46e6f13",
    "Ocak 2023": "https://medium.com/tipografi/tipografi-bülteni-ocak-2023-9dfac3c77718",
    "Şubat 2023": "https://medium.com/tipografi/tipografi-bülteni-şubat-2023-61bc8fd552ce",
    "Mart 2023": "https://medium.com/tipografi/tipografi-bülteni-mart-2023-3a93154ac01b",
    "Nisan 2023": "https://medium.com/tipografi/tipografi-bülteni-nisan-2023-a14f05be724a",
    "Mayıs 2023": "https://medium.com/tipografi/tipografi-bülteni-mayıs-2023-805c3ba8bd36",
    "Haziran 2023": "https://medium.com/tipografi/tipografi-bülteni-haziran-2023-66206d1949ee",
    "Temmuz 2023": "https://medium.com/tipografi/tipografi-bülteni-temmuz-2023-677cf7be9318",
    "Ağustos 2023": "https://medium.com/tipografi/tipografi-bülteni-ağustos-2023-5ee8b04702ec",
    "Eylül 2023": "https://medium.com/tipografi/tipografi-bülteni-eylül-2023-92014965a49a",
    "Ekim 2023": "https://medium.com/tipografi/tipografi-bülteni-ekim-2023-8dfb252f2a1b",
    "Kasım 2023": "https://medium.com/tipografi/tipografi-bülteni-kasım-2023-2ba98f905d1f",
    "Aralık 2023": "https://medium.com/tipografi/tipografi-bülteni-aralık-2023-dc3a5cc03c6a",
    "Ocak 2024": "https://medium.com/tipografi/tipografi-bülteni-ocak-2024-92f521042bae",
    "Şubat 2024": "https://medium.com/tipografi/tipografi-bülteni-şubat-2024-c2e94d6a58ae",
    "Mart 2024": "https://medium.com/tipografi/tipografi-bülteni-mart-2024-7dbe9c27c694",
    "Nisan 2024": "https://medium.com/tipografi/tipografi-bülteni-nisan-2024-df8f79c906db",
    "Mayıs 2024": "https://medium.com/tipografi/tipografi-bülteni-mayıs-2024-b4a80020ec7f",
    "Haziran 2024": "https://medium.com/tipografi/tipografi-bülteni-haziran-2024-2db3b5b4b237",
    "Temmuz 2024": "https://medium.com/tipografi/tipografi-bülteni-temmuz-2024-1e68e9d4a48c",
    "Ağustos 2024": "https://medium.com/tipografi/tipografi-bülteni-ağustos-2024-d8271c2ec119",
    "Eylül 2024": "https://medium.com/tipografi/tipografi-bülteni-eylül-2024-03f75b4d6162",
    "Ekim 2024": "https://medium.com/tipografi/tipografi-bülteni-ekim-2024-6f8a5ee599fc",
    "Kasım 2024": "https://medium.com/tipografi/tipografi-bülteni-kasım-2024-7ac6873bb581",
    "Aralık 2024": "https://medium.com/tipografi/tipografi-bülteni-aralık-2024-b5fc8e46b4ce",
    "Ocak 2025": "https://medium.com/tipografi/tipografi-bülteni-ocak-2025-4f4f7ad5aca1",
    "Şubat 2025": "https://medium.com/tipografi/tipografi-bülteni-şubat-2025-d8c2206c0274",
    "Mart 2025": "https://medium.com/tipografi/tipografi-bülteni-mart-2025-09e6ff1f9a12",
    "Nisan 2025": "https://medium.com/tipografi/tipografi-bülteni-nisan-2025-9ca46327e554",
    "Mayıs 2025": "https://medium.com/tipografi/tipografi-bülteni-mayıs-2025-81cc9ee02d83",
    "Haziran 2025": "https://medium.com/tipografi/tipografi-bülteni-haziran-2025-057366758db6",
    "Temmuz 2025": "https://medium.com/tipografi/tipografi-bülteni-temmuz-2025-f69f62427adc",
    "Ağustos 2025": "https://medium.com/tipografi/tipografi-bülteni-ağustos-2025-410f52e44a70",
    "Eylül 2025": "https://medium.com/tipografi/tipografi-bülteni-eylül-2025-fa7a0941bd68",
    "Ekim 2025": "https://medium.com/tipografi/tipografi-bülteni-ekim-2025-803661d110ac",
    "Kasım 2025": "https://medium.com/tipografi/tipografi-bülteni-kasım-2025-6a52698d71d0",
    "Aralık 2025": "https://medium.com/tipografi/tipografi-bülteni-aralık-2025-119b6d532a2b",
    "Ocak 2026": "https://tipografi.substack.com/p/tipografi-bulteni-ocak-2026",
    "Şubat 2026": "https://tipografi.substack.com/p/tipografi-bulteni-subat-2026",
    "Mart 2026": "https://tipografi.substack.com/p/tipografi-bulteni-mart-2026",
    "Nisan 2026": "https://tipografi.substack.com/p/tipografi-bulteni-nisan-2026",
    "Mayıs 2026": "https://tipografi.substack.com/p/tipografi-bulteni-mays-2026",
    "Haziran 2026": "https://tipografi.substack.com/p/tipografi-bulteni-haziran-2026",
    "Temmuz 2026": "https://tipografi.substack.com/p/tipografi-bulteni-temmuz-2026",
    "Ağustos 2026": "https://tipografi.substack.com/p/tipografi-bulteni-agustos-2026",
    "Eylül 2026": "https://tipografi.substack.com/p/tipografi-bulteni-eylul-2026"
}

POPULAR_TOPICS = [
    "Değişken Yazıtipi", "Monotype", "Gutenberg", "Yapay Zekâ",
    "Lisanslama", "Kaligrafi", "TDC", "Google Fonts", "Arial",
]
ALL_YEARS = "Tümü"
PAGE_SIZE = 20
APP_DIR = Path(__file__).resolve().parent


def find_database() -> Optional[Path]:
    """Find the existing SQLite archive without moving or modifying it."""
    candidates = []
    configured = os.environ.get("TIPOGRAFI_DB_PATH")
    if configured:
        candidates.append(Path(configured).expanduser())
    candidates.extend([APP_DIR / "tipografi_arsivi.db", Path.cwd() / "tipografi_arsivi.db"])
    for candidate in candidates:
        if candidate.is_file():
            return candidate.resolve()
    return None


@st.cache_resource(show_spinner=False)
def get_connection(db_uri: str) -> sqlite3.Connection:
    connection = sqlite3.connect(db_uri, uri=True, check_same_thread=False)
    connection.row_factory = sqlite3.Row
    return connection


def issue_name(full_name: str) -> str:
    return full_name.split(":", 1)[-1].strip() if ":" in full_name else full_name.strip()


def get_issue_url(name: str, year: int) -> str:
    clean_name = issue_name(name)
    if clean_name in BULTEN_URLS:
        return BULTEN_URLS[clean_name]
    # Same fallback used by the original app for future issues.
    tr_map = str.maketrans("çğıöşüÇĞİÖŞÜ", "cgiosuCGIOSU")
    slug = clean_name.lower().translate(tr_map).replace(" ", "-")
    return f"https://tipografi.substack.com/p/{slug}"


def build_fts_query(query: str) -> str:
    phrase = re.sub(r"\s+", " ", query).strip().replace('"', "")
    return f'"{phrase}"'


def clean_visual_lines(text: str) -> str:
    return "\n".join(
        line for line in text.splitlines()
        if not re.match(r"^\s*(?:\*|_)?\s*Görsel(?:/Video)?\s*:\s*", line, re.I)
    ).strip()


def plain_text(markdown_text: str) -> str:
    text = clean_visual_lines(markdown_text)
    text = re.sub(r"!\[([^\]]*)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"^\s{0,3}#{1,6}\s*", "", text, flags=re.MULTILINE)
    text = re.sub(r"[*_~]", "", text).replace(chr(96), "")
    text = re.sub(r"^\s*[-+>]\s*", "", text, flags=re.MULTILINE)
    return re.sub(r"\s+", " ", text).strip()


def normalize_for_match(text: str) -> str:
    """Normalize accents and Turkish dotted/dotless i for snippet matching."""
    folded = unicodedata.normalize("NFKD", text.casefold().replace("ı", "i"))
    folded = "".join(char for char in folded if not unicodedata.combining(char))
    return " ".join(re.sub(r"[^\w]+", " ", folded, flags=re.UNICODE).split())


def text_contains_query(text: str, query: str) -> bool:
    normalized_text = normalize_for_match(text)
    normalized_query = normalize_for_match(query)
    return bool(normalized_query and normalized_query in normalized_text)


def crop_around_query(sentence: str, query: str, limit: int = 460) -> str:
    if len(sentence) <= limit or len(query) >= limit:
        return sentence
    position = sentence.casefold().find(query.casefold())
    if position < 0:
        return sentence
    start = max(0, position - (limit - len(query)) // 2)
    end = min(len(sentence), start + limit)
    start = max(0, end - limit)
    while start > 0 and not sentence[start - 1].isspace():
        start -= 1
    while end < len(sentence) and not sentence[end - 1].isspace():
        end += 1
    excerpt = sentence[start:end].strip()
    return ("…" if start else "") + excerpt + ("…" if end < len(sentence) else "")


def matching_excerpt(title: str, body: str, query: str) -> str:
    """Choose a sentence that contains the searched phrase, not the article opening."""
    search_body = body
    if "küçük puntolar" in title.casefold():
        matching_lines = [
            line for line in body.splitlines() if text_contains_query(plain_text(line), query)
        ]
        if matching_lines:
            search_body = "\n".join(matching_lines)

    readable = plain_text(search_body)
    sentences = [
        part.strip()
        for part in re.split(r"(?<=[.!?])\s+", readable)
        if part.strip()
    ]
    for sentence in sentences:
        if text_contains_query(sentence, query):
            return crop_around_query(sentence, query)

    # FTS5 also indexes headings and Markdown link destinations. Make those
    # matches explicit if the visible body text has no matching sentence.
    readable_title = plain_text(title)
    if text_contains_query(readable_title, query):
        return f"Başlıkta eşleşme: {readable_title}."
    return f"Aranan ifade “{query}” bu kaydın içeriğindeki bir bağlantıda eşleşiyor."


def highlighted_excerpt(text: str, query: str) -> str:
    """Return escaped HTML with a safe, understated match highlight."""
    if not query:
        return html.escape(text)
    pattern = re.compile(re.escape(query), flags=re.IGNORECASE)
    pieces, cursor = [], 0
    for match in pattern.finditer(text):
        pieces.append(html.escape(text[cursor:match.start()]))
        pieces.append(f'<mark class="search-hit">{html.escape(match.group(0))}</mark>')
        cursor = match.end()
    pieces.append(html.escape(text[cursor:]))
    return "".join(pieces)


def result_filter(query: str, year: str) -> tuple[str, list]:
    clauses = ["haberler_fts MATCH ?"]
    parameters = [build_fts_query(query)]
    if year != ALL_YEARS:
        clauses.append("h.yil = ?")
        parameters.append(int(year))
    return " AND ".join(clauses), parameters


def get_counts(connection: sqlite3.Connection) -> tuple[int, int]:
    row = connection.execute(
        "SELECT COUNT(DISTINCT dosya_adi), COUNT(*) FROM haberler"
    ).fetchone()
    return int(row[0] or 0), int(row[1] or 0)


def get_years(connection: sqlite3.Connection) -> list[str]:
    rows = connection.execute(
        "SELECT DISTINCT yil FROM haberler WHERE yil IS NOT NULL ORDER BY yil DESC"
    ).fetchall()
    return [str(row[0]) for row in rows if row[0]]


def count_matches(connection: sqlite3.Connection, where: str, params: list) -> tuple[int, int]:
    row = connection.execute(
        f"""SELECT COUNT(*), COUNT(DISTINCT h.bulten_adi)
            FROM haberler_fts JOIN haberler h ON haberler_fts.rowid = h.id
            WHERE {where}""",
        params,
    ).fetchone()
    return int(row[0] or 0), int(row[1] or 0)


def fetch_matches(connection: sqlite3.Connection, where: str, params: list, page: int) -> list:
    return connection.execute(
        f"""SELECT h.id, h.bulten_adi, h.yil, h.ay, h.baslik, h.icerik
            FROM haberler_fts JOIN haberler h ON haberler_fts.rowid = h.id
            WHERE {where}
            ORDER BY h.yil DESC, h.id DESC LIMIT ? OFFSET ?""",
        [*params, PAGE_SIZE, (page - 1) * PAGE_SIZE],
    ).fetchall()


def get_year_distribution(connection: sqlite3.Connection, where: str, params: list) -> pd.DataFrame:
    rows = connection.execute(
        f"""SELECT h.yil, COUNT(*) AS adet
            FROM haberler_fts JOIN haberler h ON haberler_fts.rowid = h.id
            WHERE {where} GROUP BY h.yil ORDER BY h.yil""",
        params,
    ).fetchall()
    values = {int(row["yil"]): int(row["adet"]) for row in rows}
    years = list(range(2019, max(values.keys(), default=2026) + 1))
    return pd.DataFrame(
        {"Gelişme sayısı": [values.get(year, 0) for year in years]},
        index=[str(year) for year in years],
    )


def set_page(page: int) -> None:
    st.session_state["archive_page"] = page


def choose_topic(topic: str) -> None:
    st.session_state["archive_query"] = topic
    st.session_state["archive_page"] = 1


def copy_button_markup(value: str) -> str:
    """Build a compact, accessible clipboard button for an APA citation."""
    safe_value = html.escape(value, quote=True)
    return f"""<!doctype html>
<html lang="tr">
<head>
<meta charset="utf-8">
<style>
* {{ box-sizing: border-box; }}
html, body {{ margin: 0; padding: 0; background: transparent; overflow: hidden; }}
button {{
  display: block; width: 100%; height: 48px; padding: 0 .8rem;
  border: 1px solid #1d1c1a; border-radius: 10px;
  background: #1d1c1a; color: #fff;
  font: 600 .88rem/1.2 -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  cursor: pointer; transition: background-color 120ms ease, border-color 120ms ease;
}}
button:hover {{ background: #393733; border-color: #393733; }}
button:focus-visible {{ outline: 3px solid rgba(129, 81, 62, .55); outline-offset: 2px; }}
button[data-copied="true"] {{ background: #52634b; border-color: #52634b; }}
</style>
</head>
<body>
<button id="copyCitation" type="button" data-copy="{safe_value}"
        aria-label="APA 7 alıntısını panoya kopyala" aria-live="polite">Kopyala</button>
<script>
const button = document.getElementById("copyCitation");
function fallbackCopy(text) {{
  const field = document.createElement("textarea");
  field.value = text;
  field.setAttribute("readonly", "");
  field.style.position = "fixed";
  field.style.opacity = "0";
  document.body.appendChild(field);
  field.select();
  const copied = document.execCommand("copy");
  field.remove();
  return copied;
}}
button.addEventListener("click", async () => {{
  const text = button.dataset.copy;
  try {{
    if (navigator.clipboard && window.isSecureContext) {{
      try {{ await navigator.clipboard.writeText(text); }}
      catch (error) {{ if (!fallbackCopy(text)) throw error; }}
    }} else if (!fallbackCopy(text)) {{
      throw new Error("Clipboard unavailable");
    }}
    button.textContent = "Kopyalandı";
    button.dataset.copied = "true";
    button.setAttribute("aria-label", "APA 7 alıntısı kopyalandı");
  }} catch (error) {{
    button.textContent = "Kopyalanamadı";
    button.setAttribute("aria-label", "APA 7 alıntısı kopyalanamadı");
  }}
  window.setTimeout(() => {{
    button.textContent = "Kopyala";
    delete button.dataset.copied;
    button.setAttribute("aria-label", "APA 7 alıntısını panoya kopyala");
  }}, 1600);
}});
</script>
</body>
</html>"""


db_path = find_database()
if db_path is None:
    st.error(
        "Arşiv veritabanı bulunamadı. tipografi_arsivi.db dosyasını app.py ile "
        "aynı klasöre koyun ya da TIPOGRAFI_DB_PATH ortam değişkeniyle yolunu belirtin."
    )
    st.stop()

try:
    conn = get_connection(db_path.as_uri() + "?mode=ro")
    total_issues, total_articles = get_counts(conn)
    available_years = get_years(conn)
except (sqlite3.Error, OSError) as error:
    st.error(f"Arşiv veritabanı okunamadı: {error}")
    st.stop()


st.markdown(
    '<div class="brand-header"><div class="brand-identity">'
    f'<img class="brand-logo" src="{LOGO_URL}" '
    'alt="Türkçe Tipografi Topluluğu logosu">'
    '<div><div class="brand-name">Türkçe Tipografi Topluluğu</div></div></div>'
    '<div class="brand-links"><a href="https://tipografi.substack.com/">Substack</a>'
    '　·　<a href="https://medium.com/tipografi">Medium</a></div></div>',
    unsafe_allow_html=True,
)

st.markdown('<hr class="hero-rule">', unsafe_allow_html=True)
st.title("Tipografi Bülteni Arşivi")
st.markdown(
    '<div class="hero-copy">Tipografi kültürüne dair haberleri, yazı tasarımını '
    "ve görsel iletişim dünyasındaki gelişmeleri arayın. 93 sayıdan oluşan "
    "arşivin tamamı içinde keşfe başlayın.</div>",
    unsafe_allow_html=True,
)

stat_items = []
for label, value in zip(
    ("Yayımlanan sayı", "İndekslenen gelişme", "ARŞİV KAPSAMI"),
    (f"{total_issues:,}", f"{total_articles:,}",
     f"{min(available_years)}—{max(available_years)}" if available_years else "—"),
):
    stat_items.append(
        '<div class="stat-item">'
        f'<div class="stat-label">{html.escape(label)}</div>'
        f'<div class="stat-value">{html.escape(value)}</div>'
        '</div>'
    )
st.markdown(
    '<div class="stat-grid">' + "".join(stat_items) + '</div>',
    unsafe_allow_html=True,
)

st.markdown('<hr class="hero-rule">', unsafe_allow_html=True)
st.markdown('<div class="section-eyebrow">ARŞİVDE ARA</div>', unsafe_allow_html=True)

with st.form("archive_search"):
    search_col, year_col, submit_col = st.columns(
        [5, 1.6, 1.05], vertical_alignment="bottom"
    )
    with search_col:
        st.text_input(
            "Aranacak ifade", key="archive_query",
            placeholder="Örn. değişken yazıtipi, Monotype, kaligrafi",
        )
    with year_col:
        st.selectbox("Yıl", [ALL_YEARS, *available_years], key="archive_year")
    with submit_col:
        st.form_submit_button("Ara", type="primary", use_container_width=True)

st.markdown("**Öne çıkan aramalar**")
for row_start in range(0, len(POPULAR_TOPICS), 3):
    topic_cols = st.columns(3)
    for offset, topic in enumerate(POPULAR_TOPICS[row_start:row_start + 3]):
        with topic_cols[offset]:
            st.button(
                topic, key=f"topic_{row_start + offset}", on_click=choose_topic,
                args=(topic,), use_container_width=True,
            )

query = str(st.session_state.get("archive_query", "")).strip()
selected_year = str(st.session_state.get("archive_year", ALL_YEARS))
filter_key = (query.casefold(), selected_year)
if st.session_state.get("_archive_filter_key") != filter_key:
    st.session_state["_archive_filter_key"] = filter_key
    st.session_state["archive_page"] = 1
current_page = max(1, int(st.session_state.get("archive_page", 1)))

if not query:
    st.info(
        "Bir konu yazarak tüm bültenlerde arayın ya da öne çıkan aramalardan "
        "birini seçin. Sonuçlar en yeni sayıdan başlayarak listelenir."
    )
else:
    try:
        where, params = result_filter(query, selected_year)
        with st.spinner("Arşiv taranıyor…"):
            result_count, issue_count = count_matches(conn, where, params)
            page_count = max(1, (result_count + PAGE_SIZE - 1) // PAGE_SIZE)
            current_page = min(current_page, page_count)
            rows = fetch_matches(conn, where, params, current_page) if result_count else []
            distribution = get_year_distribution(conn, where, params) if result_count else None
    except sqlite3.Error as error:
        st.error(f"Bu arama çalıştırılamadı. Başka bir ifade deneyin. Veritabanı yanıtı: {error}")
        rows = []
        result_count = issue_count = 0
        page_count = 1
        distribution = None

    if result_count:
        st.markdown(
            f"**{result_count:,}** gelişme · **{issue_count}** bülten"
            f"　<span style='color:#716e68'>·　En yeniden eskiye</span>",
            unsafe_allow_html=True,
        )
        with st.expander("Yıllara göre dağılım", expanded=False):
            chart_data = distribution.rename_axis("Yıl").reset_index()
            chart_spec = {
                "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
                "description": "Arama sonuçlarının yıllara göre dağılımı.",
                "background": "#f7f6f3",
                "height": 220,
                "mark": {"type": "bar", "color": "#81513e"},
                "encoding": {
                    "x": {
                        "field": "Yıl",
                        "type": "ordinal",
                        "sort": None,
                        "axis": {
                            "title": None,
                            "labelAngle": 0,
                            "labelColor": "#716e68",
                            "labelFontSize": 12,
                            "labelPadding": 10,
                            "tickSize": 0,
                            "domain": False,
                        },
                    },
                    "y": {
                        "field": "Gelişme sayısı",
                        "type": "quantitative",
                        "axis": {
                            "title": None,
                            "labelColor": "#716e68",
                            "gridColor": "#e6e3dd",
                            "gridOpacity": 1,
                            "tickColor": "transparent",
                            "domain": False,
                            "format": "d",
                        },
                    },
                    "tooltip": [
                        {"field": "Yıl", "type": "ordinal", "title": "Yıl"},
                        {
                            "field": "Gelişme sayısı",
                            "type": "quantitative",
                            "title": "Gelişme sayısı",
                        },
                    ],
                },
                "config": {
                    "view": {"stroke": None},
                    "axis": {"labelFont": "sans-serif", "gridWidth": 1},
                },
            }
            st.vega_lite_chart(
                chart_data,
                spec=chart_spec,
                height=260,
                use_container_width=True,
                theme=None,
                alt="Arama sonuçlarının yıllara göre dağılımı",
            )

        for row in rows:
            clean_issue = issue_name(row["bulten_adi"] or "")
            issue_url = get_issue_url(clean_issue, int(row["yil"] or 0))
            body = clean_visual_lines(row["icerik"] or "")
            excerpt = matching_excerpt(row["baslik"] or "", body, query)

            with st.container(border=True):
                st.markdown(
                    '<div class="result-meta">'
                    f'<strong>{html.escape(clean_issue)}</strong>'
                    '</div>',
                    unsafe_allow_html=True,
                )
                st.subheader(row["baslik"] or "Başlıksız gelişme")
                st.markdown(
                    f'<p class="result-excerpt">{highlighted_excerpt(excerpt, query)}</p>',
                    unsafe_allow_html=True,
                )
                st.markdown(f"[Bu sayıyı aç ↗]({issue_url})")

                if body:
                    with st.expander("Tam metni oku", expanded=False):
                        st.markdown(body)

                title = re.sub(r"[*_#]", "", row["baslik"] or "").strip().replace(chr(96), "")
                citation = (
                    f"Türkçe Tipografi Topluluğu. ({int(row['yil'] or 0)}, "
                    f"{row['ay'] or ''}). {title}. Tipografi Bülteni. {issue_url}"
                )
                with st.expander("APA 7 alıntısı", expanded=False):
                    citation_col, copy_col = st.columns(
                        [8, 1.15], vertical_alignment="center"
                    )
                    with citation_col:
                        st.markdown(
                            f'<div class="citation-box">{html.escape(citation)}</div>',
                            unsafe_allow_html=True,
                        )
                    with copy_col:
                        components.html(
                            copy_button_markup(citation), height=52, scrolling=False
                        )

        if page_count > 1:
            st.markdown("")
            prev_col, label_col, next_col = st.columns([1, 2, 1])
            with prev_col:
                st.button(
                    "← Önceki", disabled=current_page <= 1, on_click=set_page,
                    args=(current_page - 1,), use_container_width=True, key="previous_page",
                )
            with label_col:
                st.markdown(
                    f"<p style='text-align:center;color:#716e68'>Sayfa {current_page} / {page_count}</p>",
                    unsafe_allow_html=True,
                )
            with next_col:
                st.button(
                    "Sonraki →", disabled=current_page >= page_count, on_click=set_page,
                    args=(current_page + 1,), use_container_width=True, key="next_page",
                )
    else:
        st.info(
            f"“{query}” ifadesiyle"
            + (f" {selected_year} yılında" if selected_year != ALL_YEARS else "")
            + " eşleşen bir gelişme bulunamadı. Yazımı kontrol edin veya daha kısa bir arama deneyin."
        )

st.markdown('<hr class="hero-rule">', unsafe_allow_html=True)
st.markdown(
    """
    <footer class="archive-footer" aria-label="Alt bilgi">
      <div class="footer-content">
        <div class="footer-name">Türkçe Tipografi Topluluğu</div>
        <div class="footer-actions">
          <div class="footer-subscribe">Bültene abone olmak için <a href="https://tipografi.substack.com/" target="_blank" rel="noopener noreferrer">dokun</a></div>
          <nav class="footer-social" aria-label="Sosyal medya bağlantıları">
          <a href="https://www.facebook.com/tipografi/" target="_blank" rel="noopener noreferrer" aria-label="Facebook" title="Facebook">
            <svg viewBox="0 0 24 24" aria-hidden="true"><path class="icon-fill" d="M13.6 21v-8.2h2.8l.4-3.2h-3.2V7.5c0-.9.3-1.6 1.6-1.6H17V3.1c-.3 0-1.3-.1-2.4-.1-2.4 0-4.1 1.5-4.1 4.3v2.4H7.8v3.2h2.7V21z"/></svg>
          </a>
          <a href="https://x.com/tipografi" target="_blank" rel="noopener noreferrer" aria-label="X" title="X">
            <svg viewBox="0 0 24 24" aria-hidden="true"><path class="icon-fill" d="M18.9 2H22l-6.8 7.8L23 22h-6.2l-4.9-6.4L6.3 22H3.1l7.3-8.4L2.7 2h6.4l4.4 5.9L18.9 2zm-1.1 17.8h1.7L8.4 4.1H6.6z"/></svg>
          </a>
          <a href="https://www.instagram.com/tipografitoplulugu/" target="_blank" rel="noopener noreferrer" aria-label="Instagram" title="Instagram">
            <svg viewBox="0 0 24 24" aria-hidden="true"><rect class="icon-stroke" x="3.2" y="3.2" width="17.6" height="17.6" rx="5.1"/><circle class="icon-stroke" cx="12" cy="12" r="4.1"/><circle class="icon-fill" cx="17.7" cy="6.6" r="1.1"/></svg>
          </a>
          <a href="https://www.youtube.com/@tipografi" target="_blank" rel="noopener noreferrer" aria-label="YouTube" title="YouTube">
            <svg viewBox="0 0 24 24" aria-hidden="true"><path class="icon-fill" d="M23.5 6.2a3 3 0 0 0-2.1-2.1C19.5 3.6 12 3.6 12 3.6s-7.5 0-9.4.5A3 3 0 0 0 .5 6.2 31 31 0 0 0 0 12a31 31 0 0 0 .5 5.8 3 3 0 0 0 2.1 2.1c1.9.5 9.4.5 9.4.5s7.5 0 9.4-.5a3 3 0 0 0 2.1-2.1A31 31 0 0 0 24 12a31 31 0 0 0-.5-5.8z"/><path d="m9.6 15.8 6.2-3.8-6.2-3.8z" fill="var(--paper)"/></svg>
          </a>
          <a href="https://open.spotify.com/show/1Ij0BoHaoobj5Mez7mAS22" target="_blank" rel="noopener noreferrer" aria-label="Spotify" title="Spotify">
            <svg viewBox="0 0 24 24" aria-hidden="true"><path class="icon-fill" d="M12 1.8A10.2 10.2 0 1 0 12 22.2 10.2 10.2 0 0 0 12 1.8z"/><path d="M6.2 9.1c3.8-1.1 8.6-.7 11.7 1.2M7 12.1c3.2-.9 7.3-.5 9.9 1.1M7.8 15c2.6-.7 5.8-.4 7.9.9" fill="none" stroke="var(--paper)" stroke-width="1.4" stroke-linecap="round"/></svg>
          </a>
          <a href="https://tipografi.substack.com/" target="_blank" rel="noopener noreferrer" aria-label="Substack" title="Substack">
            <svg viewBox="0 0 24 24" aria-hidden="true"><path class="icon-fill" d="M3 4h18v2H3zm0 4h18v2H3zm0 4h18v2H3zm0 4h18v5l-9-3.5L3 21z"/></svg>
          </a>
          </nav>
        </div>
      </div>
    </footer>
    """,
    unsafe_allow_html=True,
)
