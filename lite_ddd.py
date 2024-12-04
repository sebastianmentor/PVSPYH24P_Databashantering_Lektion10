# **Introduktion till Domändriven Design (DDD)**

# Domändriven design (DDD) är en metodik inom mjukvaruutveckling som fokuserar på att anpassa systemets design till den komplexa affärsdomänen. Syftet är att skapa en gemensam förståelse mellan utvecklingsteamet och domänexperter genom att använda ett gemensamt språk och modellera systemet baserat på domänens koncept och regler.

# **Nyckelbegrepp i DDD**

# 1. **Ubiquitous Language (Allmänt språk):** Ett gemensamt språk som används av både utvecklare och domänexperter för att säkerställa att alla har samma förståelse av termer och koncept.

# 2. **Bounded Context (Begränsad kontext):** En tydligt definierad del av systemet där ett specifikt språk och modell används konsekvent. Detta hjälper till att hantera komplexitet genom att dela upp systemet i mindre, mer hanterbara delar.

# 3. **Entiteter:** Objekt med en unik identitet som kvarstår över tid, även om deras attribut förändras. Exempel: En kund eller en beställning.

# 4. **Värdeobjekt:** Objekt som definieras av sina attribut och är utbytbara om deras värden är identiska. De är immutabla och har ingen egen identitet. Exempel: Pengar eller en adress.

# 5. **Aggregat:** En samling av entiteter och värdeobjekt som behandlas som en enhet för dataändringar. Aggregatet har en rotentitet som fungerar som ingångspunkt.

# 6. **Repository (Förråd):** En abstraktion av datalagring som ger en illusion av en samling objekt i minnet. Det används för att hämta och lagra aggregat.

# 7. **Tjänster:** Operationer som inte naturligt hör till någon specifik entitet eller värdeobjekt men är viktiga för domänen.

# 8. **Fabriker:** Ansvarar för att skapa komplexa objekt eller aggregat, särskilt när skapandeprocessen är komplicerad.

# 9. **Domänhändelser:** Händelser som har inträffat i domänen och som är viktiga för systemet att känna till och reagera på.

# ---

# **Exempel i Python**

# Låt oss illustrera dessa koncept genom att skapa ett enkelt beställningshanteringssystem för en e-handelsapplikation.

# **1. Värdeobjekt**
# Värdeobjekt är immutabla och definieras av sina attribut.

from dataclasses import dataclass

@dataclass(frozen=True)
class Pengar:
    valuta: str
    belopp: float

    def plus(self, annan: 'Pengar') -> 'Pengar':
        if self.valuta != annan.valuta:
            raise ValueError("Kan inte addera olika valutor.")
        return Pengar(self.valuta, self.belopp + annan.belopp)

@dataclass(frozen=True)
class Adress:
    gata: str
    stad: str
    postnummer: str
    land: str


# **2. Entiteter**
# Entiteter har en unik identitet.

@dataclass
class Kund:
    kund_id: int
    namn: str
    leveransadress: Adress

@dataclass(frozen=True)
class Produkt:
    produkt_id: int
    namn: str
    pris: Pengar


# **3. Aggregat**
# `Beställning` är ett aggregat med `Beställningsrad` som delobjekt.

from typing import List
from datetime import datetime

@dataclass
class Beställningsrad:
    produkt: Produkt
    kvantitet: int

    @property
    def rad_total(self) -> Pengar:
        total = self.produkt.pris.belopp * self.kvantitet
        return Pengar(self.produkt.pris.valuta, total)

@dataclass
class Beställning:
    beställnings_id: int
    kund: Kund
    rader: List[Beställningsrad]
    skapad_datum: datetime
    status: str

    def total_belopp(self) -> Pengar:
        total = Pengar(valuta="SEK", belopp=0)
        for rad in self.rader:
            total = total.plus(rad.rad_total)
        return total

    def lägg_till_rad(self, produkt: Produkt, kvantitet: int):
        self.rader.append(Beställningsrad(produkt, kvantitet))


# **4. Repository**
# Förråd för att hantera lagring och hämtning av beställningar.

class BeställningRepository:
    def __init__(self):
        self._storage = {}

    def spara(self, beställning: Beställning):
        self._storage[beställning.beställnings_id] = beställning

    def hämta(self, beställnings_id: int) -> Beställning:
        return self._storage.get(beställnings_id)

    def ta_bort(self, beställnings_id: int):
        if beställnings_id in self._storage:
            del self._storage[beställnings_id]


# **5. Tjänster**
# Tjänster för affärslogik som inte passar in i entiteter eller värdeobjekt.

class Betalningstjänst:
    def bearbeta_betalning(self, beställning: Beställning, betalningsuppgifter):
        # Logik för att bearbeta betalning
        print(f"Bearbetar betalning för beställning {beställning.beställnings_id}")
        beställning.status = "Betald"


# **6. Fabriker**
# Fabriker för att skapa komplexa objekt.

class Beställningsfabrik:
    _id_counter = 1

    @classmethod
    def skapa_beställning(cls, kund: Kund, produkter: List[Produkt], kvantiteter: List[int]) -> Beställning:
        rader = []
        for produkt, kvantitet in zip(produkter, kvantiteter):
            rader.append(Beställningsrad(produkt, kvantitet))
        beställning = Beställning(
            beställnings_id=cls._id_counter,
            kund=kund,
            rader=rader,
            skapad_datum=datetime.now(),
            status="Ny"
        )
        cls._id_counter += 1
        return beställning


# **7. Domänhändelser**
# Hantering av händelser inom domänen.

class Domänhändelse:
    pass

@dataclass
class BeställningSkapad(Domänhändelse):
    beställning: Beställning

@dataclass
class BetalningGenomförd(Domänhändelse):
    beställning: Beställning

class Händelsehanterare:
    def hantera(self, händelse: Domänhändelse):
        if isinstance(händelse, BeställningSkapad):
            print(f"Beställning {händelse.beställning.beställnings_id} skapad.")
        elif isinstance(händelse, BetalningGenomförd):
            print(f"Betalning genomförd för beställning {händelse.beställning.beställnings_id}.")

# **8. Användningsexempel**

# Skapa värdeobjekt för priser
pris1 = Pengar("SEK", 150)
pris2 = Pengar("SEK", 250)

# Skapa produkter
produkt1 = Produkt(1, "Laptop", pris1)
produkt2 = Produkt(2, "Mobiltelefon", pris2)

# Skapa en kund
adress = Adress("Exempelgatan 12", "Göteborg", "41101", "Sverige")
kund = Kund(1, "Erik Svensson", adress)

# Skapa en beställning via fabriken
beställning = Beställningsfabrik.skapa_beställning(
    kund,
    [produkt1, produkt2],
    [1, 2]
)

# Spara beställningen i förrådet
repo = BeställningRepository()
repo.spara(beställning)

# Hantera domänhändelser
händelsehanterare = Händelsehanterare()
händelsehanterare.hantera(BeställningSkapad(beställning))

# Bearbeta betalning
betalningstjänst = Betalningstjänst()
betalningstjänst.bearbeta_betalning(beställning, betalningsuppgifter=None)

# Hantera betalningshändelse
händelsehanterare.hantera(BetalningGenomförd(beställning))
