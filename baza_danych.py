import streamlit as st
from supabase import create_client, Client

# Połączenie z bazą danych
@st.cache_resource
def init_connection():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = init_connection()

st.title("📦 System Zarządzania Magazynem")

tab1, tab2 = st.tabs(["Kategorie", "Produkty"])

# --- ZAKŁADKA: KATEGORIE ---
with tab1:
    st.header("Zarządzanie Kategoriami")
    
    # Formularz dodawania
    with st.form("add_category"):
        nazwa_kat = st.text_input("Nazwa kategorii")
        opis_kat = st.text_area("Opis")
        submit_kat = st.form_submit_button("Dodaj kategorię")
        
        if submit_kat:
            if nazwa_kat:
                data = {"nazwa": nazwa_kat, "opis": opis_kat}
                supabase.table("kategorie").insert(data).execute()
                st.success(f"Dodano kategorię: {nazwa_kat}")
                st.rerun()
            else:
                st.error("Nazwa jest wymagana!")

    # Wyświetlanie i usuwanie
    st.subheader("Lista kategorii")
    kategorie = supabase.table("kategorie").select("*").execute()
    
    if kategorie.data:
        for kat in kategorie.data:
            col1, col2 = st.columns([4, 1])
            col1.write(f"**{kat['nazwa']}** - {kat['opis']}")
            if col2.button("Usuń", key=f"del_kat_{kat['id']}"):
                try:
                    supabase.table("kategorie").delete().eq("id", kat['id']).execute()
                    st.success("Usunięto!")
                    st.rerun()
                except Exception as e:
                    st.error("Nie można usunąć kategorii (prawdopodobnie są w niej produkty).")
    else:
        st.info("Brak kategorii w bazie.")

# --- ZAKŁADKA: PRODUKTY ---
with tab2:
    st.header("Zarządzanie Produktami")
    
    # Pobranie kategorii do selectboxa
    kat_list = supabase.table("kategorie").select("id, nazwa").execute().data
    kat_options = {k['nazwa']: k['id'] for k in kat_list} if kat_list else {}

    # Formularz dodawania produktu
    with st.form("add_product"):
        nazwa_prod = st.text_input("Nazwa produktu")
        liczba = st.number_input("Liczba (szt.)", min_value=0, step=1)
        cena = st.number_input("Cena", min_value=0.0, step=0.01)
        wybrana_kat = st.selectbox("Kategoria", options=list(kat_options.keys()))
        
        submit_prod = st.form_submit_button("Dodaj produkt")
        
        if submit_prod:
            if nazwa_prod and wybrana_kat:
                data = {
                    "nazwa": nazwa_prod,
                    "liczba": liczba,
                    "cena": cena,
                    "kategoria_id": kat_options[wybrana_kat]
                }
                supabase.table("produkty").insert(data).execute()
                st.success("Produkt dodany!")
                st.rerun()
            else:
                st.error("Wypełnij wszystkie pola!")

    # Wyświetlanie i usuwanie produktów
    st.subheader("Aktualny stan magazynowy")
    produkty = supabase.table("produkty").select("*, kategorie(nazwa)").execute()
    
    if produkty.data:
        for p in produkty.data:
            col1, col2, col3 = st.columns([3, 2, 1])
            kat_nazwa = p['kategorie']['nazwa'] if p.get('kategorie') else "Brak"
            col1.write(f"**{p['nazwa']}** ({kat_nazwa})")
            col2.write(f"{p['liczba']} szt. | {p['cena']} PLN")
            if col3.button("Usuń", key=f"del_prod_{p['id']}"):
                supabase.table("produkty").delete().eq("id", p['id']).execute()
                st.success("Usunięto!")
                st.rerun()
    else:
        st.info("Brak produktów w bazie.")
