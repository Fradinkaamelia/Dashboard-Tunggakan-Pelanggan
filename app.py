import streamlit as st
import pandas as pd
import plotly.graph_objs as go
from datetime import datetime
import json
from streamlit_plotly_events import plotly_events
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, DataReturnMode
from scipy.stats import gaussian_kde
import numpy as np
import plotly.graph_objects as go
import plotly.colors as pc
import numpy as np
import ast
import io
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import reportlab
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.lib.colors import navy, whitesmoke, beige, black
from reportlab.pdfgen import canvas

pd.set_option("styler.render.max_elements", 16645589)

# Set page configuration
st.set_page_config(
    page_title="Dashboard Tunggakan - Gas Negara Tbk",
    page_icon="📊",
    layout="wide"
)

# Menambahkan CSS untuk seluruh tampilan aplikasi agar rapi dan menarik
st.markdown("""
    <style>
        /* Umum: Pengaturan untuk keseluruhan halaman */
        body {
            background-color: #f4f4f9;  /* Warna latar belakang yang bersih */
            font-family: 'Arial', sans-serif;
            color: #003366;  /* Warna navy untuk teks */
            margin: 0;
            padding: 0;
        }

        /* Mengatur tampilan konten agar rata di tengah */
        .stApp {
            display: flex;
            justify-content: center;
        }

        /* Tab: Menambahkan padding dan margin agar lebih terpusat */
        .stTabs {
            display: flex;
            justify-content: space-between;  /* Membagi ruang antara tab kiri dan kanan */
            width: 80%;  /* Lebar tab lebih besar dan terpusat */
            margin: 0 auto;
            padding: 20px 0;

        }
        .stTabs div[role="tablist"] div[role="tab"] {
            padding: 12px 20px;
            margin: 0 10px;  /* Memberikan jarak antar tab */
            background-color: white;
            color: #003366;
            font-weight: bold;
            border-radius: 5px;
            transition: background-color 0.3s ease;
        }
        /* Tab hover effect */
        .stTabs div[role="tablist"] div[role="tab"]:hover {
            background-color: #003366;
            color: white;
        }
        .stTabs div[role="tablist"] div[role="tab"].stTab--active {
            background-color: #E91E63;  /* Warna merah untuk tab aktif */
            color: white;
        }
        
        /* Styling untuk elemen tab aktif */
        .stTabs div[role="tablist"] div[role="tab"]:first-child {
            margin-left: 0;  /* Tidak ada margin kiri untuk tab pertama */
        }
        
        /* Memastikan ada jarak antar tab */
        .stTabs div[role="tablist"] div[role="tab"]:not(:last-child) {
            border-right: 2px solid #003366;  /* Pembatas antar tab */
        }
        /* Unggah data */
        .upload-message {
            text-align: center;
            padding: 50px;
            background-color: #f8f9fa;
            border-radius: 10px;
            margin: 50px 0;
            border: 2px dashed #003366;
        }
        .upload-message h3 {
            color: #003366;
            margin-bottom: 20px;
        }
        /* Header Styling */
        h1, h2, h3 {
            font-weight: bold;
            color: #003366;
            text-align: center;
        }

        /* Tabel Header Styling (AgGrid) */
        .ag-theme-streamlit .ag-header-cell {
            background-color: #003366 !important;
            color: white !important;
            font-weight: bold !important;
        }

        .ag-theme-streamlit .ag-row {
            background-color: white !important;
            color: #003366 !important;
        }

        .ag-theme-streamlit .ag-row-hover {
            background-color: #f1f1f1 !important;
        }

        /* Kolom dan Pengaturan Tombol */
        .stButton>button {
            background-color: #E91E63;  /* Merah Pertamina */
            color: white;
            font-weight: bold;
            border-radius: 5px;
            border: none;
            padding: 10px 20px;
            transition: background-color 0.3s ease;
        }

        .stButton>button:hover {
            background-color: #C2185B;
        }

        .stMetric {
            background-color: #ffffff;
            color: #003366;
            font-size: 14px;  /* Ukuran font lebih besar */
            font-weight: bold;
            padding: 15px 30px;  /* Padding lebih besar */
            border-radius: 15px;  /* Radius lebih besar */
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);  /* Shadow lebih tebal */
            transition: all 0.3s ease;
            width: 100%;  /* Memperpanjang elemen untuk mengambil lebar penuh kontainer */
            max-width: 400px;  /* Maksimal lebar */
            margin: 10px auto;  /* Menambahkan margin otomatis */
            position: relative;  /* Posisi relative untuk elemen tooltip */
        }

        .stMetric:hover {
            background-color: #f4f4f9;
            transform: translateY(-2px);  /* Efek hover untuk menaikkan sedikit */
        }

        .tooltip {
            position: absolute;
            top: -30px;  /* Menempatkan tooltip di atas elemen */
            left: 50%;
            transform: translateX(-50%);
            background-color: rgba(0, 0, 0, 0.8);
            color: white;
            padding: 8px 12px;
            border-radius: 5px;
            font-size: 12px;
            visibility: hidden;
            opacity: 0;
            transition: opacity 0.3s ease, visibility 0s linear 0.3s;
            z-index: 1;
        }

        .stMetric:hover .tooltip {
            visibility: visible;
            opacity: 1;
            transition: opacity 0.3s ease;
        }

        /* CSS untuk kolom-kolom */
        .stDataFrame {
            color: #003366;
            font-weight: bold;
            font-size: 16px;
        }

        /* Styling untuk expander */
        .streamlit-expanderHeader {
            background-color: #003366;
            color: white;
            font-weight: bold;
        }

        .streamlit-expanderContent {
            background-color: #f4f4f9;
            padding: 15px;
        }

        /* Input Fields */
        .stTextInput input {
            border: 2px solid #003366;
            background-color: #ffffff;
            padding: 8px;
            color: #003366;
            font-size: 14px;
        }

        .stSelectbox select, .stMultiselect select {
            background-color: #ffffff;
            color: #003366;
            padding: 8px;
            border: 2px solid #003366;
        }

        /* Styling untuk file uploader */
        .stFileUploader {
            color: #003366;
            border: 2px dashed #003366;
            padding: 20px;
            border-radius: 5px;
            background-color: #ffffff;
        }

        .stFileUploader:hover {
            background-color: #f4f4f9;
        }

        /* Link Styling */
        a {
            color: #E91E63;
            font-weight: bold;
            text-decoration: none;
        }

        a:hover {
            color: #C2185B;
        }

        /* Expander Styling */
        .streamlit-expanderHeader {
            font-weight: bold;
            color: #ffffff;
            background-color: #003366;
        }

        .streamlit-expanderContent {
            background-color: #f4f4f9;
        }

        /* Dropdown and Selectbox */
        .stSelectbox select, .stMultiselect select {
            border-radius: 5px;
            padding: 10px;
            background-color: #ffffff;
            color: #003366;
            border: 2px solid #003366;
        }

        /* Tabel styling */
        .stTable {
            font-size: 14px;
            color: #003366;
            font-weight: bold;
        }

        /* Section Styling */
        .stSection {
            margin-bottom: 20px;
        }

        /* Section Headers */
        .stSubheader {
            font-size: 18px;
            color: #003366;
            font-weight: bold;
        }

        /* Bottom Styling */
        footer {
            background-color: #003366;
            color: white;
            text-align: center;
            padding: 10px;
            font-size: 14px;
        }

        /* Highlighting Status in DataFrame */
        .highlight-status {
            background-color: #FFEB3B;
        }
        .big-title {
            color: white !important; /* Warna putih untuk teks */
            text-align: center;
            font-weight: bold;
            margin-top: 30px;
            margin-bottom: 25px;
            font-size: 3rem; /* Ukuran font lebih besar untuk header */
            background-color: #003364;  /* Latar belakang navy */
            padding: 20px 0;
            letter-spacing: 2px; /* Spasi antar huruf */
        }
        /* Pembatasan teks dan padding di dalam tabel */
        .stTable .stDataFrame {
            padding: 8px;
            word-wrap: break-word;  /* Agar teks panjang tidak meluber keluar */
        }

        /* Pastikan elemen teks tidak menyatu */
        .stDataFrame p {
            margin-bottom: 10px;  /* Memberikan jarak antar paragraf */
        }

        .stDataFrame h1, .stDataFrame h2, .stDataFrame h3 {
            padding-bottom: 5px;
        }

         /* Styling untuk konten tab */
        .stTab {
            width: 100%;  /* Membuat tab terpusat dan mengisi ruang */
            background-color: #ffffff;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
        }

        /* Untuk menambah kesan elegan pada expander */
        .streamlit-expanderHeader {
            font-size: 16px;
            font-weight: bold;
            color: #ffffff;
            background-color: #003366; /* Navy background */
            padding: 10px 15px;
        }
        /* Menambahkan padding pada container di tab */
        .stContainer {
            margin: 20px;
            padding: 20px;
        .streamlit-expanderHeader {
            font-size: 14px !important;
        }
        .css-1aumxhk {
            font-size: 12px !important;  # Ukuran teks angka pada metric
        }
        .css-1d391kg {
            font-size: 12px !important;  # Ukuran teks label pada metric
        }
        .css-2k5cm3 {
            font-size: 12px !important;  # Ukuran teks kategori pada metric
        }
        .stMetricCustom {
        background-color: #ffffff;
        color: #003366;
        font-size: 10px;  /* Mengurangi ukuran font */
        font-weight: bold;
        padding: 8px 20px;  /* Padding yang lebih kecil */
        border-radius: 10px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        transition: all 0.3s ease;
        display: inline-block;  /* Membuat ukuran kotak sesuai dengan kontennya */
        max-width: none;  /* Menghilangkan batas lebar */
        white-space: nowrap;  /* Menghindari pemotongan tulisan */
        overflow: hidden;  /* Menyembunyikan konten yang meluap */
    }

    .stMetricCustom:hover {
        background-color: #f4f4f9;
    }

    .stMetricCustom span {
        font-size: 12px;  /* Ukuran teks untuk label */
        margin-right: 10px;
    }

    .stMetricCustom .value {
        font-size: 14px;  /* Ukuran teks untuk nilai */
        font-weight: normal;
    }

        
    </style>
""", unsafe_allow_html=True)
def show_custom_metric(label, value):
    # HTML dan CSS untuk menampilkan st.metric dengan pengaturan ukuran font dan kotak fleksibel
    metric_html = f"""
    <div class="stMetricCustom">
        <span>{label}</span>
        <div class="value">{value}</div>
    </div>
    """
    st.markdown(metric_html, unsafe_allow_html=True)

def highlight_status(row):
    if row['Status'] != 'Active':
        return ['background-color: #FFFACD'] * len(row)  # Warna kuning pastel
    return [''] * len(row)


def show_upload_message():
    st.markdown("""
        <div class="upload-message">
            <h3>📤 Data Belum Tersedia</h3>
            <p>Silakan unggah file terlebih dahulu pada tab 'Input Data'</p>
        </div>
    """, unsafe_allow_html=True)
def handle_missing_columns(df_raw, missing_cols):
    with st.form("missing_columns_form"):
        input_values = {}
        for col in missing_cols:
            # Sesuaikan jenis input berdasarkan kolom yang hilang
            if 'No HP' in col or 'Tagihan' in col or 'Denda' in col:
                input_values[col] = st.text_input(f"Input data untuk kolom '{col}'", key=f"missing_{col}")
            else:
                input_values[col] = st.text_input(f"Input data untuk kolom '{col}'", key=f"missing_{col}")
        
        submitted = st.form_submit_button("Tambahkan Kolom yang Hilang")
        
        if submitted:
            # Proses menambahkan nilai default untuk kolom yang hilang
            for col in missing_cols:
                default_value = input_values[col]
                if col in ["Tagihan", "Denda", "Jaminan Pembayaran"]:  # Kolom numerik
                    try:
                        default_value = float(default_value)
                    except:
                        pass  # Jika konversi gagal, tetap sebagai string
                df_raw[col] = default_value

            # Simpan df_raw yang sudah diperbarui ke session_state agar bisa diakses di tab lain
            st.session_state.df_raw = df_raw  # Simpan di session_state.df_raw
            st.session_state.df_processed = df_raw  # Simpan juga di session_state.df_processed untuk pemrosesan lebih lanjut
            st.session_state.data_loaded = True
            st.success(f"Kolom yang hilang telah ditambahkan dengan nilai '{default_value}'.")
st.markdown("<h1 class='big-title'>Dashboard Tunggakan Pelanggan</h1>", unsafe_allow_html=True)
st.write(" ")

