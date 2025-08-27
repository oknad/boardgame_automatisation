import json
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# --------------------------------------------
# Konfiguration
# --------------------------------------------
# BGA_URL = "https://boardgamearena.com/#!gamepanel?game=lostcities"  # Spiel-URL
BGA_URL = "https://boardgamearena.com/lobby"
OUTPUT_JSON = "bga_dommap.json"
OUTPUT_CSV = "bga_dommap.csv"

# Dein Chrome-Profil-Pfad (Windows Beispiel: r"C:\Users\<NAME>\AppData\Local\Google\Chrome\User Data")
# Wichtig: Dort bist du schon bei BGA eingeloggt
USER_DATA_DIR = r"C:\Users\Danko\AppData\Local\Google\Chrome\User Data"
PROFILE_DIR = "Default"  # oder "Profile 1" etc.

# --------------------------------------------
# Browser starten mit deinem Profil (eingeloggt)
# --------------------------------------------
options = webdriver.ChromeOptions()
options.add_argument(f"user-data-dir={USER_DATA_DIR}")
options.add_argument(f"profile-directory={PROFILE_DIR}")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
driver.get(BGA_URL)

# --------------------------------------------
# JS zum Sammeln der DOM-Elemente
# --------------------------------------------
js = """
function cssPath(el) {
  if (!(el instanceof Element)) return '';
  const path = [];
  while (el && el.nodeType === Node.ELEMENT_NODE) {
    let selector = el.nodeName.toLowerCase();
    if (el.id) { selector += "#" + el.id; path.unshift(selector); break; }
    let sib = el, nth = 1;
    while (sib = sib.previousElementSibling) if (sib.nodeName.toLowerCase() === selector) nth++;
    if (nth !== 1) selector += `:nth-of-type(${nth})`;
    path.unshift(selector);
    el = el.parentNode;
  }
  return path.join(" > ");
}
function guessKind(el) {
  if (el.matches("button,[role=button],a[href],input[type=button],input[type=submit]")) return "action";
  if (el.matches("[data-slot-id],.cell,.slot")) return "board_cell";
  if (el.matches(".market,.display,[data-display]")) return "display";
  if (el.matches("[role=dialog],.modal")) return "overlay";
  if (el.matches(".gamelog,[role=log]")) return "log";
  return "other";
}
return [...document.querySelectorAll("body *")].map(el => {
  const r = el.getBoundingClientRect();
  return {
    selector: cssPath(el),
    tag: el.tagName.toLowerCase(),
    kind: guessKind(el),
    clickable: !!(el.onclick || el.matches("button,a,[role=button]")),
    text: el.textContent.trim().slice(0,50),
    rect: {x:r.x,y:r.y,w:r.width,h:r.height}
  };
}).filter(e => e.rect.w>0 && e.rect.h>0);
"""

items = driver.execute_script(js)

# --------------------------------------------
# Speichern als JSON + CSV
# --------------------------------------------
with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
    json.dump(items, f, ensure_ascii=False, indent=2)

df = pd.DataFrame(items)
df.to_csv(OUTPUT_CSV, index=False, encoding="utf-8")

print(f"Gespeichert: {OUTPUT_JSON} & {OUTPUT_CSV} (Elemente: {len(items)})")

driver.quit()
