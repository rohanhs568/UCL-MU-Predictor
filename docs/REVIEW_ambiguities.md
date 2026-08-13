# Review list: name traps and judgement calls

- 503 distinct teams, 577 aliases
- 73 teams appear in **both** sources (these are the joins that matter)
- 173 CL-only, 257 domestic-only

## 1. Identical strings that are DIFFERENT clubs

A naive `JOIN ON name = name` or any fuzzy matcher will merge these incorrectly.

| String | CL source = | Domestic source = |
|---|---|---|
| `Apollon` | Apollon Limassol (Cyprus) | Apollon Smyrnis (Greece) |
| `Aris` | Aris Limassol (Cyprus) | Aris Thessaloniki (Greece) |

## 2. Near-identical strings that are DIFFERENT clubs

- **Hibernians (CL)** vs **Hibernian (SC0)** - Malta vs Scotland. Kept separate.
- **Brest (F1/CL)** vs **Dinamo Brest (CL)** - France vs Belarus. Kept separate.
- **Shakhtar Donetsk (CL)** vs **Shakhtyor (CL)** - Ukraine vs Belarus (Soligorsk). Kept separate.
- **Sparta Praha (CL)** vs **Sparta Rotterdam (N1)** - Czechia vs Netherlands. Kept separate.
- **Spartak Moskva (CL)** vs **Spartak Trnava (CL)** - Russia vs Slovakia. Kept separate.
- **Astana (CL)** vs **Astra (CL)** - Kazakhstan vs Romania (Giurgiu). Kept separate.
- **Riga (CL)** vs **Rigas FS (CL)** - Two separate Latvian clubs. Kept separate.
- **Vikingur (CL)** vs **Vikingur Reykjavik (CL)** - Faroe Islands (Gota) vs Iceland. Kept separate.
- **FC Santa Coloma (CL)** vs **UE Santa Coloma (CL)** - Two separate Andorran clubs. Kept separate.
- **Atletic Club d'Escaldes (CL)** vs **Inter Club d'Escaldes (CL)** - Two separate Andorran clubs. Kept separate.
- **Tirana (CL)** vs **Partizani Tirana (CL)** - Two separate Albanian clubs. Kept separate.
- **Dinamo Zagreb (CL)** vs **Lokomotiva Zagreb (CL)** - Two separate Croatian clubs. Kept separate.
- **Dinamo Tbilisi (CL)** vs **Dinamo Batumi (CL)** - Two separate Georgian clubs. Kept separate.
- **Partizan (CL)** vs **Partizani Tirana (CL)** - Serbia vs Albania. Kept separate.
- **Ajaccio (F1)** vs **Ajaccio GFCO (F1)** - AC Ajaccio vs Gazelec Ajaccio. Kept separate.
- **Ad. Demirspor (T1)** vs **Adanaspor (T1)** - Adana Demirspor vs Adanaspor. Kept separate.
- **Gaziantep (T1)** vs **Gaziantepspor (T1)** - Gaziantep FK (est. 2018) vs the older club. Kept separate.
- **Athens Kallithea (G1)** vs **Kallonis (G1)** - Kallithea vs Kalloni. Kept separate.
- **Verona (I1)** vs **Chievo (I1)** - Hellas Verona vs Chievo Verona. Kept separate.
- **Guimaraes (P1)** vs **Setubal (P1)** - Vitoria Guimaraes vs Vitoria Setubal. Kept separate.
- **Paris SG (F1)** vs **Paris FC (F1)** - Two separate Paris clubs. Kept separate.
- **Union Berlin (CL/D1)** vs **Union Saint-Gilloise (CL/B1)** - Germany vs Belgium. Kept separate.
- **Istanbul Basaksehir (T1 'Buyuksehyr')** vs **Istanbulspor (T1)** - Two separate Istanbul clubs. Kept separate.

## 3. Same club, two strings within ONE source

- `Mouscron` and `Mouscron-Peruwelz` (both B1) -> one team_id. The only intra-source duplicate found.

## 4. Judgement calls worth confirming

- **`Apollon` (CL) = Apollon Limassol, Cyprus.** Apollon Limassol won the Cypriot title in 2021/22 and entered CL qualifying. Apollon Smyrnis (the G1 club) has never played CL. Confidence: high, but see the verification query below.
- **`Aris` (CL) = Aris Limassol, Cyprus.** Aris Limassol won the Cypriot title in 2022/23. Aris Thessaloniki (the G1 club) did not finish high enough in Greece to reach CL qualifying in this window. Confidence: high, but verify.
- **`Banants` -> canonical `Urartu`** (renamed 2019). Only `Banants` appears in the data.
- **`Videoton` -> canonical `Fehervar`** (renamed 2018). Only `Videoton` appears.
- **`FCI Tallinn` and `Tallinna FC Levadia`** kept as separate teams. They merged in 2017; if you want one continuous entity, merge these two team_ids.
- **`Viitorul` and `SSC Farul`** kept as separate teams. Viitorul Constanta merged into Farul in 2021; merge the ids if you want one entity.
- **`Cardiff` and `Swansea`** are Welsh clubs in the English league; country is set to Wales, league to E0. Change if you'd rather group by competition.

## 5. Verification query for the two Cyprus/Greece cases

Your CL csvs have a `stadium_name` column. Run this over the full set of CL files to confirm which club each string refers to:

```sql
SELECT home_team_name AS team, stadium_name, COUNT(*) AS n
FROM cl_matches
WHERE home_team_name IN ('Aris','Apollon')
GROUP BY 1,2 ORDER BY 1,3 DESC;
```

A Limassol ground (e.g. Alphamega Stadium / Tsirion) confirms the Cypriot club; Kleanthis Vikelidis (Thessaloniki) or Georgios Kamaras (Athens) would mean the Greek club is also in the CL data, in which case that alias needs splitting by season.
