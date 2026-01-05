from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import requests
import pandas as pd
import os
import time
from PIL import Image
from io import BytesIO

# -- DEPENDENCIAS --
# pip install selenium webdriver-manager pandas XlsxWriter requests pillow

# Crear carpeta para imágenes (no se elimina al final)
os.makedirs("temp_images", exist_ok=True)

# URLs de cada página
urls = [
    "https://visench.en.alibaba.com/productgrouplist-950769967-1/Leoch_Battery.html?filter=all&spm=a2700.shop_plgr.41413.dbtmnavgo",
    "https://visench.en.alibaba.com/productgrouplist-950769967-2/Leoch_Battery.html?filter=all&spm=a2700.shop_plgr.41413.dbtmnavgo",
    "https://visench.en.alibaba.com/productgrouplist-950769967-3/Leoch_Battery.html?filter=all&spm=a2700.shop_plgr.41413.dbtmnavgo",
    "https://visench.en.alibaba.com/productgrouplist-950769967-4/Leoch_Battery.html?filter=all&spm=a2700.shop_plgr.41413.dbtmnavgo",
    "https://visench.en.alibaba.com/productgrouplist-950769967-5/Leoch_Battery.html?filter=all&spm=a2700.shop_plgr.41413.dbtmnavgo",
]

# Inicializar Chrome
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

products = []
img_counter = 1

for url in urls:
    driver.get(url)
    time.sleep(3)
    # Hacer scroll para lazy-load
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)

    # Localizar el contenedor principal
    try:
        gallery = driver.find_element(By.CLASS_NAME, "component-product-list")
    except:
        continue

    # Solo las tarjetas dentro de component-product-list
    cards = gallery.find_elements(By.CLASS_NAME, "icbu-product-card")
    for card in cards:
        # Título
        try:
            title = card.find_element(By.CSS_SELECTOR, ".title-con").text.strip()
        except:
            title = "N/A"
        # Precio
        try:
            price = card.find_element(By.CSS_SELECTOR, ".price .num").text.strip()
        except:
            price = "N/A"
        # URL de imagen
        try:
            img_url = card.find_element(By.TAG_NAME, "img").get_attribute("src")
            if img_url.startswith("//"):
                img_url = "https:" + img_url
        except:
            img_url = ""

        # Descargar y convertir imagen a PNG
        img_path = ""
        if img_url:
            try:
                resp = requests.get(img_url, timeout=10)
                img = Image.open(BytesIO(resp.content)).convert("RGB")
                img_path = f"temp_images/img_{img_counter}.png"
                img.save(img_path, format="PNG")
                img_counter += 1
            except Exception as e:
                print(f"Error con imagen {img_url}: {e}")
                img_path = ""

        products.append({
            "Título": title,
            "Imagen": img_path,
            "Precio": price
        })

driver.quit()

# Volcar a Excel con imágenes incrustadas
df = pd.DataFrame(products)
excel_file = "productos_leoch_filtrados.xlsx"
with pd.ExcelWriter(excel_file, engine="xlsxwriter") as writer:
    df.to_excel(writer, sheet_name="Productos", index=False, startrow=1, header=False)
    workbook  = writer.book
    worksheet = writer.sheets["Productos"]

    # Cabecera
    hdr_fmt = workbook.add_format({"bold": True, "align": "center"})
    for col_num, header in enumerate(df.columns):
        worksheet.write(0, col_num, header, hdr_fmt)

    # Anchos de columna
    worksheet.set_column("A:A", 50)
    worksheet.set_column("B:B", 20)
    worksheet.set_column("C:C", 15)

    # Insertar imágenes
    for row_idx, img_path in enumerate(df["Imagen"], start=1):
        if img_path and os.path.exists(img_path):
            worksheet.set_row(row_idx, 100)
            worksheet.insert_image(row_idx, 1, img_path, {"x_scale": 0.5, "y_scale": 0.5})

print(f"✅ Excel generado: {excel_file}")
print("✅ Imágenes guardadas en temp_images/ (no se eliminan).")
