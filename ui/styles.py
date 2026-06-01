import streamlit as st


def apply_global_styles() -> None:
    st.markdown(
        """
        <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        [data-testid="stHeaderActionElements"] {display: none;}

        .stApp {
            background-color: #fbfbfb;
            font-family: Inter, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
        }
        h1, h2, h3 {
            letter-spacing: 0;
        }
        .dual-value-box {
            border: 1px solid #dedede;
            border-radius: 6px;
            overflow: hidden;
            margin-bottom: 0.75rem;
            background: white;
        }
        .dual-exact {
            background-color: #f5f7fa;
            padding: 0.75rem 1rem;
            border-bottom: 1px solid #dedede;
            font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
            color: #213547;
            overflow-x: auto;
        }
        .dual-numeric {
            background-color: #ffffff;
            padding: 0.55rem 1rem;
            font-size: 0.92rem;
            color: #4d5b68;
            font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
        }
        .dual-interval {
            background-color: #ffffff;
            padding: 0.75rem 1rem;
            font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
            color: #213547;
            overflow-x: auto;
        }
        div[data-testid="stCaptionContainer"] {
            color: #59636e;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
