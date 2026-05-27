import streamlit as st

def apply_global_styles() -> None:
    st.markdown("""
        <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        [data-testid="stHeaderActionElements"] {display: none;}

        .stApp {
            background-color: #fbfbfb;
            font-family: 'Inter', sans-serif;
        }
        .metric-card {
            background-color: white;
            padding: 1.5rem;
            border-radius: 8px;
            border: 1px solid #eaeaea;
            margin-bottom: 1.5rem;
        }
        .dual-value-box {
            border: 1px solid #e0e0e0;
            border-radius: 6px;
            overflow: hidden;
            margin-bottom: 1rem;
        }
        .dual-exact {
            background-color: #f5f7fa;
            padding: 0.75rem 1rem;
            border-bottom: 1px solid #e0e0e0;
            font-family: 'Courier New', Courier, monospace;
            color: #2c3e50;
        }
        .dual-numeric {
            background-color: #ffffff;
            padding: 0.5rem 1rem;
            font-size: 0.9em;
            color: #596a7a;
        }
        .dual-interval {
            background-color: #fdfdfd;
            padding: 0.75rem 1rem;
            font-family: 'Courier New', Courier, monospace;
            color: #34495e;
            text-align: center;
        }
        .table-cell-dual {
            display: flex;
            flex-direction: column;
            border: 1px solid #eee;
            border-radius: 4px;
            overflow: hidden;
            text-align: center;
            min-width: 120px;
        }
        .table-cell-exact {
            padding: 4px;
            background-color: #f8f9fa;
            border-bottom: 1px solid #eee;
            font-family: monospace;
            font-size: 0.9em;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }
        .table-cell-numeric {
            padding: 4px;
            background-color: white;
            font-size: 0.8em;
            color: #666;
        }
        .table-cell-single {
            padding: 8px;
            text-align: center;
            border: 1px solid #eee;
            border-radius: 4px;
            font-family: monospace;
        }
        </style>
    """, unsafe_allow_html=True)
