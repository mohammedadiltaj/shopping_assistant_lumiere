from typing import List, Optional, Dict
import json
from database import get_db_connection

class ProductCatalog:
    def __init__(self):
        pass

    def search_products(self, query: str = "", category: str = "", tags: List[str] = []) -> List[Dict]:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        sql = "SELECT * FROM products WHERE 1=1"
        params = []
        
        if category:
            sql += " AND category LIKE ?"
            params.append(f"%{category}%")
            
        if query:
            # Tokenize query for better matching
            tokens = query.lower().split()
            for token in tokens:
                sql += " AND (lower(name) LIKE ? OR lower(description) LIKE ? OR lower(tags) LIKE ?)"
                params.extend([f"%{token}%", f"%{token}%", f"%{token}%"])
            
        # Execute basic query first
        cursor.execute(sql, params)
        rows = cursor.fetchall()
        
        results = []
        for row in rows:
            p = dict(row)
            p["tags"] = json.loads(p["tags"]) # Deserialize tags
            results.append(p)
            
        # Post-filter for tags (easier than complex SQL for JSON list intersection in basic sqlite)
        if tags:
             results = [
                p for p in results 
                if any(tag.lower() in [t.lower() for t in p["tags"]] for tag in tags)
            ]
            
        # Fallback Logic: If too few results, try broader search (ANY match instead of ALL)
        if len(results) < 1 and query:
             # Broader search
             sql_broad = "SELECT * FROM products WHERE 1=1 AND ("
             params_broad = []
             if category:
                 sql_broad += " category LIKE ? OR"
                 params_broad.append(f"%{category}%")
                 
             tokens = query.lower().split()
             for token in tokens:
                 sql_broad += " lower(name) LIKE ? OR lower(description) LIKE ? OR lower(tags) LIKE ? OR"
                 params_broad.extend([f"%{token}%", f"%{token}%", f"%{token}%"])
             
             # Remove last OR
             if sql_broad.endswith("OR"):
                 sql_broad = sql_broad[:-2]
             
             sql_broad += ")"
             
             # Avoid re-running empty query
             if tokens or category:
                 cursor.execute(sql_broad, params_broad)
                 rows_broad = cursor.fetchall()
                 for row in rows_broad:
                     p = dict(row)
                     p["tags"] = json.loads(p["tags"])
                     # Avoid duplicates if we had some results
                     if not any(r['id'] == p['id'] for r in results):
                         results.append(p)

        conn.close()
        return results[:10] # Limit to top 10 matches to avoid overwhelming LLM

    def get_product_by_id(self, product_id: str) -> Optional[Dict]:
        conn = get_db_connection()
        row = conn.execute("SELECT * FROM products WHERE id = ?", (product_id,)).fetchone()
        conn.close()
        
        if row:
            p = dict(row)
            p["tags"] = json.loads(p["tags"])
            return p
        return None

    def get_recommendations(self, product_id: str) -> List[Dict]:
        target = self.get_product_by_id(product_id)
        if not target:
            return []
        
        # Simple Logic: Same category, different item
        conn = get_db_connection()
        rows = conn.execute(
            "SELECT * FROM products WHERE category = ? AND id != ? LIMIT 3", 
            (target["category"], product_id)
        ).fetchall()
        conn.close()
        
        recs = []
        for row in rows:
            p = dict(row)
            p["tags"] = json.loads(p["tags"])
            recs.append(p)
            
        return recs
