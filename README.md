# Sonic Game

**Sonic Game** je 2D platformová hra inšpirovaná klasickými Sonic hrami. Hra je vyvinutá v jazyku Python s použitím knižnice [Pyglet](https://pyglet.readthedocs.io/) a využíva modul [aseprite.aseprite](https://github.com/tanrax/aseprite-python) na načítanie a dekódovanie `.aseprite` súborov. Hra obsahuje dynamické animácie, bossov s unikátnymi mechanikami, systém kolízií a prehrávanie hudby.

---

## Hlavné funkcie

- **Animácie a grafika:**  
  - Dynamicky načítané animácie a obrázky pomocou Resource Managera.
  - Vysoký výkon vďaka cache-ovaniu načítaných súborov.

- **Hráč a ovládanie:**  
  - Hráč (Sonic) sa môže pohybovať doľava a doprava, skákať a zbierať prstienky.
  - Ovládanie pomocou klávesnice:
    - `D` – pohyb doprava
    - `A` – pohyb doľava
    - `SPACE` – skok

- **Bossovské boje:**  
  - Rôzne typy bossov s unikátnymi správaním:
    - **Eggman:** Útočí projektílmi.
    - **Eggdrill:** Má rozšírený hitbox (špic), cez ktorý hráč môže byť zranený alebo boss môže dostať damage.
    - **MetalSonic:** Disponuje stavom "flying" a odlišnou mechanikou útoku.
  - Dynamický systém kolízií a znižovania zdravia (vyjadreného počtom prstienkov).

- **Hudba:**  
  - Hra obsahuje background hudbu (doomsday.mp3), ktorá sa prehráva počas hry.

- **Menu a loading screen:**  
  - Prezentatívne menu a loading screen pred spustením hry.

- **Spustiteľný súbor:**  
  - Hru je možné zabaliť do spustiteľného súboru (.exe) pomocou nástroja PyInstaller.

---

## Ako hrať

1. **Spustenie hry:**  
   Spustite hru spustením hlavného súboru:
   ```bash
   python main.py
    ```
   
2. **Ovládanie:**
- Pohyb: Stlačte D pre pohyb doprava, A pre pohyb doľava.
- Skok: Stlačte SPACE pre skok.
- Zbieranie prstienkov: Po ceste zbierajte prstienky, aby ste udržiavali svoje zdravie.

3. **Bossovské boje:**
- Pri stretnutí s bossom sa spustia boje, kde každý boss má svoje špecifické útoky a slabiny.
- Hráč môže bossovi dať damage iba v určitých situáciách (napríklad keď skáče) a boss môže hráča zraziť svojimi útokmi.

## Požiadavky

- **Python 3.x**
- **Pyglet**
Inštalácia:
```bash
pip install pyglet
```
- **aseprite.aseprite** (pre načítanie .aseprite súborov)
Inštalácia podľa inštrukcií na GitHub stránke
- **Assety:**
Uistite sa, že všetky obrázky, animácie a zvukové súbory (napr. doomsday.mp3) sú uložené v správnych priečinkoch, ako to vyžaduje kód.

## Inštalácia a spustenie

- **Klónovanie repozitára:**
```bash
git clone https://github.com/Petrrixx/UNIX_game.git
```
- **Inštalácia závislostí:**
```bash
pip install pyglet aseprite
```
- **Spustenie hry:**
```bash
python main.py
```
## Vytvorenie spustiteľného súboru

Ak chcete vytvoriť samostatný spustiteľný súbor (napr. .exe pre Windows), môžete použiť PyInstaller. Nainštalujte PyInstaller:
```bash
pip install pyinstaller
```
Potom spustite:

```bash
pyinstaller --onefile --name SonicGame main.py
```
Týmto sa vytvorí spustiteľný súbor SonicGame.exe v priečinku dist. Tento súbor môžete spustiť priamo bez potreby inštalácie Pythonu.

## Ovládanie a mechaniky

- **Hráč (Sonic):**
Pohybuje sa, skáče a zbiera prstienky, ktoré predstavujú jeho zdravie. Damage hráča sa znižuje, ak ho bossovia zasiahnú.

  - **Bossovské boje:**
Každý boss má unikátne správanie a slabiny:

  - **Eggman:** Útočí projektílmi; Sonic môže bossovi dať damage len keď je skákajúci.
  - **Eggdrill:** Má rozšírený hitbox, cez ktorý môže Sonic dostať damage, ale ak je skákajúci, môže bossovi dať damage.
  - **MetalSonic:** Útočí, keď je v stave "flying"; Sonic môže bossovi dať damage len keď skáče, pričom boss môže tiež zraziť Sonic, ak nie je skákajúci.
  
- **Hudba:**
  Po spustení hry začne hrať hudba doomsday.mp3, ktorá je prehrávaná na pozadí.

## Ďalšie poznámky

- Tento projekt využíva mnoho zdrojov z internetu (napr. dekóder pre .aseprite súbory) a ich autorské práva náležia pôvodným autorom.
- Ak máte akékoľvek otázky alebo pripomienky, neváhajte ma kontaktovať.
- 
## Ahoj a veľa šťastia!

Užite si hru a nech vás nikdy nezastaví rýchlosť!