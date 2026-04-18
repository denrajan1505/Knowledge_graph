"""
knowledge_graph.py — Dennis Rajan Personal Finance Knowledge Graph
Each node is created in its own explicit transaction to prevent silent failures.
"""
from __future__ import annotations
import json
import re
from typing import Any
from neo4j import GraphDatabase
from openai import OpenAI


SCHEMA = """
Neo4j Knowledge Graph — Dennis Rajan Personal Finance (March 2026)
All monetary amounts are in Indian Rupees (₹).

NODE LABELS & PROPERTIES
─────────────────────────
Person           : name, month, location,
                   total_income=90000, total_liquid_balance=255500,
                   total_fixed_expenses=26099, total_food_expense=22700,
                   total_transport_expense=11100, total_shopping_expense=31500,
                   total_emi=22900, total_investments=25500,
                   total_expenses=116899, overspending=26899

Income           : source, amount
BankAccount      : bank, account_type, balance
FixedExpense     : item, amount
FoodExpense      : item, amount
TransportExpense : item, amount
ShoppingExpense  : item, amount
EMI              : loan, amount, due_date
Insurance        : policy, amount
CreditCard       : card, bill, due_date
Investment       : investment_type, amount
Insight          : highest_expense_category, second_highest_expense_category,
                   highest_emi, highest_credit_card_bill

RELATIONSHIPS (all from :Person)
──────────────────────────────────
(:Person)-[:HAS_INCOME]->           (:Income)
(:Person)-[:HAS_ACCOUNT]->          (:BankAccount)
(:Person)-[:HAS_FIXED_EXPENSE]->    (:FixedExpense)
(:Person)-[:HAS_FOOD_EXPENSE]->     (:FoodExpense)
(:Person)-[:HAS_TRANSPORT_EXPENSE]->(:TransportExpense)
(:Person)-[:HAS_SHOPPING_EXPENSE]-> (:ShoppingExpense)
(:Person)-[:HAS_EMI]->              (:EMI)
(:Person)-[:HAS_INSURANCE]->        (:Insurance)
(:Person)-[:HAS_CREDIT_CARD]->      (:CreditCard)
(:Person)-[:HAS_INVESTMENT]->       (:Investment)
(:Person)-[:HAS_INSIGHT]->          (:Insight)

QUERY TIPS
──────────
- For totals → use Person node: MATCH (p:Person) RETURN p.total_food_expense
- For breakdowns → traverse relationships to child nodes
- current savings balance = p.total_liquid_balance = 255500
- For highest X → ORDER BY amount DESC LIMIT 1
"""


