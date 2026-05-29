# Slajdy Prezentacji — DynamoDB Demo
# Osoba 2: Instalacja, przykładowa baza, proste zapytania

Każde `---` to granica slajdu.

---

## Slajd 1 — Tytuł

**DynamoDB w Praktyce**
*Instalacja lokalna, przykładowa baza danych i proste zapytania*

> Twoje imię / data

---

## Slajd 2 — Instalacja: DynamoDB Local

AWS udostępnia **oficjalny obraz Docker** — identyczne API jak produkcja, bez konta AWS i bez kosztów.

```yaml
# docker-compose.yml (fragment)
services:
  dynamodb:
    image: amazon/dynamodb-local
    command: ["-jar", "DynamoDBLocal.jar", "-sharedDb"]
    ports:
      - "8000:8000"
    volumes:
      - dynamodb_data:/home/dynamodblocal/data
```

Jedyna różnica wobec produkcji — `endpoint_url`:

```python
boto3.client(
    "dynamodb",
    endpoint_url="http://dynamodb:8000",
    region_name="us-east-1",
    aws_access_key_id="dummy",      # lokalnie dowolna wartość
    aws_secret_access_key="dummy",
)
```

---

## Slajd 3 — Architektura Stosu Demo

```
Przeglądarka  ──→  :8080  Caddy Gateway
                              ├── /api/*  ──→  :3000  FastAPI + boto3
                              │                           └── boto3 ──→  :8000  DynamoDB Local
                              └──  *      ──→  :80    Caddy (statyczny HTML/JS)
```

Cztery kontenery Docker. Jedno źródło — brak CORS.

Uruchomienie całego stosu jedną komendą:

```bash
make up    # build + start wszystkich 4 serwisów
make seed  # załaduj przykładowe dane
```

---

## Slajd 4 — Tworzenie Tabeli

DynamoDB wymusza schemat **tylko na atrybutach kluczowych**. Reszta jest dowolna.

```python
# Tabela Products — tylko klucz główny
client.create_table(
    TableName="Products",
    KeySchema=[
        {"AttributeName": "productId", "KeyType": "HASH"},
    ],
    AttributeDefinitions=[
        {"AttributeName": "productId", "AttributeType": "S"},
    ],
    BillingMode="PAY_PER_REQUEST",
)

# Tabela Orders — klucz złożony (PK + SK)
client.create_table(
    TableName="Orders",
    KeySchema=[
        {"AttributeName": "orderId",    "KeyType": "HASH"},
        {"AttributeName": "customerId", "KeyType": "RANGE"},
    ],
    AttributeDefinitions=[
        {"AttributeName": "orderId",    "AttributeType": "S"},
        {"AttributeName": "customerId", "AttributeType": "S"},
    ],
    BillingMode="PAY_PER_REQUEST",
)
```

| Tabela   | PK         | SK           |
|----------|------------|--------------|
| Products | `productId`| —            |
| Orders   | `orderId`  | `customerId` |

---

## Slajd 5 — Przykładowe Dane (Seed)

Dwie tabele, wypełniane skryptem `seed.py`:

- **Products** — 20 produktów, kategorie: Electronics, Clothing, Books, Home
- **Orders** — 15 zamówień powiązanych z klientami

```python
# Fragment seed.py
products_table.put_item(Item={
    "productId": "P001",
    "name": "Wireless Headphones",
    "category": "Electronics",
    "price": Decimal("79.99"),
    "inStock": True,
})

orders_table.put_item(Item={
    "orderId":    "O001",
    "customerId": "C001",
    "status":     "shipped",
    "total":      Decimal("159.98"),
    "items":      ["P001", "P003"],
})
```

Atrybuty `name`, `price`, `inStock`, `status` — **nie są w schemacie tabeli**, ale DynamoDB je przyjmuje.

---

## Slajd 6 — Proste Zapytania: GetItem i PutItem

**GetItem** — odczyt po dokładnym kluczu, O(1):

```python
# Products — tylko PK
response = table.get_item(Key={"productId": "P001"})
item = response["Item"]

# Orders — PK + SK (klucz złożony)
response = table.get_item(Key={
    "orderId":    "O001",
    "customerId": "C001",
})
```

**PutItem** — zapis całego elementu (UPSERT — zastępuje jeśli klucz istnieje):

