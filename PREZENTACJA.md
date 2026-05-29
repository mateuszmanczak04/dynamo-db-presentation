# Slajdy Prezentacji — DynamoDB Demo

Każde `---` to granica slajdu.

---

## Slajd 1 — Tytuł

**DynamoDB w Praktyce**
*Lokalne środowisko, CRUD i projektowanie wzorców dostępu*

> Podtytuł / Twoje imię / data

---

## Slajd 2 — Czym jest DynamoDB?

**DynamoDB** to w pełni zarządzana baza danych NoSQL od AWS.

- Magazyn klucz-wartość + dokumenty (nie relacyjna, bez SQL)
- Projektowana pod **jednocyfrowe opóźnienia w milisekundach** przy dowolnej skali
- Skaluje poziomo rozkładając dane na partycje
- **Pricing serverless** — płacisz za odczyty/zapisy, nie za instancję
- Brak schematu dla pól nie będących kluczem — elementy w tej samej tabeli mogą wyglądać zupełnie inaczej

> „Zmusza do przemyślenia wzorców dostępu z góry, nie po fakcie."

---

## Slajd 3 — Architektura Stosu Demo

```
Przeglądarka  ──→  :8080  Caddy Gateway
                              ├── /api/*  ──→  :3000  FastAPI + boto3
                              │                           └── boto3 ──→  :8000  DynamoDB Local
                              └──  *      ──→  :80    Caddy (statyczny HTML/JS)
```

Cztery kontenery Docker. Jedno źródło — brak CORS.

**DynamoDB Local** = oficjalny obraz Docker od AWS. Identyczne API jak produkcja. Bez konta AWS, bez kosztów. Jedyna różnica: `endpoint_url`.

```python
boto3.client("dynamodb", endpoint_url="http://dynamodb:8000")
```

---

## Slajd 4 — Model Danych: Częściowy Schemat

DynamoDB wymusza schemat **tylko na atrybutach kluczowych**. Reszta jest dowolna.

```python
# Tworzenie tabeli — deklarowane są tylko klucze
client.create_table(
    TableName="Products",
    KeySchema=[{"AttributeName": "productId", "KeyType": "HASH"}],
    AttributeDefinitions=[
        {"AttributeName": "productId", "AttributeType": "S"},
    ],
)

# W czasie zapisu — akceptowane są dowolne atrybuty
table.put_item(Item={
    "productId": "P001",
    "name": "Wireless Headphones",   # ← nie w schemacie
    "price": Decimal("79.99"),        # ← nie w schemacie
    "inStock": True,                  # ← nie w schemacie
})
```

**Dostępne typy:** `S` (String), `N` (Number), `B` (Binary), `BOOL`, `NULL`, `L` (List), `M` (Map), `SS/NS/BS` (Sets)

---

## Slajd 5 — Klucze: Klucz Partycji i Klucz Sortowania

**Klucz partycji (HASH)** — obowiązkowy. Hashowany → określa fizyczny shard. Jak klucz w mapie. Wyszukiwanie O(1).

**Klucz sortowania (RANGE)** — opcjonalny. Elementy z tym samym PK są sortowane przez SK w obrębie sharda. Umożliwia zapytania zakresowe.

| Tabela   | PK         | SK           | Przypadek użycia |
|----------|------------|--------------|------------------|
| Products | `productId`| —            | Bezpośrednie wyszukiwanie po ID produktu |
| Orders   | `orderId`  | `customerId` | Złożony klucz zamówienie + klient |

**Projekt kluczy to Twoja najważniejsza decyzja.** Złe klucze = kosztowne skany w czasie działania. Nie można ich zmienić po utworzeniu.

---

## Slajd 6 — Globalny Indeks Wtórny (GSI)

GSI to **kopia tabeli, przeindeksowana** na innych atrybutach. Utrzymywana automatycznie.

```
Indeks główny:  productId  →  element
CategoryIndex:  category   →  element   ← GSI
```

Bez GSI na `category`:
- „Pobierz wszystkie Electronics" = pełny Scan (czyta wszystkie 100 elementów, filtruje)

Z `CategoryIndex`:
- „Pobierz wszystkie Electronics" = Query (czyta tylko partycję Electronics)

```python
client.create_table(
    ...
    GlobalSecondaryIndexes=[{
        "IndexName": "CategoryIndex",
        "KeySchema": [{"AttributeName": "category", "KeyType": "HASH"}],
        "Projection": {"ProjectionType": "ALL"},
    }],
)
```

---

## Slajd 7 — Operacje CRUD

| Operacja | DynamoDB | Zachowanie |
|----------|----------|------------|
| Odczyt   | `GetItem` | Dokładny klucz → O(1). Najtańszy. |
| Tworzenie| `PutItem` | Zapisuje cały element. **Zastępuje** jeśli klucz istnieje (UPSERT). |
| Aktualizacja | `UpdateItem` | Modyfikuje konkretne atrybuty. Element nie jest zastępowany. |
| Usuwanie | `DeleteItem` | Wymaga pełnego klucza (PK + SK jeśli złożony). |

**Warunkowe zapisy** — PutItem zachowuje się jak INSERT:
```python
table.put_item(
    Item={...},
    ConditionExpression="attribute_not_exists(productId)"
    # rzuca ConditionalCheckFailedException jeśli element istnieje
)
```