def main():
    if 'df_processed' not in st.session_state:
        st.session_state.df_processed = None
        st.session_state.data_loaded = False
        
        st.session_state.clicked_month = None   # Untuk Line Chart
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 1  # untuk pagination


    # with st.sidebar:
    #     st.title("Dashboard Tunggakan")
        # st.markdown("""
        # ### Panduan Singkat:
        # 1. Unggah data di 'Input Data'.
        # 2. Pilih bulan terakhir (misal "Dec-2024").
        # 3. Kolom-kolom setelah bulan tersebut tidak akan ditampilkan di tabel.
        # 4. Tabel utama ditampilkan dalam pagination per 50 baris.
        # """)
        # st.markdown("---")
        # st.markdown("#### Kontak")
        # st.markdown("""
        # - **Email**: helpdesk@pgn.co.id
        # - **Telepon**: +62000-0000-0000
        # """)

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["Input Data", "Durasi Tunggakan", "Total Tunggakan", "Detail Pelanggan", 'Total Pelanggan dalam Range Tunggakan', 'Jumlah Penggan & Total Tunggakan per Kategori'])

    with tab1:
        st.title("Input Data Tunggakan")

        uploaded_file = st.file_uploader("Unggah file .xlsx atau .parquet", type=["xlsx", "parquet"])

        if uploaded_file is not None:
            try:
                # --- 1) Baca data ---
                if uploaded_file.name.endswith('.xlsx'):
                    df_raw = pd.read_excel(uploaded_file, engine='openpyxl')
                    if isinstance(df_raw, pd.DataFrame):
                        if df_raw.empty:
                            raise ValueError("File Excel kosong atau tidak memiliki data.")
                        else:
                            df_raw.columns = df_raw.columns.str.strip()  # Membersihkan spasi pada kolom
                    else:
                        raise ValueError("Data yang dimuat bukan DataFrame.")
                else:
                    df_raw = pd.read_parquet(uploaded_file)

                required_cols = [
                    "Noref", "Nama", "Alamat", "Customer Management", "Kelurahan",
                    "Bulan Tagihan", "Tagihan", "Denda", "Jaminan Pembayaran",
                    "Jenis Pelanggan", "Jenis Rekening", "Buku", "Status"
                ]
                missing = [c for c in required_cols if c not in df_raw.columns]
                if missing:
                    st.error(f"Kolom wajib tidak lengkap. Tidak ditemukan: {', '.join(missing)}")
                    handle_missing_columns(df_raw, missing)
                else:
                    # Jika kolom tidak hilang, lanjutkan proses
                    df_raw = df_raw.loc[:, 'No':'Status'] if 'No' in df_raw.columns and 'Status' in df_raw.columns else df_raw
                    df_raw = df_raw.dropna(how='all')
                    df_raw.columns = df_raw.columns.str.strip()

                    # Mengubah semua kolom menjadi tipe string
                    df_raw['Nama'] = df_raw['Nama'].astype(str).fillna('')
                    df_raw['No HP'] = df_raw['No HP'].astype(str).fillna('')
                    df_raw['Alamat'] = df_raw['Alamat'].astype(str).fillna('')
                    df_raw['Customer Management'] = df_raw['Customer Management'].astype(str).fillna('')
                    df_raw['Kelurahan'] = df_raw['Kelurahan'].astype(str).fillna('')

                    # Simpan data ke session_state agar dapat diakses di seluruh tab
                    st.session_state.df_processed = df_raw
                    st.session_state.df_raw = df_raw  # Pastikan df_raw juga disimpan di session_state
                    st.session_state.data_loaded = True
                    st.success("Data berhasil diunggah dan diproses!")

                    df_raw = df_raw.loc[:, 'No':'Status'] if 'No' in df_raw.columns and 'Status' in df_raw.columns else df_raw
                    if 'No' in df_raw.columns:
                        df_raw = df_raw[~df_raw['No'].astype(str).str.contains(':', na=False)]

                if 'df_raw' in st.session_state:
                    df_raw = st.session_state.df_raw

                # --- 2) Pivot data ---
                df_raw['Bulan Tagihan'] = pd.to_datetime(df_raw['Bulan Tagihan'], errors='coerce')
                df_raw['Bulan-Tahun'] = df_raw['Bulan Tagihan'].dt.to_period('M').astype(str)

                pivoted = df_raw.pivot_table(
                    index=['Noref','Nama'],
                    columns='Bulan-Tahun',
                    values='Tagihan',
                    aggfunc='sum'
                ).reset_index()

                other_cols = [
                    'No HP', 'Alamat', 'Kelurahan', 'Customer Management', 'Denda',
                    'Jaminan Pembayaran', 'Jenis Pelanggan', 'Jenis Rekening', 'Buku', 'Status'
                ]
                other_data = df_raw.drop_duplicates(subset=['Noref','Nama'])[['Noref','Nama'] + other_cols]
                df_merged = pd.merge(other_data, pivoted, on=['Noref','Nama'], how='left')

                def format_month_year(x):
                    if isinstance(x, str) and '-' in x:
                        try:
                            return pd.to_datetime(x, format='%Y-%m').strftime('%b-%Y')
                        except:
                            return x
                    return str(x).strip()

                df_merged.columns = [format_month_year(c) for c in df_merged.columns]
                df_merged = df_merged.rename(columns={
                    'Nama':'Nama Pelanggan',
                    'Noref':'No Reff.',
                    'Jenis Pelanggan':'Kategori Pelanggan'
                })

                # --- 3) Urutkan kolom & Pilih Bulan Terakhir ---
                all_month_cols = [c for c in df_merged.columns if '-' in c]
                if not all_month_cols:
                    st.warning("Tidak ada kolom Bulan-Tahun.")
                    return

                def parse_my(s):
                    return datetime.strptime(s, '%b-%Y')

                sorted_month_cols = sorted(all_month_cols, key=parse_my)

                chosen_month = st.selectbox(
                    "Pilih Bulan Terakhir (batas perhitungan)",
                    options=sorted_month_cols,
                    index=len(sorted_month_cols)-1
                )

                # Index untuk chosen_month
                chosen_idx = sorted_month_cols.index(chosen_month)
                # relevant_cols => semua bulan s/d chosen_month (termasuk chosen_month)
                relevant_cols = sorted_month_cols[:chosen_idx+1]

                # Pastikan numeric
                df_merged[sorted_month_cols] = df_merged[sorted_month_cols].apply(pd.to_numeric, errors='coerce').abs()

                # --- 4) Hitung tunggakan + hapus kolom setelah chosen_month ---
                # Kolom setelah chosen_month
                after_chosen = sorted_month_cols[chosen_idx+1:]
                # Buang setelah chosen_month dari tampilan (tapi kita bisa tetap simpan di memori jika mau).
                # Di sini kita langsung droplast columns agar tidak muncul di df_merged:
                df_merged.drop(columns=after_chosen, inplace=True, errors='ignore')

                # Sekarang df_merged hanya memiliki kolom s/d chosen_month
                # Hitung jumlah_bulan_tunggakan + total_tunggakan (hanya dari kolom sebelum chosen_month)
                # untuk itu relevant_cols_without_chosen = sorted_month_cols[:chosen_idx] => sampai (chosen_idx-1)
                relevant_cols_for_tunggakan = sorted_month_cols[:chosen_idx]  # dec-2024 tidak diikutkan, sesuai request
                # Jika Anda ingin memasukkan chosen_month juga, tinggal +1
                # -> relevant_cols_for_tunggakan = relevant_cols

                df_merged['jumlah_bulan_tunggakan'] = df_merged[relevant_cols_for_tunggakan].apply(
                    lambda row: (row.notna() & (row != 0)).sum(),
                    axis=1
                )
                df_merged['jumlah_bulan_tunggakan'] = df_merged['jumlah_bulan_tunggakan'].astype(int)
                df_merged['total_tunggakan'] = df_merged[relevant_cols_for_tunggakan].fillna(0).sum(axis=1)

                # detail_tunggakan
                def build_detail(row):
                    detail = {}
                    for c in relevant_cols_for_tunggakan:
                        val = row[c]
                        if pd.notna(val) and val != 0:
                            detail[c] = val
                    return json.dumps(detail)
                df_merged['detail_tunggakan'] = df_merged.apply(build_detail, axis=1)

                # penentuan Status => menggunakan kolom chosen_month
                df_merged['Status'] = df_merged[chosen_month].apply(
                    lambda val: 'Active' if pd.notna(val) and val != 0 else 'Inactive'
                )

                # Simpan ke session
                st.session_state.df_processed = df_merged
                st.session_state.data_loaded = True

                # --- 5) Tampilkan dataframe dengan PAGINATION ---
                st.subheader("Data Hasil Perhitungan Tunggakan")

                if st.session_state.df_processed is not None:
                    rows_per_page = 50
                    total_rows = len(st.session_state.df_processed)
                    total_pages = (total_rows // rows_per_page) + (1 if total_rows % rows_per_page != 0 else 0)

                    # Pastikan current_page dalam range
                    if st.session_state.current_page < 1:
                        st.session_state.current_page = 1
                    elif st.session_state.current_page > total_pages:
                        st.session_state.current_page = total_pages

                    start_idx = (st.session_state.current_page - 1) * rows_per_page
                    end_idx = start_idx + rows_per_page
                    df_page = st.session_state.df_processed.iloc[start_idx:end_idx].copy()

                    # Format
                    numeric_cols = df_page.select_dtypes(include=['int64','float64']).columns.tolist()
                    format_dict = {c: "{:,.0f}" for c in numeric_cols}
                    if 'total_tunggakan' in df_page.columns:
                        format_dict['total_tunggakan'] = "Rp {:,.0f}"

                    styled_df = df_page.style.format(format_dict).apply(highlight_status, axis=1)
                    st.dataframe(styled_df, height=600, use_container_width=True)

                    # Indikator Halaman
                    st.text(f"Halaman {st.session_state.current_page} dari {total_pages}")
                    colA, colB, colC = st.columns([1, 3, 1])
                    with colA:
                        if st.button("⬅ Previous") and st.session_state.current_page > 1:
                            st.session_state.current_page -= 1
                            # Tidak perlu st.experimental_rerun(), cukup memodifikasi current_page
                            st.session_state.current_page = max(st.session_state.current_page, 1)  # Pastikan halaman tidak kurang dari 1
                            st.session_state.data_loaded = True  # Menandakan data sudah dimuat

                    with colC:
                        if st.button("Next ⮕") and st.session_state.current_page < total_pages:
                            st.session_state.current_page += 1
                            # Tidak perlu st.experimental_rerun(), cukup memodifikasi current_page
                            st.session_state.current_page = min(st.session_state.current_page, total_pages)  # Pastikan halaman tidak lebih dari total_pages

                # Tombol untuk mengunduh data langsung
                file_path = 'Data Piutang Pelanggan.xlsx'

                with st.spinner("Mempersiapkan file untuk diunduh..."):
                    # Simpan file sementara saat tombol unduh ditekan
                    st.session_state.df_processed.to_excel(file_path, index=False)

                st.download_button(
                    label="📥 Unduh Data",
                    data=open(file_path, 'rb'),
                    file_name=file_path,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                )

                # Additional Information
                st.subheader("Informasi Dataset")
                df = df_merged.copy()
                total_rows = len(df)
                month_year_cols = [col for col in df.columns if '-' in col]

                if month_year_cols:
                    def parse_month_year(s):
                        return datetime.strptime(s, '%b-%Y')
                    sorted_months = sorted(month_year_cols, key=parse_month_year)
                    min_month = sorted_months[0]
                    max_month = sorted_months[-1]
                    range_bulan = f"{min_month}|{max_month}"
                else:
                    range_bulan = "Tidak ada kolom Bulan"

                total_tunggakan = df['total_tunggakan'].sum()
                rata_rata_bulan = df['jumlah_bulan_tunggakan'].mean()
                median_bulan = df['jumlah_bulan_tunggakan'].median()
                rata_rata_tunggakan = df['total_tunggakan'].mean()
                median_tunggakan = df['total_tunggakan'].median()

                if 'Nama Pelanggan' in df.columns and 'No Reff.' in df.columns:
                    top_pelanggan = df.sort_values(by='total_tunggakan', ascending=False)[
                        ['No Reff.', 'Nama Pelanggan', 'Alamat', 'Kelurahan', 'Customer Management', 'total_tunggakan']
                    ].copy()
                    top_pelanggan['total_tunggakan'] = top_pelanggan['total_tunggakan'].apply(lambda x: f"Rp {x:,.0f}")
                else:
                    st.warning("Kolom 'Nama Pelanggan' atau 'No Reff.' tidak ditemukan.")
                    top_pelanggan = pd.DataFrame(columns=['No Reff.', 'Nama Pelanggan', 'Alamat', 'Kelurahan', 'Customer Management', 'total_tunggakan'])

                # Tampilkan beberapa metrik
                col_a, col_b, col_c = st.columns(3)
                with col_a:
                    st.metric("Total Baris", f"{total_rows:,}")
                with col_b:
                    st.metric("Range Bulan", f"{range_bulan}")
                with col_c:
                    st.metric("Total Tunggakan", f"Rp {total_tunggakan:,.0f}")

                col_e, col_f, col_g = st.columns(3)
                with col_e:
                    st.metric("Rata-rata Total Tunggakan", f"Rp {rata_rata_tunggakan:,.0f}")
                with col_f:
                    st.metric("Median Total Tunggakan", f"Rp {median_tunggakan:,.0f}")
                with col_g:
                    st.metric("Rata-rata Bulan Tunggakan", f"{rata_rata_bulan:.2f}")
                # Pelanggan Berdasarkan Tunggakan Terbesar
                from st_aggrid import AgGrid
                if not top_pelanggan.empty:
                    st.subheader("Pelanggan Berdasarkan Tunggakan Terbesar")
                    top_pelanggan = top_pelanggan.rename(columns={'total_tunggakan': 'Total Tunggakan'})
                    gb_pelanggan = GridOptionsBuilder.from_dataframe(top_pelanggan.reset_index(drop=True))
                    gb_pelanggan.configure_pagination(enabled=True, paginationPageSize=5)
                    gb_pelanggan.configure_default_column(resizable=True)
                    grid_options_pelanggan = gb_pelanggan.build()

                    AgGrid(
                        top_pelanggan.reset_index(drop=True),
                        gridOptions=grid_options_pelanggan,
                        height=300,
                        theme='streamlit',
                        enable_enterprise_modules=False,
                        update_mode=GridUpdateMode.SELECTION_CHANGED,
                        data_return_mode=DataReturnMode.FILTERED_AND_SORTED
                    )
                else:
                    st.info("Tidak ada data top pelanggan.")

                # Informasi Tunggakan per Kategori Pelanggan
                if 'Kategori Pelanggan' in df.columns and 'total_tunggakan' in df.columns:
                    pelanggan_per_kategori = df.groupby('Kategori Pelanggan').agg(
                        Jumlah_Pelanggan=('Nama Pelanggan', 'count'),
                        Total_Tunggakan=('total_tunggakan', 'sum')
                    ).reset_index()

                    pelanggan_per_kategori = pelanggan_per_kategori.sort_values(by='Total_Tunggakan', ascending=False)
                    pelanggan_per_kategori['Jumlah Pelanggan'] = pelanggan_per_kategori['Jumlah_Pelanggan'].apply(lambda x: f"{x:,}")
                    pelanggan_per_kategori['Total Tunggakan'] = pelanggan_per_kategori['Total_Tunggakan'].apply(lambda x: f"Rp {x:,.0f}")

                    st.subheader("Informasi Tunggakan per Kategori Pelanggan")
                    AgGrid(
                        pelanggan_per_kategori[['Kategori Pelanggan','Jumlah Pelanggan','Total Tunggakan']],
                        height=300,
                        fit_columns_on_grid_load=True,
                        theme='streamlit',
                        enable_enterprise_modules=False,
                        update_mode=GridUpdateMode.SELECTION_CHANGED,
                        data_return_mode=DataReturnMode.FILTERED_AND_SORTED
                    )
                else:
                    st.info("Data kurang lengkap untuk menampilkan kategori pelanggan.")

                # Informasi Tunggakan per Kelurahan
                if 'Kelurahan' in df.columns and 'total_tunggakan' in df.columns:
                    pelanggan_per_kelurahan = df.groupby('Kelurahan').agg(
                        Jumlah_Pelanggan=('Nama Pelanggan', 'count'),
                        Total_Tunggakan=('total_tunggakan', 'sum')
                    ).reset_index()
                    pelanggan_per_kelurahan = pelanggan_per_kelurahan.sort_values(by='Total_Tunggakan', ascending=False)
                    pelanggan_per_kelurahan['Jumlah Pelanggan'] = pelanggan_per_kelurahan['Jumlah_Pelanggan'].apply(lambda x: f"{x:,}")
                    pelanggan_per_kelurahan['Total Tunggakan'] = pelanggan_per_kelurahan['Total_Tunggakan'].apply(lambda x: f"Rp {x:,.0f}")

                    st.subheader("Informasi Tunggakan per Kelurahan")
                    AgGrid(
                        pelanggan_per_kelurahan[['Kelurahan','Jumlah Pelanggan','Total Tunggakan']],
                        height=300,
                        fit_columns_on_grid_load=True,
                        theme='streamlit',
                        enable_enterprise_modules=False,
                        update_mode=GridUpdateMode.SELECTION_CHANGED,
                        data_return_mode=DataReturnMode.FILTERED_AND_SORTED
                    )
                else:
                    st.info("Data kurang lengkap untuk menampilkan informasi per Kelurahan.")

                # Informasi Tunggakan per Customer Management
                if 'Customer Management' in df.columns and 'total_tunggakan' in df.columns:
                    pelanggan_per_cm = df.groupby('Customer Management').agg(
                        Jumlah_Pelanggan=('Nama Pelanggan', 'count'),
                        Total_Tunggakan=('total_tunggakan', 'sum')
                    ).reset_index()
                    pelanggan_per_cm = pelanggan_per_cm.sort_values(by='Total_Tunggakan', ascending=False)
                    pelanggan_per_cm['Jumlah Pelanggan'] = pelanggan_per_cm['Jumlah_Pelanggan'].apply(lambda x: f"{x:,}")
                    pelanggan_per_cm['Total Tunggakan'] = pelanggan_per_cm['Total_Tunggakan'].apply(lambda x: f"Rp {x:,.0f}")

                    st.subheader("Informasi Tunggakan per Customer Management")
                    AgGrid(
                        pelanggan_per_cm[['Customer Management','Jumlah Pelanggan','Total Tunggakan']],
                        height=300,
                        fit_columns_on_grid_load=True,
                        theme='streamlit',
                        enable_enterprise_modules=False,
                        update_mode=GridUpdateMode.SELECTION_CHANGED,
                        data_return_mode=DataReturnMode.FILTERED_AND_SORTED
                    )
                else:
                    st.info("Data kurang lengkap untuk menampilkan informasi Customer Management.")

                # ----- Visualisasi Tambahan -----
                st.markdown("### Overview Data")
                with st.expander("Berikut adalah beberapa visualisasi untuk mendapatkan gambaran terkait distribusi data"):
                    # 1. Histogram 'jumlah_bulan_tunggakan' dengan bins manual
                    if 'jumlah_bulan_tunggakan' in df.columns:
                        # Ambil nilai (drop NaN)
                        vals_bulan = df['jumlah_bulan_tunggakan'].dropna()

                        # Hitung histogram secara manual
                        freq, edges = np.histogram(vals_bulan, bins=10)  # bins=10 atau sesuai kebutuhan

                        # Kita akan simpan bin_label dan bin_freq yg > 0
                        bin_labels = []
                        bin_freqs = []

                        for i in range(len(freq)):
                            if freq[i] > 0:
                                left_edge = edges[i]
                                right_edge = edges[i+1]
                                # Contoh label bin: "0 - 4" atau "5 - 9" dsb.  
                                # Silakan kustom sesuai keinginan, misalnya integer.
                                bin_label = f"{int(left_edge)} - {int(right_edge)-1}"  # atau f"{left_edge:.0f} - {right_edge:.0f}"
                                bin_labels.append(bin_label)
                                bin_freqs.append(freq[i])

                        # Buat bar chart hanya dengan bin yg freq>0
                        if len(bin_freqs) > 0:
                            fig_hist_bulan = go.Figure(
                                data=[go.Bar(
                                    x=bin_labels,
                                    y=bin_freqs,
                                    text=bin_freqs,                # Menampilkan nilai spesifik di atas bar
                                    textposition='outside',
                                    marker_color='#4285F4',
                                    hovertemplate='Jumlah Bulan Tunggakan: %{x}<br>Frekuensi: %{y}',
                                )]
                            )
                            fig_hist_bulan.update_layout(
                                title="Jumlah Bulan Tunggakan",
                                xaxis_title="Range Jumlah Bulan Tunggakan",
                                yaxis_title="Frekuensi",
                                template="plotly_white"
                            )
                            # Pastikan label di luar bar tidak terpotong
                            fig_hist_bulan.update_traces(cliponaxis=False)
                            st.plotly_chart(fig_hist_bulan, use_container_width=True)
                        else:
                            st.info("Seluruh bin Jumlah Bulan Tunggakan memiliki frekuensi 0, tidak ada bar yang perlu ditampilkan.")
                    else:
                        st.info("Kolom 'jumlah_bulan_tunggakan' tidak tersedia untuk histogram.")

                    # 2. Histogram 'total_tunggakan' dengan bins manual
                    if 'total_tunggakan' in df.columns:
                        vals_tunggakan = df['total_tunggakan'].dropna()

                        # Definisikan sendiri jumlah bin, misal 20
                        freq2, edges2 = np.histogram(vals_tunggakan, bins=20)

                        bin_labels2 = []
                        bin_freqs2 = []

                        for i in range(len(freq2)):
                            if freq2[i] > 0:
                                left_edge2 = edges2[i]
                                right_edge2 = edges2[i+1]
                                # Label bin misalnya "100 - 999", dsb.
                                bin_label2 = f"{int(left_edge2)} - {int(right_edge2)}"
                                bin_labels2.append(bin_label2)
                                bin_freqs2.append(freq2[i])

                        if len(bin_freqs2) > 0:
                            fig_hist_tunggakan = go.Figure(
                                data=[go.Bar(
                                    x=bin_labels2,
                                    y=bin_freqs2,
                                    text=bin_freqs2,                
                                    textposition='outside',
                                    marker_color='#FF9900',
                                    hovertemplate='Total Tunggakan: %{x}<br>Frekuensi: %{y}',
                                )]
                            )
                            fig_hist_tunggakan.update_layout(
                                title="Total Tunggakan (Rp)",
                                xaxis_title="Range Total Tunggakan (Rp)",
                                yaxis_title="Frekuensi",
                                template="plotly_white"
                            )
                            fig_hist_tunggakan.update_traces(cliponaxis=False)
                            st.plotly_chart(fig_hist_tunggakan, use_container_width=True)
                        else:
                            st.info("Seluruh bin Total Tunggakan memiliki frekuensi 0, tidak ada bar yang perlu ditampilkan.")
                    else:
                        st.info("Kolom 'total_tunggakan' tidak tersedia untuk histogram.")
                     # -------------- Bar Chart Tunggakan per Kategori Pelanggan --------------
                    if 'Kategori Pelanggan' in st.session_state.df_processed.columns and 'total_tunggakan' in st.session_state.df_processed.columns:
                        dcat = st.session_state.df_processed.groupby('Kategori Pelanggan')['total_tunggakan'].sum().reset_index()
                        # Hanya ambil kategori dengan total_tunggakan > 0
                        dcat = dcat[dcat['total_tunggakan'] > 0]
                        if not dcat.empty:
                            dcat = dcat.sort_values(by='total_tunggakan', ascending=False)
                            
                            fig_bar_cat = go.Figure(
                                data=[go.Bar(
                                    x=dcat['Kategori Pelanggan'],
                                    y=dcat['total_tunggakan'],
                                    marker_color='#1f77b4',
                                    text=dcat['total_tunggakan'],           # Menampilkan nilai spesifik
                                    textposition='auto',                     # Menempatkan label otomatis
                                    hovertemplate="Kategori: %{x}<br>Total Tunggakan: %{y}"
                                )]
                            )
                            fig_bar_cat.update_layout(
                                title="Tunggakan per Kategori Pelanggan (Hanya > 0)",
                                xaxis_title="Kategori Pelanggan",
                                yaxis_title="Total Tunggakan (Rp)",
                                template="plotly_white"
                            )
                            st.plotly_chart(fig_bar_cat, use_container_width=True)
                        else:
                            st.info("Tidak ada Kategori Pelanggan dengan Total Tunggakan > 0.")

                    # -------------- Bar Chart Tunggakan per Kelurahan --------------
                    if 'Kelurahan' in st.session_state.df_processed.columns and 'total_tunggakan' in st.session_state.df_processed.columns:
                        dkel = st.session_state.df_processed.groupby('Kelurahan')['total_tunggakan'].sum().reset_index()
                        # Hanya kelurahan dengan total_tunggakan > 0
                        dkel = dkel[dkel['total_tunggakan'] > 0]
                        if not dkel.empty:
                            dkel = dkel.sort_values(by='total_tunggakan', ascending=False)
                            
                            fig_bar_kel = go.Figure(
                                data=[go.Bar(
                                    x=dkel['Kelurahan'],
                                    y=dkel['total_tunggakan'],
                                    marker_color='#E91E63',
                                    text=dkel['total_tunggakan'],
                                    textposition='auto',
                                    hovertemplate="Kelurahan: %{x}<br>Total Tunggakan: %{y}"
                                )]
                            )
                            fig_bar_kel.update_layout(
                                title="Tunggakan per Kelurahan (Hanya > 0)",
                                xaxis_title="Kelurahan",
                                yaxis_title="Total Tunggakan (Rp)",
                                template="plotly_white"
                            )
                            st.plotly_chart(fig_bar_kel, use_container_width=True)
                        else:
                            st.info("Tidak ada Kelurahan dengan Total Tunggakan > 0.")

                    # -------------- Bar Chart Tunggakan per Customer Management --------------
                    if 'Customer Management' in st.session_state.df_processed.columns and 'total_tunggakan' in st.session_state.df_processed.columns:
                        dcm = st.session_state.df_processed.groupby('Customer Management')['total_tunggakan'].sum().reset_index()
                        # Hanya Customer Management dengan total_tunggakan > 0
                        dcm = dcm[dcm['total_tunggakan'] > 0]
                        if not dcm.empty:
                            dcm = dcm.sort_values(by='total_tunggakan', ascending=False)

                            fig_bar_cm = go.Figure(
                                data=[go.Bar(
                                    x=dcm['Customer Management'],
                                    y=dcm['total_tunggakan'],
                                    marker_color='#00C853',
                                    text=dcm['total_tunggakan'],
                                    textposition='auto',
                                    hovertemplate="Customer Management: %{x}<br>Total Tunggakan: %{y}"
                                )]
                            )
                            fig_bar_cm.update_layout(
                                title="Tunggakan per Customer Management (Hanya > 0)",
                                xaxis_title="Customer Management",
                                yaxis_title="Total Tunggakan (Rp)",
                                template="plotly_white"
                            )
                            st.plotly_chart(fig_bar_cm, use_container_width=True)
                        else:
                            st.info("Tidak ada Customer Management dengan Total Tunggakan > 0.")

            except Exception as e:
                # Tampilkan pesan kesalahan umum. 
                st.error(f"Terjadi kesalahan saat memproses data: {str(e)}")
                st.session_state.data_loaded = False
        else:
            # Jika belum ada data
            show_upload_message()

     # ---- Tab 2: Bar Chart Durasi Tunggakan ----
    with tab2:
        # Pastikan 'data_loaded' dan 'df_processed' sudah diinisialisasi di session_state
        if not st.session_state.data_loaded:
            show_upload_message()  # Pesan jika data belum dimuat
        else:
            # Gunakan DataFrame hasil preprocessing
            df = st.session_state.df_processed

            st.title("Bar Chart Durasi Tunggakan")

            # ------------------------------------------------------------------
            # 1) Bagian FILTER
            # ------------------------------------------------------------------
            # st.markdown("""
            #     <div class="tooltip">
            #         ⚙️ Filter Data
            #         <span class="tooltiptext">Gunakan filter di bawah ini untuk menyesuaikan data yang ditampilkan pada bar chart.</span>
            #     </div>
            # """, unsafe_allow_html=True)
            st.markdown("### Filter Data")

            col1, col2, col3, col4, col5 = st.columns(5)

            with col1:
                # Pastikan kolom 'jumlah_bulan_tunggakan' bernilai numeric (int/float)
                # Kalau masih float, konversi ke int bila perlu:
                # df['jumlah_bulan_tunggakan'] = df['jumlah_bulan_tunggakan'].astype(int)
                min_month_val = int(df['jumlah_bulan_tunggakan'].min())
                max_month_val = int(df['jumlah_bulan_tunggakan'].max())
                month_range = st.slider(
                    'Range Bulan Tunggakan:',
                    min_value=min_month_val,
                    max_value=max_month_val,
                    value=(1, 5),  # default
                    label_visibility='visible'
                )

            with col2:
                if 'Kategori Pelanggan' in df.columns:
                    unique_kategori = df['Kategori Pelanggan'].dropna().unique()
                    selected_kategori = st.selectbox(
                        'Filter Kategori Pelanggan:',
                        ['Semua Kategori'] + list(unique_kategori),
                        label_visibility='visible'
                    )
                else:
                    selected_kategori = 'Semua Kategori'

            with col3:
                if 'Kelurahan' in df.columns:
                    unique_kel = df['Kelurahan'].dropna().unique()
                    selected_kelurahan = st.selectbox(
                        'Filter Kelurahan:',
                        ['Semua Kelurahan'] + list(unique_kel),
                        label_visibility='visible'
                    )
                else:
                    selected_kelurahan = 'Semua Kelurahan'

            with col4:
                if 'Customer Management' in df.columns:
                    unique_cm = df['Customer Management'].dropna().unique()
                    selected_cm = st.selectbox(
                        'Filter Customer Management:',
                        ['Semua Customer Management'] + list(unique_cm),
                        label_visibility='visible'
                    )
                else:
                    selected_cm = 'Semua Customer Management'

            with col5:
                if 'Status' in df.columns:
                    unique_status = df['Status'].dropna().unique()
                    selected_status = st.selectbox(
                        'Filter Status:',
                        ['Semua Status'] + list(unique_status),
                        label_visibility='visible'
                    )
                else:
                    selected_status = 'Semua Status'

            # ------------------------------------------------------------------
            # 2) Aplikasi FILTER ke DataFrame
            # ------------------------------------------------------------------
            filtered_df = df.copy()

            # Filter Kategori
            if selected_kategori != 'Semua Kategori' and 'Kategori Pelanggan' in filtered_df.columns:
                filtered_df = filtered_df[filtered_df['Kategori Pelanggan'] == selected_kategori]

            # Filter Kelurahan
            if selected_kelurahan != 'Semua Kelurahan' and 'Kelurahan' in filtered_df.columns:
                filtered_df = filtered_df[filtered_df['Kelurahan'] == selected_kelurahan]

            # Filter Customer Management
            if selected_cm != 'Semua Customer Management' and 'Customer Management' in filtered_df.columns:
                filtered_df = filtered_df[filtered_df['Customer Management'] == selected_cm]

            # Filter Status
            if selected_status != 'Semua Status' and 'Status' in filtered_df.columns:
                filtered_df = filtered_df[filtered_df['Status'] == selected_status]

            # Filter range bulan tunggakan
            filtered_df = filtered_df[
                (filtered_df['jumlah_bulan_tunggakan'] >= month_range[0]) &
                (filtered_df['jumlah_bulan_tunggakan'] <= month_range[1])
            ]

            # ------------------------------------------------------------------
            # 3) Visualisasi Stacked Bar
            # ------------------------------------------------------------------
            col_vis1, col_vis2 = st.columns([7, 3])

            with col_vis1:
                if selected_kategori == 'Semua Kategori':
                    # Stacked bar chart untuk semua kategori
                    df_kategori = (
                        filtered_df
                        .groupby(['jumlah_bulan_tunggakan', 'Kategori Pelanggan'])
                        .size()
                        .reset_index(name='jumlah_pelanggan')
                    )

                    if not df_kategori.empty:
                        fig = go.Figure()

                        colors = pc.qualitative.Plotly  # palet warna
                        unique_kats = df_kategori['Kategori Pelanggan'].unique()

                        for i, kategori in enumerate(unique_kats):
                            kategori_data = df_kategori[df_kategori['Kategori Pelanggan'] == kategori]
                            warna_kategori = colors[i % len(colors)]

                            fig.add_trace(go.Bar(
                                x=kategori_data['jumlah_bulan_tunggakan'],
                                y=kategori_data['jumlah_pelanggan'],
                                name=kategori,  # Menampilkan kategori yang sesuai di legend
                                hovertemplate=(
                                    '<b>Jumlah Bulan Tunggakan:</b> %{x}<br>'
                                    + '<b>Jumlah Pelanggan (' + kategori + '):</b> %{y}<br>'  # Memasukkan kategori ke dalam hover
                                ),
                                textposition='inside',
                                marker_color=warna_kategori
                            ))

                        # Tambahkan total di atas bar
                        total_per_bulan = (
                            df_kategori
                            .groupby('jumlah_bulan_tunggakan')['jumlah_pelanggan']
                            .sum()
                            .reset_index()
                        )
                        fig.add_trace(go.Scatter(
                            x=total_per_bulan['jumlah_bulan_tunggakan'],
                            y=total_per_bulan['jumlah_pelanggan'],
                            mode='text',
                            text=total_per_bulan['jumlah_pelanggan'].apply(lambda x: f"{x:,}"),
                            textposition='top center',
                            showlegend=False,
                            textfont=dict(size=12, color='black')
                        ))

                        fig.update_layout(
                            title='Distribusi Tunggakan Pelanggan Seluruh Kategori',
                            barmode='stack',
                            xaxis_title='Jumlah Bulan Tunggakan',
                            yaxis_title='Jumlah Pelanggan',
                            template='plotly_white',
                            height=700,
                            hovermode='closest',
                            xaxis=dict(showgrid=True),
                            yaxis=dict(showgrid=True),
                            dragmode='zoom',  # Enables zoom on the chart
                            margin=dict(l=40, r=40, t=40, b=40)
                        )
                        st.plotly_chart(fig, use_container_width=True)

                        import plotly.express as px

                        # Membuat heatmap berdasarkan bulan tunggakan dan kategori pelanggan
                        heatmap_data = filtered_df.groupby(['jumlah_bulan_tunggakan', 'Kategori Pelanggan']).size().reset_index(name='Jumlah Pelanggan')

                        # Membuat heatmap interaktif
                        fig_heatmap = px.density_heatmap(heatmap_data, 
                                                        x='jumlah_bulan_tunggakan', 
                                                        y='Kategori Pelanggan', 
                                                        z='Jumlah Pelanggan', 
                                                        color_continuous_scale='Viridis')

                        fig_heatmap.update_layout(
                            title='Heatmap Jumlah Pelanggan Berdasarkan Bulan dan Kategori Pelanggan',
                            xaxis_title='Jumlah Bulan Tunggakan',
                            yaxis_title='Kategori Pelanggan',
                            template='plotly_white',
                            height=500
                        )

                        st.plotly_chart(fig_heatmap, use_container_width=True)


                    else:
                        st.warning("Tidak ada data untuk ditampilkan pada stacked bar chart berdasarkan filter yang dipilih.")
                else:
                    # Jika kategori spesifik dipilih
                    df_kategori = (
                        filtered_df
                        .groupby(['jumlah_bulan_tunggakan', 'Kategori Pelanggan'])
                        .size()
                        .reset_index(name='jumlah_pelanggan')
                    )

                    if not df_kategori.empty:
                        fig = go.Figure()

                        # Data khusus kategori terpilih
                        selected_kategori_data = df_kategori[df_kategori['Kategori Pelanggan'] == selected_kategori]

                        fig.add_trace(go.Bar(
                            x=selected_kategori_data['jumlah_bulan_tunggakan'],
                            y=selected_kategori_data['jumlah_pelanggan'],
                            name=selected_kategori,
                            hovertemplate=(
                                '<b>Jumlah Bulan Tunggakan:</b> %{x}<br>'
                                + '<b>Jumlah Pelanggan:</b> %{y}<br>'  # Menambahkan kategori secara dinamis
                            ),
                            text=selected_kategori_data['jumlah_pelanggan'],
                            textposition='inside',
                            marker_color='rgb(15, 118, 228)'
                        ))

                        fig.update_layout(
                            title=f'Distribusi Tunggakan Pelanggan ({selected_kategori})',
                            barmode='stack',
                            xaxis_title='Jumlah Bulan Tunggakan',
                            yaxis_title='Jumlah Pelanggan',
                            template='plotly_white',
                            height=500,
                            hovermode='closest'
                        )
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.warning(f"Tidak ada data untuk kategori {selected_kategori} pada filter ini.")

            # ------------------------------------------------------------------
            # 4) Bagian Statistik Singkat
            # ------------------------------------------------------------------
            with col_vis2:
                st.subheader("Statistik Tunggakan")

                total_pelanggan = len(filtered_df)
                if 'total_tunggakan' in filtered_df.columns:
                    total_tunggakan = filtered_df['total_tunggakan'].sum()
                    tunggakan_min = filtered_df['total_tunggakan'].min()
                    tunggakan_max = filtered_df['total_tunggakan'].max()
                    rata_rata_tunggakan = filtered_df['total_tunggakan'].mean()
                else:
                    total_tunggakan = 0
                    tunggakan_min = 0
                    tunggakan_max = 0
                    rata_rata_tunggakan = 0

                # Agregasi jumlah bulan
                agregasi_bulan = (
                    filtered_df
                    .groupby('jumlah_bulan_tunggakan')
                    .size()
                    .reset_index(name='jumlah_pelanggan')
                )

                if not agregasi_bulan.empty:
                    # Bulan tunggakan dengan jumlah pelanggan terbanyak
                    idxmax_ = agregasi_bulan['jumlah_pelanggan'].idxmax()
                    bulan_tunggakan_terbanyak = agregasi_bulan.loc[idxmax_, 'jumlah_bulan_tunggakan']
                else:
                    bulan_tunggakan_terbanyak = 0

                st.metric("Total Pelanggan", f"{total_pelanggan:,}")
                st.metric("Total Tunggakan", f"Rp {total_tunggakan:,.0f}")
                st.metric("Tunggakan Minimum", f"Rp {tunggakan_min:,.0f}")
                st.metric("Tunggakan Maksimum", f"Rp {tunggakan_max:,.0f}")
                st.metric("Rata-Rata Tunggakan", f"Rp {rata_rata_tunggakan:,.0f}")
                st.metric("Bulan Tunggakan Terbanyak", f"{bulan_tunggakan_terbanyak} bulan")

            # ------------------------------------------------------------------
            # 5) Tabel Ringkasan Tunggakan
            # ------------------------------------------------------------------
            agregasi_bulan = (
                filtered_df
                .groupby('jumlah_bulan_tunggakan')
                .size()
                .reset_index(name='jumlah_pelanggan')
            )

            if not agregasi_bulan.empty:
                st.subheader("Tabel Ringkasan Tunggakan")
                agregasi_bulan['Total Tunggakan'] = agregasi_bulan['jumlah_bulan_tunggakan'].apply(
                    lambda x: filtered_df.loc[filtered_df['jumlah_bulan_tunggakan'] == x, 'total_tunggakan'].sum()
                )
                agregasi_bulan['Persentase Perubahan'] = agregasi_bulan['Total Tunggakan'].pct_change() * 100
                agregasi_bulan['Total Tunggakan Display'] = agregasi_bulan['Total Tunggakan'].apply(lambda x: f"Rp {x:,.0f}")
                agregasi_bulan['Persentase Perubahan Display'] = agregasi_bulan['Persentase Perubahan'].apply(
                    lambda x: f"{x:.2f}%" if pd.notnull(x) else '-'
                )
                
                agregasi_bulan_display = agregasi_bulan[[
                    'jumlah_bulan_tunggakan',
                    'jumlah_pelanggan',
                    'Total Tunggakan Display',
                    'Persentase Perubahan Display'
                ]]

                # buat AgGrid
                grid_options = GridOptionsBuilder.from_dataframe(agregasi_bulan_display)
                grid_options.configure_pagination(paginationPageSize=10)
                grid_options.configure_column('jumlah_bulan_tunggakan', headerName='Jumlah Bulan Tunggakan', editable=False)
                grid_options.configure_column('jumlah_pelanggan', headerName='Jumlah Pelanggan', editable=False)
                grid_options.configure_column('Total Tunggakan Display', headerName='Total Tunggakan', editable=False)
                grid_options.configure_column('Persentase Perubahan Display', headerName='Persentase Perubahan', editable=False)
                grid_options.configure_selection('single')

                grid_response = AgGrid(
                    agregasi_bulan_display,
                    gridOptions=grid_options.build(),
                    height=350,
                    fit_columns_on_grid_load=True,
                    update_mode=GridUpdateMode.SELECTION_CHANGED,
                    data_return_mode=DataReturnMode.FILTERED
                )
            else:
                st.warning("Tidak ada data untuk ditampilkan pada tabel ringkasan tunggakan.")

            # ------------------------------------------------------------------
            # 6) Filter Jumlah Bulan Tunggakan untuk Tabel Detail Pelanggan
            # ------------------------------------------------------------------
            st.subheader("Detail Pelanggan berdasarkan Jumlah Bulan Tunggakan")

            # Ambil jumlah bulan tunggakan yang unik dari data yang sudah difilter
            unique_bulan_tunggakan = sorted(filtered_df['jumlah_bulan_tunggakan'].dropna().unique())


            col1, col2, col3, col4, col5 = st.columns(5)

            with col1:
                selected_bulan_tunggakan = st.selectbox(
                'Jumlah Bulan Tagihan:',
                ['Semua Bulan'] + [str(bulan) for bulan in unique_bulan_tunggakan],
                label_visibility='visible')

            if selected_bulan_tunggakan != 'Semua Bulan':
                # Filter berdasarkan jumlah bulan tunggakan yang dipilih
                filtered_detail_df = filtered_df[filtered_df['jumlah_bulan_tunggakan'] == int(selected_bulan_tunggakan)]
            else:
                # Jika "Semua Bulan" dipilih, tampilkan semua data
                filtered_detail_df = filtered_df

            # Pastikan ada data yang ditampilkan
            if not filtered_detail_df.empty:
                # Pilih kolom yang ingin ditampilkan dalam tabel detail pelanggan
                detail_pelanggan_df = filtered_detail_df[[
                    'No Reff.', 'Nama Pelanggan', 'No HP', 'Alamat', 'Customer Management', 
                    'Kelurahan', 'Kategori Pelanggan', 'jumlah_bulan_tunggakan', 
                    'total_tunggakan', 'detail_tunggakan'
                ]]

                # Format kolom 'total_tunggakan' agar lebih mudah dibaca
                detail_pelanggan_df['total_tunggakan'] = detail_pelanggan_df['total_tunggakan'].apply(
                    lambda x: f"Rp {x:,.0f}"
                )

                # Buat AgGrid untuk menampilkan data pelanggan
                grid_options_detail = GridOptionsBuilder.from_dataframe(detail_pelanggan_df)
                grid_options_detail.configure_pagination(paginationPageSize=10)
                grid_options_detail.configure_column('No Reff.', editable=False)
                grid_options_detail.configure_column('Nama Pelanggan', editable=False)
                grid_options_detail.configure_column('No HP', editable=False)
                grid_options_detail.configure_column('Alamat', editable=False)
                grid_options_detail.configure_column('Customer Management', editable=False)
                grid_options_detail.configure_column('Kelurahan', editable=False)
                grid_options_detail.configure_column('Kategori Pelanggan', editable=False)
                grid_options_detail.configure_column('jumlah_bulan_tunggakan', editable=False)
                grid_options_detail.configure_column('total_tunggakan', editable=False)
                grid_options_detail.configure_column('detail_tunggakan', editable=False)

                AgGrid(
                    detail_pelanggan_df,
                    gridOptions=grid_options_detail.build(),
                    height=350,
                    fit_columns_on_grid_load=True,
                    update_mode=GridUpdateMode.SELECTION_CHANGED,
                    data_return_mode=DataReturnMode.FILTERED
                )
            else:
                st.warning("Tidak ada data untuk ditampilkan pada tabel detail pelanggan berdasarkan filter yang dipilih.")

            
            # ------------------------------------------------------------------
            # 7) Tabel "Tunggakan Terbesar Berdasarkan Kelurahan - Customer Management"
            # ------------------------------------------------------------------
            st.subheader("Tunggakan Terbesar Berdasarkan Kelurahan - Customer Management")

            if not filtered_df.empty:
                kelurahan_cm_summary = (
                    filtered_df
                    .groupby(['Kelurahan', 'Customer Management'])
                    .agg(
                        jumlah_pelanggan=('Nama Pelanggan', 'count'),
                        total_tunggakan=('total_tunggakan', 'sum')
                    )
                    .reset_index()
                )

                # Urutkan descending by total_tunggakan
                kelurahan_cm_summary = kelurahan_cm_summary.sort_values(by='total_tunggakan', ascending=False)

                # Format tampilan total_tunggakan
                kelurahan_cm_summary['total_tunggakan'] = kelurahan_cm_summary['total_tunggakan'].apply(
                    lambda x: f"Rp {x:,.0f}".replace(",", ".")
                )

                grid_options_kelurahan_cm = GridOptionsBuilder.from_dataframe(kelurahan_cm_summary)
                grid_options_kelurahan_cm.configure_pagination(paginationPageSize=10)
                grid_options_kelurahan_cm.configure_column('Kelurahan', editable=False)
                grid_options_kelurahan_cm.configure_column('Customer Management', editable=False)
                grid_options_kelurahan_cm.configure_column('jumlah_pelanggan', editable=False)
                grid_options_kelurahan_cm.configure_column('total_tunggakan', editable=False)

                AgGrid(
                    kelurahan_cm_summary,
                    gridOptions=grid_options_kelurahan_cm.build(),
                    height=350,
                    fit_columns_on_grid_load=True,
                    update_mode=GridUpdateMode.SELECTION_CHANGED,
                    data_return_mode=DataReturnMode.FILTERED
                )
            else:
                st.warning("Tidak ada data untuk ditampilkan pada tabel Tunggakan Terbesar Berdasarkan Kelurahan - Customer Management.")

    # ---- Tab 3: Line Chart Total Tunggakan ----
    with tab3:
        if not st.session_state.data_loaded:
            show_upload_message()
        else:
            # Ambil DataFrame hasil preprocessing
            df = st.session_state.df_processed

            st.title("Line Chart Total Tunggakan")

            # 1. Identifikasi kolom bulan-tahun
            month_year_cols = [col for col in df.columns if '-' in col]

            # 2. Urutkan kolom bulan-tahun (format '%b-%Y')
            try:
                month_year_cols_sorted = sorted(
                    month_year_cols, 
                    key=lambda x: datetime.strptime(x, '%b-%Y')
                )
            except Exception as e:
                st.error(f"Error saat mengurutkan kolom bulan-tahun: {e}")
                st.stop()

            # 3. Pastikan kolom 'detail_tunggakan' sudah bisa diakses sebagai dict
            try:
                df['detail_tunggakan'] = df['detail_tunggakan'].apply(
                    lambda x: ast.literal_eval(x) if isinstance(x, str) else x
                )
            except Exception as e:
                st.error(f"Error saat mempersiapkan data: {e}")

            # Baris 1: Filter bulan-tahun
            st.markdown("### Filter Data")
            col_filter1, col_filter2 = st.columns(2)
            with col_filter1:
                start_month = st.selectbox(
                    'Bulan Awal',
                    options=month_year_cols_sorted,
                    index=0
                )
            with col_filter2:
                end_month = st.selectbox(
                    'Bulan Akhir',
                    options=month_year_cols_sorted,
                    index=len(month_year_cols_sorted) - 1
                )

            # Validasi rentang bulan
            try:
                start_idx = month_year_cols_sorted.index(start_month)
                end_idx = month_year_cols_sorted.index(end_month)
                if start_idx > end_idx:
                    st.error("Bulan Awal harus sebelum atau sama dengan Bulan Akhir.")
                    st.stop()
            except ValueError as e:
                st.error(f"Bulan Awal atau Bulan Akhir tidak valid: {e}")
                st.stop()

            selected_months = month_year_cols_sorted[start_idx:end_idx + 1]
            if not selected_months:
                st.warning("Tidak ada kolom bulan-tahun yang terpilih.")
                st.stop()

            # Baris 2: Filter tambahan
            col_filter3, col_filter4, col_filter5, col_filter6 = st.columns(4)
            with col_filter3:
                if 'Kategori Pelanggan' in df.columns:
                    unique_categories = sorted(df['Kategori Pelanggan'].dropna().unique())
                    selected_category = st.selectbox(
                        'Kategori Pelanggan',
                        options=['Semua Kategori'] + list(unique_categories),
                        index=0  # Default ke "Semua Kategori"
                    )
                else:
                    selected_category = 'Semua Kategori'
            with col_filter4:
                if 'Kelurahan' in df.columns:
                    unique_kel = sorted(df['Kelurahan'].dropna().unique())
                    selected_kelurahan = st.selectbox(
                        'Kelurahan',
                        options=['Semua Kelurahan'] + list(unique_kel)
                    )
                else:
                    selected_kelurahan = 'Semua Kelurahan'
            with col_filter5:
                if 'Customer Management' in df.columns:
                    unique_cm = sorted(df['Customer Management'].dropna().unique())
                    selected_cm = st.selectbox(
                        'Customer Management',
                        options=['Semua Customer Management'] + list(unique_cm)
                    )
                else:
                    selected_cm = 'Semua Customer Management'
            with col_filter6:
                if 'Status' in df.columns:
                    unique_status = sorted(df['Status'].dropna().unique())
                    selected_status = st.selectbox(
                        'Status',
                        options=['Semua Status'] + list(unique_status),
                        index=0  # Default ke "Semua Status"
                    )
                else:
                    selected_status = 'Semua Status'

            # Filter DataFrame berdasarkan filter tambahan
            def apply_filters(df, selected_months, selected_category, selected_kelurahan, selected_cm, selected_status):
                filtered_df = df.copy()
                if selected_kelurahan != 'Semua Kelurahan' and 'Kelurahan' in filtered_df.columns:
                    filtered_df = filtered_df[filtered_df['Kelurahan'] == selected_kelurahan]
                if selected_cm != 'Semua Customer Management' and 'Customer Management' in filtered_df.columns:
                    filtered_df = filtered_df[filtered_df['Customer Management'] == selected_cm]
                if selected_category != 'Semua Kategori' and 'Kategori Pelanggan' in filtered_df.columns:
                    filtered_df = filtered_df[filtered_df['Kategori Pelanggan'] == selected_category]
                if selected_status != 'Semua Status' and 'Status' in filtered_df.columns:
                    filtered_df = filtered_df[filtered_df['Status'] == selected_status]
                # Buat kolom 'total_tunggakan_selected' = penjumlahan tunggakan di bulan-bulan terpilih
                filtered_df['total_tunggakan_selected'] = filtered_df[selected_months].sum(axis=1)
                return filtered_df

            filtered_df = apply_filters(df, selected_months, selected_category, selected_kelurahan, selected_cm, selected_status)

            # Hitung total tunggakan per bulan
            monthly_totals = filtered_df[selected_months].sum().reset_index()
            monthly_totals.columns = ['bulan_tahun', 'total_tunggakan']

            # Tambahkan kolom datetime untuk urutan waktu
            monthly_totals['bulan_datetime'] = monthly_totals['bulan_tahun'].apply(
                lambda x: datetime.strptime(x, '%b-%Y')
            )
            monthly_totals = monthly_totals.sort_values('bulan_datetime')
            
            # 8. Buat line chart (tanpa plotly_events, hanya st.plotly_chart)
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=monthly_totals['bulan_tahun'],
                y=monthly_totals['total_tunggakan'],
                mode='lines+markers',
                marker=dict(size=8, color='#1E90FF'),
                line=dict(color='#1E90FF'),
                hovertemplate=(
                    '<b>Bulan-Tahun:</b> %{x}<br>'
                    '<b>Total Tunggakan:</b> Rp %{y:,.0f}<br>'
                )
            ))
            fig.update_layout(
                title='Total Tunggakan per Bulan',
                xaxis_title='Bulan-Tahun',
                yaxis_title='Total Tunggakan (Rp)',
                template='plotly_white',
                height=500,
                hovermode='closest'
            )

            # Render hanya dengan st.plotly_chart (tidak ada event click)
            st.plotly_chart(fig, use_container_width=True)

            # 9. Visualisasi berdasarkan filter 'semua'
            if selected_category == 'Semua Kategori' or selected_kelurahan == 'Semua Kelurahan' or selected_cm == 'Semua Customer Management' or selected_status == 'Semua Status':
                with st.expander("Berikut adalah beberapa visualisasi untuk mendapatkan gambaran terkait distribusi total tunggakan"):
                    # Visualisasi berdasarkan Kategori (Satu grafik untuk semua kategori)
                    if selected_category == 'Semua Kategori':
                        fig_category = go.Figure()
                        for category in unique_categories:
                            category_data = filtered_df[filtered_df['Kategori Pelanggan'] == category]
                            monthly_totals_category = category_data[selected_months].sum().reset_index()
                            monthly_totals_category.columns = ['bulan_tahun', 'total_tunggakan']

                            fig_category.add_trace(go.Scatter(
                                x=monthly_totals_category['bulan_tahun'],
                                y=monthly_totals_category['total_tunggakan'],
                                mode='lines+markers',
                                name=category,
                                marker=dict(size=8),
                                line=dict(width=2),
                                hovertemplate=(
                                    '<b>Bulan-Tahun:</b> %{x}<br>'
                                    '<b>Total Tunggakan:</b> Rp %{y:,.0f}<br>'
                                )
                            ))

                        fig_category.update_layout(
                            title=f'Total Tunggakan per Bulan berdasarkan Kategori Pelanggan',
                            xaxis_title='Bulan-Tahun',
                            yaxis_title='Total Tunggakan (Rp)',
                            template='plotly_white',
                            height=500,
                            hovermode='closest'
                        )

                        st.plotly_chart(fig_category, use_container_width=True)

                    # Visualisasi berdasarkan Customer Management (Satu grafik untuk semua Customer Management)
                    if selected_cm == 'Semua Customer Management':
                        fig_cm = go.Figure()
                        for cm in unique_cm:
                            cm_data = filtered_df[filtered_df['Customer Management'] == cm]
                            monthly_totals_cm = cm_data[selected_months].sum().reset_index()
                            monthly_totals_cm.columns = ['bulan_tahun', 'total_tunggakan']

                            fig_cm.add_trace(go.Scatter(
                                x=monthly_totals_cm['bulan_tahun'],
                                y=monthly_totals_cm['total_tunggakan'],
                                mode='lines+markers',
                                name=cm,
                                marker=dict(size=8),
                                line=dict(width=2),
                                hovertemplate=(
                                    '<b>Bulan-Tahun:</b> %{x}<br>'
                                    '<b>Total Tunggakan:</b> Rp %{y:,.0f}<br>'
                                )
                            ))

                        fig_cm.update_layout(
                            title=f'Total Tunggakan per Bulan berdasarkan Customer Management',
                            xaxis_title='Bulan-Tahun',
                            yaxis_title='Total Tunggakan (Rp)',
                            template='plotly_white',
                            height=500,
                            hovermode='closest'
                        )

                        st.plotly_chart(fig_cm, use_container_width=True)

                    # Visualisasi berdasarkan Kelurahan (Satu grafik untuk semua Kelurahan)
                    if selected_kelurahan == 'Semua Kelurahan':
                        fig_kelurahan = go.Figure()
                        for kelurahan in sorted(filtered_df['Kelurahan'].dropna().unique()):
                            kelurahan_data = filtered_df[filtered_df['Kelurahan'] == kelurahan]
                            monthly_totals_kelurahan = kelurahan_data[selected_months].sum().reset_index()
                            monthly_totals_kelurahan.columns = ['bulan_tahun', 'total_tunggakan']

                            fig_kelurahan.add_trace(go.Scatter(
                                x=monthly_totals_kelurahan['bulan_tahun'],
                                y=monthly_totals_kelurahan['total_tunggakan'],
                                mode='lines+markers',
                                name=kelurahan,
                                marker=dict(size=8),
                                line=dict(width=2),
                                hovertemplate=(
                                    '<b>Bulan-Tahun:</b> %{x}<br>'
                                    '<b>Total Tunggakan:</b> Rp %{y:,.0f}<br>'
                                )
                            ))

                        fig_kelurahan.update_layout(
                            title=f'Total Tunggakan per Bulan berdasarkan Kelurahan',
                            xaxis_title='Bulan-Tahun',
                            yaxis_title='Total Tunggakan (Rp)',
                            template='plotly_white',
                            height=500,
                            hovermode='closest'
                        )

                        st.plotly_chart(fig_kelurahan, use_container_width=True)

                    # Visualisasi berdasarkan Status (Satu grafik untuk semua Status)
                    if selected_status == 'Semua Status':
                        fig_status = go.Figure()
                        for status in sorted(filtered_df['Status'].dropna().unique()):
                            status_data = filtered_df[filtered_df['Status'] == status]
                            monthly_totals_status = status_data[selected_months].sum().reset_index()
                            monthly_totals_status.columns = ['bulan_tahun', 'total_tunggakan']

                            fig_status.add_trace(go.Scatter(
                                x=monthly_totals_status['bulan_tahun'],
                                y=monthly_totals_status['total_tunggakan'],
                                mode='lines+markers',
                                name=status,
                                marker=dict(size=8),
                                line=dict(width=2),
                                hovertemplate=(
                                    '<b>Bulan-Tahun:</b> %{x}<br>'
                                    '<b>Total Tunggakan:</b> Rp %{y:,.0f}<br>'
                                )
                            ))

                        fig_status.update_layout(
                            title=f'Total Tunggakan per Bulan berdasarkan Status',
                            xaxis_title='Bulan-Tahun',
                            yaxis_title='Total Tunggakan (Rp)',
                            template='plotly_white',
                            height=500,
                            hovermode='closest'
                        )

                        st.plotly_chart(fig_status, use_container_width=True)

            # 10. Panel Statistik
            st.subheader("Statistik Tunggakan")
            col_stat1, col_stat2 = st.columns(2)
            with col_stat1:
                if selected_months:
                    st.metric("Rentang Bulan", f"{selected_months[0]}|{selected_months[-1]}")

                # # Total Pelanggan (Unique)
                # if 'Nama Pelanggan' in filtered_df.columns:
                #     st.metric("Total Pelanggan (Unique)", f"{filtered_df['Nama Pelanggan'].nunique():,}")
                # else:
                #     st.metric("Total Pelanggan (Unique)", f"{len(filtered_df):,}")

                # Total Tunggakan (Rentang Filter)
                st.metric(
                    "Total Tunggakan",
                    f"Rp {filtered_df['total_tunggakan_selected'].sum():,.0f}"
                )

                # Rata-rata Tunggakan per Pelanggan
                st.metric(
                    "Rata-rata Tunggakan per Pelanggan",
                    f"Rp {filtered_df['total_tunggakan'].mean():,.0f}"
                )

                # Rata-rata Tunggakan Per Bulan
                total_bulan_tunggakan = filtered_df['jumlah_bulan_tunggakan'].sum()
                start_date = datetime.strptime(start_month, '%b-%Y')
                end_date = datetime.strptime(end_month, '%b-%Y')
                jumlah_bulan = (end_date.year - start_date.year) * 12 + end_date.month - start_date.month 
                if total_bulan_tunggakan > 0:
                    rata_rata_bulan_tunggakan = filtered_df['total_tunggakan_selected'].sum() / jumlah_bulan
                    st.metric(
                        "Rata-rata Tunggakan Per Bulan",
                        f"Rp {rata_rata_bulan_tunggakan:,.0f}"
                    )
                else:
                    st.metric("Rata-rata Tunggakan Per Bulan", "-")

            with col_stat2:
                if 'Nama Pelanggan' in filtered_df.columns:
                    st.metric("Total Pelanggan (Unique)", f"{filtered_df['Nama Pelanggan'].nunique():,}")
                else:
                    st.metric("Total Pelanggan (Unique)", f"{len(filtered_df):,}")

                if not monthly_totals.empty:
                    try:
                        max_row = monthly_totals.loc[monthly_totals['total_tunggakan'].idxmax()]
                        min_row = monthly_totals.loc[monthly_totals['total_tunggakan'].idxmin()]

                        st.metric(
                            "Tunggakan Tertinggi Bulanan",
                            f"{max_row['bulan_tahun']} - Rp {max_row['total_tunggakan']:,.0f}"
                        )

                        st.metric(
                            "Tunggakan Terendah Bulanan",
                            f"{min_row['bulan_tahun']} - Rp {min_row['total_tunggakan']:,.0f}"
                        )

                    except Exception as e:
                        st.error(f"Error saat menentukan tertinggi/terendah: {e}")

                else:
                    st.metric("Tunggakan Tertinggi Bulanan", "-")
                    st.metric("Tunggakan Terendah Bulanan", "-")

                if not monthly_totals.empty:
                    monthly_totals['growth_rate'] = (
                        monthly_totals['total_tunggakan'].pct_change().fillna(0) * 100
                    )
                    avg_growth = monthly_totals['growth_rate'].mean()
                    st.metric(
                        "Rata-rata Pertumbuhan Tunggakan Bulanan",
                        f"{avg_growth:.2f}%"
                    )
                else:
                    st.metric("Rata-rata Pertumbuhan Tunggakan Bulanan", "-")


            # 10. Tabel Ringkasan Tunggakan per Bulan
            st.subheader("Tabel Ringkasan Tunggakan")
            if not monthly_totals.empty:
                summary_data = monthly_totals.copy()
                
                # Menambahkan kolom persentase perubahan
                summary_data['Persentase Perubahan'] = summary_data['total_tunggakan'].pct_change() * 100
                summary_data['Persentase Perubahan Display'] = summary_data['Persentase Perubahan'].apply(
                    lambda x: f"{x:.2f}%" if pd.notnull(x) else "-"
                )
                
                # Format angka
                summary_data['Total Tunggakan'] = summary_data['total_tunggakan'].apply(
                    lambda x: f"Rp {x:,.0f}"
                )
                summary_data.rename(columns={'bulan_tahun': 'Bulan-Tahun'}, inplace=True)

                # Mengatur AgGrid
                gb = GridOptionsBuilder.from_dataframe(
                    summary_data[['Bulan-Tahun', 'Total Tunggakan', 'Persentase Perubahan Display']]
                )
                gb.configure_pagination(paginationAutoPageSize=False, paginationPageSize=10)
                gb.configure_selection(selection_mode='single', use_checkbox=False)
                gb.configure_side_bar()
                grid_options = gb.build()

                # Menampilkan AgGrid
                AgGrid(
                    summary_data[['Bulan-Tahun', 'Total Tunggakan', 'Persentase Perubahan Display']],
                    gridOptions=grid_options,
                    height=300,
                    fit_columns_on_grid_load=True,
                    theme='streamlit',
                    enable_enterprise_modules=False,
                    update_mode=GridUpdateMode.SELECTION_CHANGED,
                    data_return_mode=DataReturnMode.FILTERED_AND_SORTED
                )
            else:
                st.info("Tidak ada data ringkasan untuk ditampilkan.")

            # 12. Tabel Detail Pelanggan per Bulan
            st.subheader("Tabel Detail Pelanggan per Bulan")

            col1, col2, col3, col4, col5 = st.columns(5)

            with col1:
                # Pilih bulan untuk detail pelanggan
                selected_detail_month = st.selectbox(
                    'Pilih Bulan-Tahun',
                    options=['Semua Bulan'] + list(selected_months),
                    index=0
                )

            # Fungsi untuk memproses data detail pelanggan
            def get_detailed_customers(df, selected_detail_month, selected_months):
                # Jika 'Semua Bulan' dipilih, gunakan semua bulan yang dipilih sebelumnya
                if selected_detail_month == 'Semua Bulan':
                    month_columns = selected_months
                else:
                    month_columns = [selected_detail_month]
                
                # Buat salinan DataFrame yang difilter
                detailed_df = filtered_df.copy()
                
                # Hitung total tunggakan per pelanggan untuk bulan yang dipilih
                detailed_df['total_tunggakan_detail'] = detailed_df[month_columns].sum(axis=1)
                
                # Filter hanya pelanggan dengan tunggakan
                detailed_df = detailed_df[detailed_df['total_tunggakan_detail'] > 0]
                
                # Persiapkan kolom yang akan ditampilkan
                columns_to_show = [
                    'No Reff.', 'Nama Pelanggan', 'No HP', 'Alamat', 'Kelurahan', 
                    'Customer Management', 'Kategori Pelanggan', 
                    'total_tunggakan_detail'
                ]
                
                # Hitung jumlah bulan tunggakan
                def count_tunggakan_months(row, month_columns):
                    return sum(1 for col in month_columns if row[col] > 0)
                
                detailed_df['Jumlah Bulan Tunggakan'] = detailed_df.apply(
                    lambda row: count_tunggakan_months(row, month_columns), 
                    axis=1
                )
                
                # Persiapkan data untuk ditampilkan
                display_df = detailed_df[columns_to_show + ['Jumlah Bulan Tunggakan']]
                
                # Rename kolom
                display_df = display_df.rename(columns={
                    'Noref': 'No Reff.',
                    'total_tunggakan_detail': 'Total Tunggakan',
                    'Nama': 'Nama Pelanggan'
                })
                
                # Format Total Tunggakan
                display_df['Total Tunggakan'] = display_df['Total Tunggakan'].apply(
                    lambda x: f"Rp {x:,.0f}"
                )
                
                return display_df

            # Dapatkan data detail pelanggan
            detail_customers_df = get_detailed_customers(df, selected_detail_month, selected_months)

            # Konfigurasi AgGrid untuk tabel detail pelanggan
            gb_detail = GridOptionsBuilder.from_dataframe(detail_customers_df)
            gb_detail.configure_pagination(paginationAutoPageSize=False, paginationPageSize=10)
            gb_detail.configure_selection(selection_mode='single', use_checkbox=False)
            gb_detail.configure_side_bar()
            gb_detail.configure_default_column(editable=False, sortable=True, filter=True)
            grid_options_detail = gb_detail.build()

            # Tampilkan tabel detail pelanggan
            if not detail_customers_df.empty:
                AgGrid(
                    detail_customers_df,
                    gridOptions=grid_options_detail,
                    height=400,
                    fit_columns_on_grid_load=True,
                    theme='streamlit',
                    enable_enterprise_modules=False,
                    update_mode=GridUpdateMode.SELECTION_CHANGED,
                    data_return_mode=DataReturnMode.FILTERED_AND_SORTED
                )
            else:
                st.info("Tidak ada data pelanggan dengan tunggakan untuk bulan yang dipilih.")

            # 11. Tabel Ringkasan Total Tunggakan per Kelurahan-CM (Rentang Terpilih)
            st.subheader("Total Tunggakan per Kelurahan - Customer Management")
            if 'Kelurahan' in filtered_df.columns and 'Customer Management' in filtered_df.columns:
                top_combinations = filtered_df.groupby(
                    ['Kelurahan', 'Customer Management']
                )['total_tunggakan_selected'].sum().reset_index()

                top_combinations = top_combinations.sort_values(
                    by='total_tunggakan_selected', ascending=False
                )
                top_combinations['Total Tunggakan'] = top_combinations['total_tunggakan_selected'].apply(
                    lambda x: f"Rp {x:,.0f}"
                )

                top_combinations_display = top_combinations[
                    ['Kelurahan', 'Customer Management', 'Total Tunggakan']
                ].head(5)

                gb_top = GridOptionsBuilder.from_dataframe(top_combinations_display)
                gb_top.configure_pagination(paginationAutoPageSize=False, paginationPageSize=5)
                gb_top.configure_default_column(editable=False, sortable=True, filter=True)
                grid_options_top = gb_top.build()

                AgGrid(
                    top_combinations_display,
                    gridOptions=grid_options_top,
                    height=200,
                    fit_columns_on_grid_load=True,
                    theme='streamlit',
                    enable_enterprise_modules=False,
                    update_mode=GridUpdateMode.NO_UPDATE,  # Perbaikan di sini
                    data_return_mode=DataReturnMode.FILTERED_AND_SORTED
                )
            else:
                st.info(
                    "Data tidak memiliki kolom 'Kelurahan' atau 'Customer Management' untuk menampilkan kombinasi."
                )

    # ---- Tab 4: Line Chart Pelanggan ----
    with tab4:
        if not st.session_state.data_loaded:
            show_upload_message()
        else:
            st.title("Line Chart Tunggakan")
            # 2. Ambil DataFrame hasil preprocessing
            df = st.session_state.df_processed

            # 3. Pastikan kolom 'detail_tunggakan' sudah dalam bentuk dict
            if 'detail_tunggakan' in df.columns:
                try:
                    df['detail_tunggakan'] = df['detail_tunggakan'].apply(
                        lambda x: ast.literal_eval(x) if isinstance(x, str) else x
                    )
                except Exception as e:
                    st.error(f"Error saat mempersiapkan kolom 'detail_tunggakan': {e}")
                    st.stop()
            else:
                st.error("Kolom 'detail_tunggakan' tidak ditemukan dalam data.")
                st.stop()

            # 2. Identifikasi kolom bulan-tahun
            month_year_cols = [col for col in df.columns if '-' in col]

            # 3. Urutkan kolom bulan-tahun secara kronologis
            try:
                month_year_cols_sorted = sorted(month_year_cols, key=lambda x: datetime.strptime(x, '%b-%Y'))
            except Exception as e:
                st.error(f"Error saat mengurutkan kolom bulan-tahun: {e}")
                month_year_cols_sorted = month_year_cols

            # 4. Tambahkan kolom pelanggan unik
            if 'unique_pelanggan' not in df.columns:
                df['unique_pelanggan'] = df.apply(
                    lambda row: f"{row.get('Nama Pelanggan', '')} - {row.get('Alamat', '')}",
                    axis=1
                )

            df_unique_pelanggan = df.drop_duplicates(subset=['unique_pelanggan'])

            # 5. Filter Pelanggan dan Periode
            st.markdown("### Filter Data")
            col_filter_left, col_filter_right = st.columns([1.5, 1.5])

            with col_filter_left:
                start_month = st.selectbox("Bulan-Tahun Awal", options=month_year_cols_sorted, index=0)
            with col_filter_right:
                end_month = st.selectbox("Bulan-Tahun Akhir", options=month_year_cols_sorted, index=len(month_year_cols_sorted) - 1)

            unique_pelanggan_list = df_unique_pelanggan['unique_pelanggan'].dropna().unique().tolist()
            selected_pelanggan = st.selectbox("Pilih Pelanggan (Nama - Alamat)", options=unique_pelanggan_list)
            # 6. Validasi Rentang Bulan
            try:
                start_idx = month_year_cols_sorted.index(start_month)
                end_idx = month_year_cols_sorted.index(end_month)
                if start_idx > end_idx:
                    st.error("Bulan Awal harus sebelum atau sama dengan Bulan Akhir.")
                    st.stop()
            except ValueError as e:
                st.error(f"Bulan Awal atau Bulan Akhir tidak valid: {e}")
                st.stop()

            # 7. Subset Data Pelanggan
            selected_months = month_year_cols_sorted[start_idx:end_idx + 1]
            df_pelanggan = df_unique_pelanggan[df_unique_pelanggan['unique_pelanggan'] == selected_pelanggan].copy()

            if df_pelanggan.empty:
                st.warning("Data untuk pelanggan terpilih tidak ditemukan.")
                st.stop()

            baris = df_pelanggan.iloc[0].copy()

            # 8. Hitung Data Bulanan
            data_bulanan = []
            total_sebelumnya = 0

            for i, m in enumerate(selected_months):
                # Ambil nilai tunggakan dan ganti NaN atau None dengan 0
                aktual = baris.get(m, 0) if pd.notna(baris.get(m)) else 0  # Mengganti NaN dengan 0

                # Hitung akumulasi
                if i == 0:
                    kumulatif = aktual
                else:
                    kumulatif = total_sebelumnya + aktual

                # Hitung persentase perubahan
                if i > 0 and total_sebelumnya != 0:
                    pct_aktual = ((aktual - total_sebelumnya) / total_sebelumnya) * 100
                else:
                    pct_aktual = 0

                data_bulanan.append({
                    'bulan': m,
                    'aktual': aktual,
                    'kumulatif': kumulatif,
                    'pct_aktual': pct_aktual
                })

                total_sebelumnya = kumulatif

            df_bulanan = pd.DataFrame(data_bulanan)

            # 9. Buat Visualisasi Line Chart
            st.subheader("Visualisasi Line Chart")

            # Membuat dua kolom untuk visualisasi kiri dan kanan
            col_chart_left, col_chart_right = st.columns(2)

            # Visualisasi Kiri: Total Tunggakan
            with col_chart_left:
                fig_left = go.Figure()
                fig_left.add_trace(go.Scatter(
                    x=df_bulanan['bulan'],
                    y=df_bulanan['aktual'],
                    mode='lines+markers',
                    line=dict(color='#007bff', width=2),
                    marker=dict(size=8, color='#007bff'),
                    name='Tunggakan Aktual'
                ))

                fig_left.update_layout(
                    title="Total Tunggakan per Bulan",
                    xaxis_title="Bulan-Tahun",
                    yaxis_title="Total Tunggakan (Rp)",
                    template="plotly_white",
                    hovermode="closest"
                )

                st.plotly_chart(fig_left, use_container_width=True)

            # Visualisasi Kanan: Akumulasi Tunggakan
            with col_chart_right:
                fig_right = go.Figure()
                fig_right.add_trace(go.Scatter(
                    x=df_bulanan['bulan'],
                    y=df_bulanan['kumulatif'],
                    mode='lines+markers',
                    line=dict(color='#ff9900', width=2),
                    marker=dict(size=8, color='#ff9900'),
                    name='Akumulasi Tunggakan'
                ))

                fig_right.update_layout(
                    title="Akumulasi Total Tunggakan",
                    xaxis_title="Bulan-Tahun",
                    yaxis_title="Akumulasi Tunggakan (Rp)",
                    template="plotly_white",
                    hovermode="closest"
                )

                st.plotly_chart(fig_right, use_container_width=True)

            # 10. Tampilkan Detail Pelanggan
            st.subheader("Detail Pelanggan")
            detail_cols = ['No Reff.', 'Nama Pelanggan', 'Alamat', 'Kategori Pelanggan', 'Kelurahan',
                        'Customer Management', 'jumlah_bulan_tunggakan', 'total_tunggakan', 'Denda', 'Jaminan Pembayaran']

            # Tambahkan Total Keseluruhan yang merupakan penjumlahan antara total_tunggakan dan Denda
            total_tunggakan = baris.get('total_tunggakan', 0)
            denda = baris.get('Denda', 0)
            jaminan_pembayaran = baris.get('Jaminan Pembayaran', 0)

            # Jika Denda NaN, set menjadi 0
            denda = 0 if pd.isna(denda) else denda
            jaminan_pembayaran = 0 if pd.isna(jaminan_pembayaran) else jaminan_pembayaran

            # Hitung Total Keseluruhan
            total_keseluruhan = total_tunggakan + denda

            # Membuat detail HTML dengan perubahan kolom
            detail_html = f"""
            <div style="
                border: 1px solid #ccc;
                padding: 15px;
                border-radius: 10px;
                background-color: #f9f9f9;
                width: 100%;
            ">
                <h3>Detail Pelanggan: {selected_pelanggan}</h3>
            """

            # Menambahkan semua detail pelanggan
            for col in detail_cols:
                if col in df_pelanggan.columns:
                    val = baris[col]
                    
                    # Perubahan format untuk kolom tertentu
                    if col == 'total_tunggakan':
                        val = f"Rp {total_tunggakan:,.2f}"
                    elif col == 'jumlah_bulan_tunggakan':
                        val = f"{int(baris.get('jumlah_bulan_tunggakan', 0)):,} bulan"
                    elif col == 'Denda':
                        val = f"Rp {denda:,.2f}"
                    elif col == 'Total Keseluruhan':  # Menambahkan Total Keseluruhan
                        val = f"Rp {total_keseluruhan:,.2f}"
                    elif col == 'Jaminan Pembayaran':  # Menambahkan Total Keseluruhan
                        val = f"Rp {jaminan_pembayaran:,.2f}"
                    
                    # Menambahkan baris detail
                    detail_html += f"<p><strong>{col.replace('jumlah_bulan_tunggakan', 'Jumlah Bulan Tunggakan').replace('total_tunggakan', 'Total Tunggakan')}:</strong> {val}</p>"


            # Menambahkan Total Keseluruhan di bawah detail lainnya
            detail_html += f"<h3><strong>Total Keseluruhan:</strong> Rp {total_keseluruhan:,.2f}</h3>"

            detail_html += "</div>"

            # Tampilkan HTML detail pelanggan
            st.markdown(detail_html, unsafe_allow_html=True)

            # 11. Tampilkan Tabel Detail Tunggakan
            st.subheader("Tabel Detail Tunggakan")
            df_detail = df_bulanan[['bulan', 'aktual', 'pct_aktual', 'kumulatif']].copy()

            # Filter hanya baris dengan nilai tunggakan yang valid
            df_detail = df_detail[df_detail['aktual'] > 0]

            df_detail.columns = ['Bulan', 'Tunggakan', '% Perubahan', 'Akumulasi']

            # Format angka
            df_detail['Tunggakan'] = df_detail['Tunggakan'].apply(lambda x: f"Rp {x:,.0f}")
            df_detail['% Perubahan'] = df_detail['% Perubahan'].apply(lambda x: f"{x:+.2f}%")
            df_detail['Akumulasi'] = df_detail['Akumulasi'].apply(lambda x: f"Rp {x:,.0f}")

            # Tampilkan dengan AgGrid
            gb = GridOptionsBuilder.from_dataframe(df_detail)
            gb.configure_pagination()
            gb.configure_default_column(resizable=True)

            grid_options = gb.build()
            AgGrid(
                df_detail,
                gridOptions=grid_options,
                height=300,
                theme='streamlit',
                enable_enterprise_modules=False
            )

            # Fungsi untuk membuat PNG dengan informasi lengkap dan tabel berdasarkan data yang ada
            def generate_report(df_pelanggan, df_detail, total_keseluruhan, report_type='png'):
                # Memastikan df_pelanggan tidak kosong
                if df_pelanggan.empty:
                    return "Data pelanggan kosong"
                
                # Mengambil informasi dari df_pelanggan dengan menggunakan .iloc untuk mengakses baris pertama
                no_reff = df_pelanggan.iloc[0]['No Reff.'] if 'No Reff.' in df_pelanggan.columns else 'Not Available'
                nama_pelanggan = df_pelanggan.iloc[0]['Nama Pelanggan'] if 'Nama Pelanggan' in df_pelanggan.columns else 'Not Available'
                alamat = df_pelanggan.iloc[0]['Alamat'] if 'Alamat' in df_pelanggan.columns else 'Not Available'
                kategori_pelanggan = df_pelanggan.iloc[0]['Kategori Pelanggan'] if 'Kategori Pelanggan' in df_pelanggan.columns else 'Not Available'
                kelurahan = df_pelanggan.iloc[0]['Kelurahan'] if 'Kelurahan' in df_pelanggan.columns else 'Not Available'
                customer_management = df_pelanggan.iloc[0]['Customer Management'] if 'Customer Management' in df_pelanggan.columns else 'Not Available'
                jumlah_bulan_tunggakan = df_pelanggan.iloc[0]['jumlah_bulan_tunggakan'] if 'jumlah_bulan_tunggakan' in df_pelanggan.columns else 0
                total_tunggakan = df_pelanggan.iloc[0]['total_tunggakan'] if 'total_tunggakan' in df_pelanggan.columns else 0
                denda = df_pelanggan.iloc[0]['Denda'] if 'Denda' in df_pelanggan.columns else 0
                jaminan_pembayaran = df_pelanggan.iloc[0]['Jaminan Pembayaran'] if 'Jaminan Pembayaran' in df_pelanggan.columns else 0

                # Jika Denda atau Jaminan Pembayaran NaN, set menjadi 0
                denda = 0 if pd.isna(denda) else denda
                jaminan_pembayaran = 0 if pd.isna(jaminan_pembayaran) else jaminan_pembayaran

                if report_type == 'png':
                    fig, ax = plt.subplots(figsize=(8, 10))
                    ax.axis('off')

                    # Styling untuk PNG
                    ax.text(0.1, 0.95, f"Invoice Tagihan Pelanggan PT Perusahaan Gas Negara, Tbk.", ha='left', fontsize=14, fontweight='bold', color='navy')
                    ax.text(0.1, 0.90, f"No Reff.: {no_reff}", ha='left', fontsize=12, color='black')
                    ax.text(0.1, 0.87, f"Nama Pelanggan: {nama_pelanggan}", ha='left', fontsize=12)
                    ax.text(0.1, 0.84, f"Alamat: {alamat}", ha='left', fontsize=12)
                    ax.text(0.1, 0.81, f"Kategori Pelanggan: {kategori_pelanggan}", ha='left', fontsize=12)
                    ax.text(0.1, 0.78, f"Kelurahan: {kelurahan}", ha='left', fontsize=12)
                    ax.text(0.1, 0.75, f"Customer Management: {customer_management}", ha='left', fontsize=12)
                    ax.text(0.1, 0.72, f"Jumlah Bulan Piutang: {jumlah_bulan_tunggakan} bulan", ha='left', fontsize=12)
                    ax.text(0.1, 0.69, f"Total Piutang: Rp {total_tunggakan:,.2f}", ha='left', fontsize=12)
                    ax.text(0.1, 0.66, f"Denda: Rp {denda:,.2f}", ha='left', fontsize=12)
                    ax.text(0.1, 0.63, f"Jaminan Pembayaran: Rp {jaminan_pembayaran:,.2f}", ha='left', fontsize=12)
                    ax.text(0.1, 0.60, f"Total Keseluruhan: Rp {total_keseluruhan:,.2f}", ha='left', fontsize=14, fontweight='bold')

                    # Membuat sedikit ruang antara informasi dan tabel
                    ax.text(0.1, 0.57, "-"*60, ha='left', fontsize=12, color='gray')

                    # Menampilkan Tabel Detail Tunggakan
                    ax.text(0.1, 0.55, f"Tabel Detail Tunggakan:", ha='left', fontsize=12, fontweight='bold')

                    # Menampilkan tabel detail tunggakan dari df_detail
                    row_height = 0.52  # Mulai menampilkan tabel
                    for idx, row in df_detail.iterrows():
                        ax.text(0.1, row_height, f"{row['Bulan']} - {row['Tunggakan']} - {row['% Perubahan']} - {row['Akumulasi']}", ha='left', fontsize=10)
                        row_height -= 0.05  # Memberikan jarak antar baris dalam tabel

                    # Menambahkan garis pemisah sebelum total
                    ax.text(0.1, row_height, "-"*60, ha='left', fontsize=12, color='gray')

                    png_buffer = io.BytesIO()
                    plt.savefig(png_buffer, format='png', bbox_inches='tight', dpi=300, facecolor='white')
                    plt.close(fig)
                    png_buffer.seek(0)
                    return png_buffer

                elif report_type == 'pdf':
                    buffer = io.BytesIO()
                    doc = SimpleDocTemplate(buffer, pagesize=letter)
                    styles = getSampleStyleSheet()
                    
                    # Elemen-elemen untuk PDF
                    story = []
                    
                    # Judul
                    title_style = styles['Title']
                    title_style.textColor = "navy"  # Gunakan navy yang diimpor di awal
                    story.append(Paragraph("Invoice Detail Pelanggan", title_style))
                    
                    # Data pelanggan
                    details = [
                        ["No Reff.", no_reff],
                        ["Nama Pelanggan", nama_pelanggan],
                        ["Alamat", alamat],
                        ["Kategori Pelanggan", kategori_pelanggan],
                        ["Kelurahan", kelurahan],
                        ["Customer Management", customer_management],
                        ["Jumlah Bulan Piutang", f"{jumlah_bulan_tunggakan} bulan"],
                        ["Total Piutang", f"Rp {total_tunggakan:,.2f}"],
                        ["Denda", f"Rp {denda:,.2f}"],
                        ["Jaminan Pembayaran", f"Rp {jaminan_pembayaran:,.2f}"],
                        ["Total Keseluruhan", f"Rp {total_keseluruhan:,.2f}"]
                    ]
                    
                    # Tabel detail pelanggan
                    table = Table(details, colWidths=[2*inch, 4*inch])
                    table.setStyle(TableStyle([ 
                        ('BACKGROUND', (0,0), (-1,0), 'navy'),
                        ('TEXTCOLOR', (0,0), (-1,0), 'whitesmoke'),
                        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
                        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                        ('FONTSIZE', (0,0), (-1,0), 12),
                        ('BOTTOMPADDING', (0,0), (-1,0), 12),
                        ('BACKGROUND', (0,1), (-1,-1), 'beige'),
                        ('GRID', (0,0), (-1,-1), 1, 'black')
                    ]))
                    story.append(table)
                    
                    # Tabel detail tunggakan
                    detail_headers = ['Bulan', 'Tunggakan', '% Perubahan', 'Akumulasi']
                    detail_data = [detail_headers]
                    detail_data.extend(df_detail.values.tolist())
                    
                    detail_table = Table(detail_data, colWidths=[1.5*inch, 1.5*inch, 1.5*inch, 1.5*inch])
                    detail_table.setStyle(TableStyle([
                        ('BACKGROUND', (0,0), (-1,0), 'navy'),
                        ('TEXTCOLOR', (0,0), (-1,0), 'whitesmoke'),
                        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                        ('FONTSIZE', (0,0), (-1,0), 12),
                        ('BOTTOMPADDING', (0,0), (-1,0), 12),
                        ('BACKGROUND', (0,1), (-1,-1), 'beige'),
                        ('GRID', (0,0), (-1,-1), 1, 'black')
                    ]))
                    
                    story.append(Paragraph("Tabel Detail Tunggakan", styles['Heading2']))
                    story.append(detail_table)
                    
                    doc.build(story)
                    buffer.seek(0)
                    return buffer


            # 10. Pilih format file dan klik untuk mengunduh
            report_format = st.radio("Pilih format laporan", ('PNG', 'PDF'))

            if st.button(f"Unduh Invoice sebagai {report_format}"):
                if report_format == 'PNG':
                    png_buffer = generate_report(df_pelanggan, df_detail, total_keseluruhan, 'png')
                    file_name = f"invoice_pelanggan {df_pelanggan.iloc[0]['Nama Pelanggan']} - {df_pelanggan.iloc[0]['Alamat']}.png"
                    st.download_button(
                        label="Download Invoice as PNG",
                        data=png_buffer,
                        file_name=file_name,
                        mime="image/png"
                    )
                elif report_format == 'PDF':
                    pdf_buffer = generate_report(df_pelanggan, df_detail, total_keseluruhan, 'pdf')
                    file_name = f"invoice_pelanggan {df_pelanggan.iloc[0]['Nama Pelanggan']} - {df_pelanggan.iloc[0]['Alamat']}.pdf"
                    st.download_button(
                        label="Download Invoice as PDF",
                        data=pdf_buffer,
                        file_name=file_name,
                        mime="application/pdf"
                    )


    # ---- Tab 5: Histogram Tunggakan ----
    with tab5:
        if not st.session_state.data_loaded:
            show_upload_message()
        else:
            st.title("Histogram Tunggakan")

            # Filter Inputs
            st.markdown("### Filter Data")

            # Baris pertama: Slide bulan-tahun awal dan akhir & range histogram
            col1, col2, col3 = st.columns(3)

            with col1:
                start_month, end_month = st.select_slider(
                    "Pilih Rentang Bulan-Tahun:",
                    options=month_year_cols,
                    value=(month_year_cols[0], month_year_cols[-1]),
                    key="slider_month"
                )

            with col2:
                hist_min = st.number_input("Range Histogram Minimum:", min_value=0, value=0, step=1000, key="hist_min")

            with col3:
                hist_max = st.number_input(
                    "Range Histogram Maksimum:",
                    min_value=0,
                    value=int(df['total_tunggakan'].max()),
                    step=1000,
                    key="hist_max"
                )

            # Baris kedua: Kelurahan, Customer Management, Kategori Pelanggan
            col4, col5, col6 = st.columns(3)

            with col4:
                kelurahan_filter = st.selectbox(
                    "Filter Kelurahan:",
                    ['Semua Kelurahan'] + list(df['Kelurahan'].dropna().unique()),
                    key="kelurahan_filter"
                )

            with col5:
                cm_filter = st.selectbox(
                    "Filter Customer Management:",
                    ['Semua Customer Management'] + list(df['Customer Management'].dropna().unique()),
                    key="cm_filter"
                )

            with col6:
                kategori_filter = st.selectbox(
                    "Filter Kategori Pelanggan:",
                    ['Semua Kategori'] + list(df['Kategori Pelanggan'].dropna().unique()),
                    key="kategori_filter"
                )

            # Checkbox untuk menampilkan pelanggan dengan tunggakan 0
            include_zero_tunggakan = st.checkbox('Tampilkan Pelanggan dengan Tunggakan 0', value=False)
            
            # Filter DataFrame
            filtered_df = st.session_state.df_processed

            if kelurahan_filter != "Semua Kelurahan":
                filtered_df = filtered_df[filtered_df['Kelurahan'] == kelurahan_filter]

            if cm_filter != "Semua Customer Management":
                filtered_df = filtered_df[filtered_df['Customer Management'] == cm_filter]

            if kategori_filter != "Semua Kategori":
                filtered_df = filtered_df[filtered_df['Kategori Pelanggan'] == kategori_filter]

            if hist_max > hist_min:
                filtered_df = filtered_df[(filtered_df['total_tunggakan'] >= hist_min) & (filtered_df['total_tunggakan'] <= hist_max)]
            # Menambahkan baris dengan tunggakan 0 jika checkbox dicentang
            if not include_zero_tunggakan:
                filtered_df = filtered_df[filtered_df['total_tunggakan'] > 0]

            # Generate Histogram
            st.markdown("### Histogram Distribusi Tunggakan")
            hist_data = filtered_df['total_tunggakan']

            if not hist_data.empty:
                fig = go.Figure()
                fig.add_trace(go.Histogram(
                    x=hist_data,
                    nbinsx=10,
                    marker_color='#003366',
                    opacity=0.75
                ))

                fig.update_layout(
                    title="Distribusi Total Tunggakan Pelanggan",
                    xaxis_title="Total Tunggakan (Rp)",
                    yaxis_title="Jumlah Pelanggan",
                    template="plotly_white",
                    bargap=0.2
                )

                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("Tidak ada data untuk histogram berdasarkan filter yang dipilih.")
            
            # Statistik dan Insight
            st.markdown("### Statistik Tunggakan")

            # Kolom untuk menampilkan metrik
            col_stat1, col_stat2 = st.columns(2)

            with col_stat1:
                # Total Pelanggan
                total_pelanggan = len(filtered_df)
                st.metric(label="Total Pelanggan", value=f"{total_pelanggan:,}")
                
                # Total Tunggakan
                total_tunggakan = filtered_df['total_tunggakan'].sum()
                st.metric(label="Total Tunggakan", value=f"Rp {total_tunggakan:,.0f}")
                
                # Tunggakan Maksimum
                max_tunggakan = filtered_df['total_tunggakan'].max() if not filtered_df.empty else 0
                st.metric(label="Tunggakan Maksimum", value=f"Rp {max_tunggakan:,.0f}")
                
                # Tunggakan Minimum
                min_tunggakan = filtered_df['total_tunggakan'].min() if not filtered_df.empty else 0
                st.metric(label="Tunggakan Minimum", value=f"Rp {min_tunggakan:,.0f}")

                # Tunggakan Rata-Rata
                mean_tunggakan = filtered_df['total_tunggakan'].mean() if not filtered_df.empty else 0
                st.metric(label="Rata-Rata Tunggakan", value=f"Rp {mean_tunggakan:,.0f}")

            with col_stat2:
                # Insight tambahan
                if total_pelanggan > 0:
                    # Rata-rata tunggakan
                    avg_tunggakan = total_tunggakan / total_pelanggan
                    st.metric(label="Rata-rata Tunggakan per Pelanggan", value=f"Rp {avg_tunggakan:,.0f}")

                    # Sebaran pelanggan dalam range histogram
                    mid_point = (hist_max + hist_min) / 2
                    pelanggan_bawah_mid = len(filtered_df[filtered_df['total_tunggakan'] < avg_tunggakan])
                    pelanggan_atas_mid = total_pelanggan - pelanggan_bawah_mid
                    st.metric(label=f"Pelanggan dengan Tunggakan < Rp {avg_tunggakan:,.0f}", value=f"{pelanggan_bawah_mid:,}")
                    st.metric(label=f"Pelanggan dengan Tunggakan > Rp {avg_tunggakan:,.0f}", value=f"{pelanggan_atas_mid:,}")
                    
                    # Histogram tertinggi
                    hist_counts, hist_edges = np.histogram(
                        filtered_df['total_tunggakan'], 
                        bins=np.linspace(hist_min, hist_max, 11)  # Sesuaikan dengan jumlah bin di histogram
                    )
                    max_count_index = np.argmax(hist_counts)
                    range_bawah = hist_edges[max_count_index]
                    range_atas = hist_edges[max_count_index + 1]
                    pelanggan_di_range = hist_counts[max_count_index]
                    st.metric(label=f"Mayoritas Pelanggan dalam Rentang", value=f"Rp {range_bawah:,.0f} - Rp {range_atas:,.0f}")

                    # Persentase pelanggan dalam range histogram tertinggi
                    persentase_di_range = (pelanggan_di_range / total_pelanggan) * 100
                    st.metric(label="Persentase Pelanggan di Rentang Histogram Tertinggi", value=f"{persentase_di_range:.2f}%  ({pelanggan_di_range:,} Pelanggan)")
                else:
                    st.metric(label="Informasi", value="Tidak ada data pelanggan yang cocok dengan filter saat ini.")

            # Filter tambahan berdasarkan range histogram yang dipilih
            filtered_table = filtered_df.copy()

            # Urutkan data berdasarkan 'total_tunggakan' secara ascending
            filtered_table = filtered_table.sort_values(by='total_tunggakan', ascending=True)

            # Pilih kolom yang akan ditampilkan
            columns_to_display = [
                'No Reff.', 'Nama Pelanggan', 'Alamat', 'Kelurahan',
                'Customer Management', 'Kategori Pelanggan',
                'jumlah_bulan_tunggakan', 'total_tunggakan', 'detail_tunggakan'
            ]

            # Tampilkan hanya tabel dengan highlight
            if not filtered_table.empty:
                # Gunakan DataFrame yang sudah difilter
                filtered_table = filtered_table[columns_to_display]
                
                # Tetapkan warna berdasarkan bin histogram
                bin_edges = np.linspace(hist_min, hist_max, num=11)  # Membuat 10 bins
                color_palette = [
                    '#b3cde0', '#b2e2e2', '#b2d8b2', '#ccebc5', '#d9f0d3',
                    '#edf8e9', '#f7fcf5', '#e5f5e0', '#c7e9c0', '#a1d99b'
                ]
                
                def assign_color(value):
                    for i in range(len(bin_edges) - 1):
                        if bin_edges[i] <= value < bin_edges[i + 1]:
                            return color_palette[i]
                    return color_palette[-1]

                filtered_table['highlight_color'] = filtered_table['total_tunggakan'].apply(assign_color)

                # Terapkan gaya highlight
                def highlight_row(row):
                    return [f"background-color: {row['highlight_color']}" for _ in row]

                styled_table = filtered_table.style.apply(highlight_row, axis=1)

                # Tampilkan tabel dengan highlight
                st.markdown("### Data Pelanggan dengan Highlight")
                st.dataframe(styled_table)
            else:
                st.warning("Tidak ada data pelanggan yang sesuai dengan filter.")

    with tab6:
        def generate_statistics(summary_df):
            # Menghitung bulan dengan tunggakan tertinggi dan terendah
            max_tunggakan_row = summary_df.loc[summary_df['total_tunggakan'].idxmax()]
            max_tunggakan = f"{max_tunggakan_row['bulan_tahun']} (Rp {max_tunggakan_row['total_tunggakan']:,.0f})"
            
            min_tunggakan_row = summary_df.loc[summary_df['total_tunggakan'].idxmin()]
            min_tunggakan = f"{min_tunggakan_row['bulan_tahun']} (Rp {min_tunggakan_row['total_tunggakan']:,.0f})"

            # Menghitung kenaikan tertinggi (selisih antara 2 bulan berturut-turut)
            summary_df['tunggakan_change'] = summary_df['total_tunggakan'].diff()

            # Mencari kenaikan tertinggi (bandingkan bulan sebelumnya dengan bulan berikutnya)
            max_increase_idx = summary_df['tunggakan_change'].idxmax()
            if summary_df.loc[max_increase_idx, 'tunggakan_change'] > 0:
                max_increase = f"{summary_df.loc[max_increase_idx-1, 'bulan_tahun']} ke {summary_df.loc[max_increase_idx, 'bulan_tahun']} (Rp {summary_df.loc[max_increase_idx, 'tunggakan_change']:,})"
            else:
                max_increase = "Tidak ada bulan dengan kenaikan tunggakan"

            # Mencari penurunan tertinggi (bandingkan bulan sebelumnya dengan bulan berikutnya)
            min_decrease_idx = summary_df['tunggakan_change'].idxmin()
            if summary_df.loc[min_decrease_idx, 'tunggakan_change'] < 0:
                min_decrease = f"{summary_df.loc[min_decrease_idx-1, 'bulan_tahun']} ke {summary_df.loc[min_decrease_idx, 'bulan_tahun']} (Rp {summary_df.loc[min_decrease_idx, 'tunggakan_change']:,})"
            else:
                min_decrease = "Tidak ada bulan dengan penurunan tunggakan"

            # Menghitung rata-rata jumlah pelanggan dan total tunggakan
            avg_pelanggan = summary_df['total_pelanggan'].mean()
            avg_tunggakan = summary_df['total_tunggakan'].mean()

            statistics = {
                "Bulan dengan Tunggakan Tertinggi": max_tunggakan,
                "Bulan dengan Tunggakan Terendah": min_tunggakan,
                "Kenaikan Tertinggi": max_increase,
                "Penurunan Tertinggi": min_decrease,
                "Rata-rata Jumlah Pelanggan": f"{avg_pelanggan:,.0f}",
                "Rata-rata Total Tunggakan": f"Rp {avg_tunggakan:,.0f}"
            }

            return statistics



        if not st.session_state.data_loaded:
            show_upload_message()  # Pesan jika data belum dimuat
        else:
            st.title("Bar & Line Chart - Total Pelanggan dan Tunggakan")

            # Ambil DataFrame hasil preprocessing
            df = st.session_state.df_processed

            # Identifikasi kolom bulan-tahun
            month_year_cols = [col for col in df.columns if '-' in col]

            if not month_year_cols:
                st.error("Kolom bulan-tahun tidak ditemukan dalam data.")
                st.stop()

            # Filter tambahan
            st.markdown("### Filter Data")

            # Range bulan-tahun awal dan akhir
            col1, col2 = st.columns(2)
            with col1:
                start_month = st.selectbox(
                    'Bulan-Tahun Awal',
                    options=sorted(month_year_cols, key=lambda x: datetime.strptime(x, '%b-%Y')),
                    index=0,
                    key='start_month_key7'  # Key unik
                )
            with col2:
                end_month = st.selectbox(
                    'Bulan-Tahun Akhir',
                    options=sorted(month_year_cols, key=lambda x: datetime.strptime(x, '%b-%Y')),
                    index=len(month_year_cols) - 1,
                    key='end_month_key7'  # Key unik
                )

            # Validasi range bulan-tahun
            try:
                start_idx = month_year_cols.index(start_month)
                end_idx = month_year_cols.index(end_month)
                if start_idx > end_idx:
                    st.error("Bulan-Tahun Awal harus sebelum atau sama dengan Bulan-Tahun Akhir.")
                    st.stop()
            except ValueError as e:
                st.error(f"Bulan-Tahun tidak valid: {e}")
                st.stop()

            selected_months = month_year_cols[start_idx:end_idx + 1]

            # Filter Kelurahan, Customer Management, dan Status
            col3, col4, col5, col6 = st.columns(4)
            with col3:
                # Filter Kategori Pelanggan
                if 'Kategori Pelanggan' in df.columns:
                    unique_categories = sorted(df['Kategori Pelanggan'].dropna().unique())
                    selected_category = st.selectbox(
                        'Pilih Kategori Pelanggan:',
                        options=['Semua Kategori'] + unique_categories,
                        index=0,
                        key='kategori_pelanggan_key7'
                    )
                else:
                    st.warning("Kolom 'Kategori Pelanggan' tidak ditemukan dalam data.")
                    st.stop()
            with col4:
                if 'Kelurahan' in df.columns:
                    unique_kelurahan = sorted(df['Kelurahan'].dropna().unique())
                    selected_kelurahan = st.selectbox(
                        'Kelurahan',
                        options=['Semua Kelurahan'] + unique_kelurahan,
                        index=0,
                        key='kelurahan_key7'
                    )
                else:
                    selected_kelurahan = 'Semua Kelurahan'
            with col5:
                if 'Customer Management' in df.columns:
                    unique_cm = sorted(df['Customer Management'].dropna().unique())
                    selected_cm = st.selectbox(
                        'Customer Management',
                        options=['Semua Customer Management'] + unique_cm,
                        index=0,
                        key='customer_management_key7'
                    )
                else:
                    selected_cm = 'Semua Customer Management'
            with col6:
                if 'Status' in df.columns:
                    unique_status = sorted(df['Status'].dropna().unique())
                    selected_status = st.selectbox(
                        'Status',
                        options=['Semua Status'] + unique_status,
                        index=0,
                        key='status_key7'
                    )
                else:
                    selected_status = 'Semua Status'

            # Filter DataFrame berdasarkan filter tambahan
            filtered_df = df.copy()
            if selected_kelurahan != 'Semua Kelurahan' and 'Kelurahan' in filtered_df.columns:
                filtered_df = filtered_df[filtered_df['Kelurahan'] == selected_kelurahan]
            if selected_cm != 'Semua Customer Management' and 'Customer Management' in filtered_df.columns:
                filtered_df = filtered_df[filtered_df['Customer Management'] == selected_cm]
            if selected_status != 'Semua Status' and 'Status' in filtered_df.columns:
                filtered_df = filtered_df[filtered_df['Status'] == selected_status]

            # Fungsi untuk menghitung total pelanggan dan tunggakan
            def prepare_monthly_summary(data, month_year_columns):
                monthly_summary = pd.DataFrame()
                monthly_summary['bulan_tahun'] = month_year_columns
                monthly_summary['total_pelanggan'] = data[month_year_columns].notna().sum(axis=0).values
                monthly_summary['total_tunggakan'] = data[month_year_columns].sum(axis=0).values
                return monthly_summary

            # Jika user memilih "Semua Kategori", tampilkan visualisasi akumulatif
            if selected_category == 'Semua Kategori':
                # Membuat DataFrame untuk keseluruhan data yang terfilter
                overall_summary = prepare_monthly_summary(filtered_df, selected_months)

                if overall_summary.empty:
                    st.warning("Data untuk visualisasi semua ketegori tidak ditemukan.")
                else:
                    # Visualisasi untuk akumulasi total pelanggan dan total tunggakan
                    st.subheader("Visualisasi Akumulatif Total Pelanggan dan Tunggakan")
                    fig_overall = go.Figure()

                    # Bar Chart - Akumulasi Total Pelanggan (yaxis='y1')
                    fig_overall.add_trace(go.Bar(
                        x=overall_summary['bulan_tahun'],
                        y=overall_summary['total_pelanggan'].cumsum(),  # Akumulasi total pelanggan
                        name="Total Pelanggan",
                        marker_color='rgb(100, 149, 237)',
                        yaxis='y1',
                        hovertemplate='<b>Bulan:</b> %{x}<br><b>Total Pelanggan:</b> %{y}<br>'
                    ))

                    # Line Chart - Akumulasi Total Tunggakan (yaxis='y2')
                    fig_overall.add_trace(go.Scatter(
                        x=overall_summary['bulan_tahun'],
                        y=overall_summary['total_tunggakan'].cumsum(),  # Akumulasi total tunggakan
                        mode='lines+markers',
                        name="Total Tunggakan",
                        line=dict(color='rgb(0,0,128)', width=2),
                        yaxis='y2',
                        hovertemplate='<b>Bulan:</b> %{x}<br><b>Total Tunggakan:</b> Rp %{y:,.0f}<br>'
                    ))

                    # Update Layout untuk dua y-axis
                    fig_overall.update_layout(
                        xaxis_title='Bulan-Tahun',
                        yaxis=dict(
                            title='Total Pelanggan',
                            titlefont=dict(color='rgb(100, 149, 237)'),
                            tickfont=dict(color='rgb(100, 149, 237)'),
                            showgrid=False
                        ),
                        yaxis2=dict(
                            title='Total Tunggakan (Rp)',
                            titlefont=dict(color='rgb(0,0,128)'),
                            tickfont=dict(color='rgb(0,0,128)'),
                            overlaying='y',
                            side='right',
                            showgrid=False
                        ),
                        legend=dict(x=0, y=1.2),
                        height=500,
                        template='plotly_white',
                        hovermode='x unified'
                    )

                    # Tampilkan chart akumulasi
                    st.plotly_chart(fig_overall, use_container_width=True)

                    # Menampilkan statistik
                    # st.markdown("### Statistik Kategori Pelanggan:")
                    # statistics = generate_statistics(overall_summary)
                    # for stat_name, stat_value in statistics.items():
                    #     st.write(f"**{stat_name}:** {stat_value}")


                for i, category in enumerate(unique_categories):
                    category_df = filtered_df[filtered_df['Kategori Pelanggan'] == category]
                    category_summary = prepare_monthly_summary(category_df, selected_months)

                    # Pastikan data tidak kosong
                    if category_summary['total_pelanggan'].sum() == 0:
                        continue

                    # Layout untuk visualisasi dan statistik
                    cols = st.columns(2)  # kolom untuk visualisasi dan statistik
                    with cols[0]:
                        st.subheader(f"Kategori Pelanggan: {category}")
                        fig = go.Figure()

                        # Bar Chart - Total Pelanggan
                        fig.add_trace(go.Bar(
                            x=category_summary['bulan_tahun'],
                            y=category_summary['total_pelanggan'],
                            name='Total Pelanggan',
                            marker_color='#FFA500',
                            yaxis='y1',
                            hovertemplate='<b>Bulan:</b> %{x}<br><b>Total Pelanggan:</b> %{y}<br>'
                        ))

                        # Line Chart - Total Tunggakan
                        fig.add_trace(go.Scatter(
                            x=category_summary['bulan_tahun'],
                            y=category_summary['total_tunggakan'],
                            name='Total Tunggakan',
                            mode='lines+markers',
                            line=dict(color='#1E90FF', width=2),
                            yaxis='y2',
                            hovertemplate='<b>Bulan:</b> %{x}<br><b>Total Tunggakan:</b> Rp %{y:,.0f}<br>'
                        ))

                        # Update Layout
                        fig.update_layout(
                            barmode='group',
                            xaxis=dict(title='Bulan'),
                            yaxis=dict(
                                title='Total Pelanggan',
                                titlefont=dict(color='#FFA500'),
                                tickfont=dict(color='#FFA500'),
                                showgrid=False
                            ),
                            yaxis2=dict(
                                title='Total Tunggakan (Rp)',
                                titlefont=dict(color='#1E90FF'),
                                tickfont=dict(color='#1E90FF'),
                                overlaying='y',
                                side='right',
                                showgrid=False
                            ),
                            legend=dict(x=0, y=1.2),
                            height=500,
                            template='plotly_white',
                            hovermode='x unified'
                        )
                        st.plotly_chart(fig, use_container_width=True)

                    # Menampilkan statistik
                    with cols[1]:
                        st.markdown("### Statistik Kategori Pelanggan:")
                        statistics = generate_statistics(category_summary)
                        for stat_name, stat_value in statistics.items():
                            st.write(f"**{stat_name}:** {stat_value}")

            else:
                # Visualisasi untuk kategori spesifik
                st.subheader(f"Kategori Pelanggan: {selected_category}")
                category_df = filtered_df[filtered_df['Kategori Pelanggan'] == selected_category]
                category_summary = prepare_monthly_summary(category_df, selected_months)

                fig = go.Figure()

                # Bar Chart - Total Pelanggan
                fig.add_trace(go.Bar(
                    x=category_summary['bulan_tahun'],
                    y=category_summary['total_pelanggan'],
                    name='Total Pelanggan',
                    marker_color='#FFA500',
                    yaxis='y1',
                    hovertemplate='<b>Bulan:</b> %{x}<br><b>Total Pelanggan:</b> %{y}<br>'
                ))

                # Line Chart - Total Tunggakan
                fig.add_trace(go.Scatter(
                    x=category_summary['bulan_tahun'],
                    y=category_summary['total_tunggakan'],
                    name='Total Tunggakan',
                    mode='lines+markers',
                    line=dict(color='#1E90FF', width=2),
                    yaxis='y2',
                    hovertemplate='<b>Bulan:</b> %{x}<br><b>Total Tunggakan:</b> Rp %{y:,.0f}<br>'
                ))

                # Update Layout
                fig.update_layout(
                    barmode='group',
                    xaxis=dict(title='Bulan'),
                    yaxis=dict(
                        title='Total Pelanggan',
                        titlefont=dict(color='#FFA500'),
                        tickfont=dict(color='#FFA500'),
                        showgrid=False
                    ),
                    yaxis2=dict(
                        title='Total Tunggakan (Rp)',
                        titlefont=dict(color='#1E90FF'),
                        tickfont=dict(color='#1E90FF'),
                        overlaying='y',
                        side='right',
                        showgrid=False
                    ),
                    legend=dict(x=0, y=1.2),
                    height=500,
                    template='plotly_white',
                    hovermode='x unified'
                )
                st.plotly_chart(fig, use_container_width=True)

                # Menampilkan statistik untuk kategori spesifik
                st.markdown("### Statistik Kategori Pelanggan:")
                statistics = generate_statistics(category_summary)
                for stat_name, stat_value in statistics.items():
                    st.write(f"**{stat_name}:** {stat_value}")


    st.markdown("""
        <footer style="background-color: #003366; color: white; text-align: center; padding: 20px 0; font-size: 14px; border-top: 2px solid #ffffff;">
            <p>&copy; 2025 PT Gas Negara Tbk. All rights reserved.</p>
            <p>Providing quality energy solutions for a sustainable future.</p>
            <p>For inquiries or support, please contact our PGN contact center at <strong>135</strong>.</p>
        </footer>
    """, unsafe_allow_html=True)

# Jalankan aplikasi
if __name__ == "__main__":
    main()