```python
table.put_item(Item={
    "productId": "P099",
    "name": "Nowy Produkt",
    "price": Decimal("49.99"),
    "inStock": True,
})
```

Warunkowe wstawienie (zachowuje się jak INSERT):

```python
table.put_item(
    Item={...},
    ConditionExpression="attribute_not_exists(productId)",
    # rzuca ConditionalCheckFailedException jeśli element już istnieje
)
```

---

## Slajd 7 — Proste Zapytania: UpdateItem i DeleteItem

**UpdateItem** — modyfikuje konkretne atrybuty, nie zastępuje całego elementu:

```python
table.update_item(
    Key={"productId": "P001"},
    UpdateExpression="SET #price = :price, inStock = :stock",
    ExpressionAttributeNames={"#price": "price"},  # 'price' jest zarezerwowane
    ExpressionAttributeValues={
        ":price": Decimal("99.99"),
        ":stock": False,
    },
    ReturnValues="ALL_NEW",
)
```

**DeleteItem** — wymaga pełnego klucza:

```python
# Products
table.delete_item(Key={"productId": "P001"})

# Orders — PK + SK obowiązkowe
table.delete_item(Key={
    "orderId":    "O001",
    "customerId": "C001",
})
```

| Operacja     | DynamoDB     | Zachowanie |
|--------------|--------------|------------|
| Odczyt       | `GetItem`    | Dokładny klucz → O(1). Najtańszy. |
| Tworzenie    | `PutItem`    | Zapisuje cały element. UPSERT. |
| Aktualizacja | `UpdateItem` | Modyfikuje konkretne atrybuty. |
| Usuwanie     | `DeleteItem` | Wymaga pełnego klucza (PK + SK). |

---

## Slajd 8 — Proste Zapytania: Scan

**Scan** — odczytuje wszystkie elementy tabeli:

```python
# Wszystkie produkty
response = table.scan()
items = response["Items"]

# Scan z filtrem (filtr stosowany PO odczycie — koszt się nie zmniejsza)
from boto3.dynamodb.conditions import Attr

response = table.scan(
    FilterExpression=Attr("category").eq("Electronics")
)
```

Odpowiedź zawiera `ScannedCount` i `Count` — widać różnicę gdy filtr odrzuca elementy.

> Scan czyta całą tabelę. Dobry do przeglądania danych w demo i migracji — na produkcji używaj Query z indeksem.

---

## Slajd 9 — Demo Na Żywo

**Co pokażemy:**
1. `make up` → cztery kontenery startują
2. Konfiguracja boto3 — jedna linia wskazuje na DynamoDB Local
3. Tworzenie tabel — schemat tylko dla kluczy
4. `make seed` → 20 produktów, 15 zamówień
5. GetItem — odczyt po kluczu
6. PutItem — dodanie nowego produktu
7. UpdateItem — zmiana ceny
8. DeleteItem — usunięcie produktu
9. Scan — podgląd całej tabeli, porównanie `ScannedCount` vs `Count`

---

## Slajd 10 — Podsumowanie

1. **DynamoDB Local** = produkcyjne API w Dockerze — zero konfiguracji AWS, zero kosztów
2. **Schemat = tylko klucze** — pozostałe atrybuty dowolne, różne elementy mogą mieć różne pola
3. **Klucz prosty (PK)** lub **złożony (PK + SK)** — decyzja przy tworzeniu tabeli, nie do zmiany
4. **GetItem = O(1)** — najtańszy i najszybszy odczyt
5. **PutItem = UPSERT** — zastępuje cały element, używaj `ConditionExpression` dla INSERT
6. **UpdateItem** modyfikuje atrybuty bez zastępowania całego elementu
7. **Scan** czyta całą tabelę — OK na demo, unikaj na produkcji
8. Na produkcję: usuń `endpoint_url`, dodaj prawdziwe dane uwierzytelniające. To wszystko.

---

## Slajd 11 — Zasoby

- [DynamoDB Local — obraz Docker](https://hub.docker.com/r/amazon/dynamodb-local)
- [Przewodnik DynamoDB dla Deweloperów](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/)
- [NoSQL Workbench (darmowy)](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/workbench.html) — wizualny podgląd tabel i danych
- Dokumentacja boto3: `Table.get_item`, `Table.put_item`, `Table.update_item`, `Table.delete_item`, `Table.scan`