**Przykład UpdateExpression:**
```python
table.update_item(
    Key={"productId": "P001"},
    UpdateExpression="SET #price = :price",
    ExpressionAttributeNames={"#price": "price"},  # 'price' jest zarezerwowane
    ExpressionAttributeValues={":price": Decimal("99.99")},
    ReturnValues="ALL_NEW",
)
```

---

## Slajd 8 — Scan vs Query (kluczowa lekcja)

|                   | **Scan**                         | **Query**                        |
|-------------------|----------------------------------|----------------------------------|
| Co odczytuje      | Każdy element w tabeli           | Wszystkie elementy w jednej partycji |
| Filtr stosowany   | Po odczycie wszystkiego          | Warunek klucza ogranicza odczyty |
| Koszt             | Proporcjonalny do **rozmiaru tabeli** | Proporcjonalny do **wyniku** |
| Kiedy używać      | Migracje, analityka, jednorazowe | Wszystkie ścieżki dostępu na produkcji |

**Płacisz za to co DynamoDB odczytuje, nie za to co zwraca.**

```
Products: 100 elementów

Scan (bez filtra):          scanned=100  returned=100  ✓ uczciwie
Scan + filtr Electronics:   scanned=100  returned=25   ✗ zapłaciłeś za 75 niepotrzebnych elementów
Query na CategoryIndex:     scanned=25   returned=25   ✓ zapłaciłeś tylko za to co dostałeś
```

---

## Slajd 9 — Koszt Złego Wzorca Dostępu

DynamoDB on-demand: **$0,25 za milion jednostek Read Capacity Units**
Odczyt eventually consistent: **0,5 RCU za element** (≤4KB)

**Scenariusz:** znajdź 25 produktów Electronics spośród 100 łącznie. 100 000 żądań/dzień.

|                       | RCU/op  | $/op         | $/miesiąc     |
|-----------------------|---------|--------------|---------------|
| Scan (bez GSI)        | 50 RCU  | $0,0000125   | **$37,50**    |
| Query (CategoryIndex) | 12,5 RCU| $0,000003125 | **$9,38**     |
| **Oszczędności**      |         |              | **$28,12/mies.** |

Skala do 10 mln elementów → Scan kosztuje $1 250/mies. dla tego samego zapytania. Query dalej kosztuje $9,38.

**Projektuj wzorce dostępu przed pisaniem kodu.**

---

## Slajd 10 — FilterExpression

Filtr stosowany **w pamięci po odczycie przez DynamoDB**, przed wysłaniem do klienta.

```python
table.scan(
    FilterExpression=Attr("category").eq("Electronics") & Attr("price").lte(Decimal("50"))
)
```

- Zmniejsza **dane przesyłane przez sieć** ✓
- **NIE** zmniejsza kosztu odczytu ✗ — płacisz za wszystko przeskanowane

Używaj `FilterExpression` do redukcji payloadu sieciowego.  
Używaj **GSI + Query** do redukcji kosztu odczytu.

> „FilterExpression nie zastępuje właściwego projektu kluczy."

---

## Slajd 11 — Demo Na Żywo

**Co pokażemy:**
1. `make up` → cztery kontenery startują
2. Konfiguracja AWS SDK — jedna linia wskazuje na DynamoDB Local
3. Tworzenie tabeli — schemat tylko dla kluczy
4. `make seed` → 100 produktów, 15 zamówień
5. CRUD: GetItem, PutItem, UpdateItem, DeleteItem
6. Scan vs FilterExpression — obserwuj `scanned_count` vs `returned_count`
7. Szacunki kosztów na żywo w UI
8. NoSQL Workbench — wizualna inspekcja GSI

---

## Slajd 12 — Kluczowe Wnioski

1. **DynamoDB Local** = produkcyjne API, zero konfiguracji AWS
2. **Schemat = tylko klucze** — atrybuty nie będące kluczem to dowolne dokumenty
3. **GetItem to O(1)** — hash na kluczu partycji, bezpośrednie wyszukiwanie sharda
4. **Płacisz za scanned_count**, nie returned_count
5. **Scan = pełny odczyt tabeli** za każdym razem — unikaj na produkcyjnych ścieżkach
6. **GSI rozwiązuje wzorce dostępu poza kluczem** — utrzymuj alternatywne indeksy w czasie zapisu
7. **Wzorce dostępu najpierw** — projektuj klucze wokół sposobu zapytań, nie struktury danych
8. Na produkcję: usuń `endpoint_url`, dodaj prawdziwe dane uwierzytelniające. To wszystko.

---

## Slajd 13 — Zasoby (opcjonalne / zapasowe)

- [Przewodnik DynamoDB dla Deweloperów](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/)
- [NoSQL Workbench (darmowy download)](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/workbench.html)
- [Obraz Docker DynamoDB Local](https://hub.docker.com/r/amazon/dynamodb-local)
- [Alex DeBrie — The DynamoDB Book](https://www.dynamodbbook.com/) — najlepsze pogłębione źródło
- [Kalkulator cen DynamoDB](https://aws.amazon.com/dynamodb/pricing/on-demand/)
- Dokumentacja boto3: `Table.get_item`, `Table.put_item`, `Table.update_item`, `Table.scan`, `Table.query`