class KnowledgeGraphRAG:

    def __init__(
        self,
        neo4j_uri: str,
        neo4j_user: str,
        neo4j_password: str,
        openai_api_key: str,
        model_name: str = "gpt-4",
    ):
        self.model  = model_name
        self.llm    = OpenAI(api_key=openai_api_key)
        self.driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))
        self.driver.verify_connectivity()
        self._build_graph()

    # ── utilities ─────────────────────────────────────────────────────────────

    def _tx(self, cypher: str, **params):
        """Run one Cypher statement in its own transaction."""
        with self.driver.session() as s:
            s.run(cypher, **params)

    def _read(self, cypher: str, **params) -> list[dict]:
        with self.driver.session() as s:
            return [dict(r) for r in s.run(cypher, **params)]

    def close(self):
        self.driver.close()

    def get_graph_statistics(self) -> dict:
        nodes = self._read("MATCH (n) RETURN count(n) AS c")[0]["c"]
        rels  = self._read("MATCH ()-[r]->() RETURN count(r) AS c")[0]["c"]
        return {"total_nodes": nodes, "total_relationships": rels,
                "num_entities": nodes, "num_episodes": 0}

    # ── graph builder ─────────────────────────────────────────────────────────

    def _build_graph(self):
        # Clear
        self._tx("MATCH (n) DETACH DELETE n")

        # Person node (all totals stored here for fast lookup)
        self._tx("""
            CREATE (:Person {
                name:                    'Dennis Rajan',
                month:                   'March 2026',
                location:                'Chennai',
                total_income:            90000,
                total_liquid_balance:    255500,
                total_fixed_expenses:    26099,
                total_food_expense:      22700,
                total_transport_expense: 11100,
                total_shopping_expense:  31500,
                total_emi:               22900,
                total_investments:       25500,
                total_expenses:          116899,
                overspending:            26899
            })
        """)

        # Income
        for src, amt in [
            ("Primary Salary",   65000),
            ("Freelance Income", 12000),
            ("Rental Income",     8000),
            ("Bonus Received",    5000),
        ]:
            self._tx("""
                MATCH (p:Person {name:'Dennis Rajan'})
                CREATE (n:Income {source:$src, amount:$amt})
                CREATE (p)-[:HAS_INCOME]->(n)
            """, src=src, amt=amt)

        # Bank accounts
        for bank, atype, bal in [
            ("HDFC",      "Savings Account",  85000),
            ("ICICI",     "Savings Account",  42500),
            ("Cash",      "Cash in Hand",      8000),
            ("Emergency", "Emergency Fund",  120000),
        ]:
            self._tx("""
                MATCH (p:Person {name:'Dennis Rajan'})
                CREATE (n:BankAccount {bank:$bank, account_type:$atype, balance:$bal})
                CREATE (p)-[:HAS_ACCOUNT]->(n)
            """, bank=bank, atype=atype, bal=bal)

        # Fixed expenses
        for item, amt in [
            ("House Rent",        18000),
            ("Electricity Bill",   2500),
            ("Internet Bill",      1200),
            ("Mobile Recharge",     799),
            ("Water Bill",          600),
            ("Maid Salary",        3000),
        ]:
            self._tx("""
                MATCH (p:Person {name:'Dennis Rajan'})
                CREATE (n:FixedExpense {item:$item, amount:$amt})
                CREATE (p)-[:HAS_FIXED_EXPENSE]->(n)
            """, item=item, amt=amt)

        # Food expenses
        for item, amt in [
            ("Groceries",              9500),
            ("Vegetables",             3200),
            ("Milk & Dairy",           2100),
            ("Restaurants",            5600),
            ("Snacks / Tea / Coffee",  2300),
        ]:
            self._tx("""
                MATCH (p:Person {name:'Dennis Rajan'})
                CREATE (n:FoodExpense {item:$item, amount:$amt})
                CREATE (p)-[:HAS_FOOD_EXPENSE]->(n)
            """, item=item, amt=amt)

        # Transport expenses
        for item, amt in [
            ("Petrol",          6500),
            ("Bike Service",    1800),
            ("Parking Charges",  600),
            ("Auto / Taxi",     2200),
        ]:
            self._tx("""
                MATCH (p:Person {name:'Dennis Rajan'})
                CREATE (n:TransportExpense {item:$item, amount:$amt})
                CREATE (p)-[:HAS_TRANSPORT_EXPENSE]->(n)
            """, item=item, amt=amt)

        # Shopping expenses
        for item, amt in [
            ("Clothes",             5000),
            ("Shoes",               2500),
            ("Electronics",         9000),
            ("Jewellery Purchase", 15000),
        ]:
            self._tx("""
                MATCH (p:Person {name:'Dennis Rajan'})
                CREATE (n:ShoppingExpense {item:$item, amount:$amt})
                CREATE (p)-[:HAS_SHOPPING_EXPENSE]->(n)
            """, item=item, amt=amt)

        # EMIs
        for loan, amt, due in [
            ("Bike EMI",          4500, "5th of every month"),
            ("Personal Loan EMI", 8700, "12th of every month"),
            ("Mobile EMI",        3200, "18th of every month"),
            ("Gold Loan EMI",     6500, "22nd of every month"),
        ]:
            self._tx("""
                MATCH (p:Person {name:'Dennis Rajan'})
                CREATE (n:EMI {loan:$loan, amount:$amt, due_date:$due})
                CREATE (p)-[:HAS_EMI]->(n)
            """, loan=loan, amt=amt, due=due)

        # Insurance
        for policy, amt in [
            ("Health Insurance Premium", 2500),
            ("Bike Insurance",           1200),
        ]:
            self._tx("""
                MATCH (p:Person {name:'Dennis Rajan'})
                CREATE (n:Insurance {policy:$policy, amount:$amt})
                CREATE (p)-[:HAS_INSURANCE]->(n)
            """, policy=policy, amt=amt)

        # Credit cards
        for card, bill, due in [
            ("HDFC Credit Card",  12400, "15th"),
            ("ICICI Credit Card",  8600, "20th"),
            ("Axis Credit Card",  14200, "27th"),
        ]:
            self._tx("""
                MATCH (p:Person {name:'Dennis Rajan'})
                CREATE (n:CreditCard {card:$card, bill:$bill, due_date:$due})
                CREATE (p)-[:HAS_CREDIT_CARD]->(n)
            """, card=card, bill=bill, due=due)

        # Investments
        for itype, amt in [
            ("SIP Mutual Funds",  10000),
            ("PPF Contribution",   5000),
            ("Gold Savings",       3000),
            ("Stocks Investment",  7500),
        ]:
            self._tx("""
                MATCH (p:Person {name:'Dennis Rajan'})
                CREATE (n:Investment {investment_type:$itype, amount:$amt})
                CREATE (p)-[:HAS_INVESTMENT]->(n)
            """, itype=itype, amt=amt)

        # Insight node
        self._tx("""
            MATCH (p:Person {name:'Dennis Rajan'})
            CREATE (n:Insight {
                highest_expense_category:        'Shopping (31500)',
                second_highest_expense_category: 'Fixed Expenses (26099)',
                highest_emi:                     'Personal Loan EMI (8700 due 12th)',
                highest_credit_card_bill:        'Axis Credit Card (14200 due 27th)'
            })
            CREATE (p)-[:HAS_INSIGHT]->(n)
        """)

    # ── querying ──────────────────────────────────────────────────────────────

    def _to_cypher(self, question: str) -> str:
        prompt = f"""You are a Neo4j Cypher expert. Write ONE read-only Cypher query to answer:

"{question}"

SCHEMA:
{SCHEMA}

Rules:
- Return ONLY raw Cypher. No markdown, no backticks, no explanation whatsoever.
- Always start with: MATCH (p:Person {{name:'Dennis Rajan'}})
- For simple totals use the Person property (e.g. RETURN p.total_food_expense AS food_total).
- Use meaningful RETURN aliases.
"""
        raw = self.llm.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
        ).choices[0].message.content.strip()
        raw = re.sub(r"^```[a-zA-Z]*\n?", "", raw)
        raw = re.sub(r"\n?```$", "", raw)
        return raw.strip()

    def _full_dump(self) -> str:
        rows = self._read("MATCH (n) RETURN labels(n) AS lbl, properties(n) AS props")
        return json.dumps(
            [{"labels": r["lbl"], "props": dict(r["props"])} for r in rows],
            indent=2, ensure_ascii=False
        )

    def _answer(self, question: str, facts: str) -> str:
        prompt = f"""You are Dennis Rajan's Personal Finance AI Assistant.
Answer using ONLY the data below. Always give exact ₹ amounts. Never say data is unavailable.

DATA:
{facts}

QUESTION: {question}

Give a clear, direct answer in 1-3 sentences with the exact ₹ figure."""
        return self.llm.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
        ).choices[0].message.content.strip()

    async def query(self, question: str) -> dict[str, Any]:
        cypher = ""
        raw: list[dict] = []
        facts = ""

        try:
            cypher = self._to_cypher(question)
            raw    = self._read(cypher)
            if raw:
                facts = json.dumps(raw, indent=2, ensure_ascii=False)
        except Exception as e:
            cypher = f"# Cypher error: {e}"

        if not facts:
            facts = self._full_dump()

        answer = self._answer(question, facts)
        return {"answer": answer, "cypher": cypher, "raw_results": raw}