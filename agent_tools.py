import json
from typing import Dict, List, Any
from local_rag_retriever import LocalRAGRetriever
import sqlite3
from config import DB_PATH

class CreditCardTools:
    """Tools for the credit card recommendation agent"""
    
    CARD_NAME_MAPPING = {
        'Axis_Atlas': 'Axis Bank Atlas Credit Card',
        'HDFC_Infinia': 'HDFC Infinia',
        'HDFC_Regalia': 'HDFC Regalia Gold',
        'AmericanExpress_PlatinumTravel': 'American Express Platinum Travel Credit Card',
        'HDFC_DCB': 'HDFC Diners Club Black',
        'SBI_Cashback': 'SBI Cashback Credit Card'
    }
    
    def __init__(self):
        self.retriever = LocalRAGRetriever()
        self.db_path = DB_PATH
    
    def normalize_card_name(self, card_name: str) -> str:
        """Normalize card name from chunks to database format"""
        return self.CARD_NAME_MAPPING.get(card_name, card_name)
    
    def retrieve_card_rules(self, query: str, card_name: str = None, top_k: int = 5) -> Dict[str, Any]:
        """
        Retrieve relevant card rules and context from vector DB and SQLite.
        
        Args:
            query: User query or spend category
            card_name: Optional specific card name to filter
            top_k: Number of chunks to retrieve
            
        Returns:
            Dictionary with context_chunks, reward_rules, and cards_involved
        """
        try:
            result = self.retriever.hybrid_retrieve(query, card_name=card_name, top_k=top_k)
            return {
                "success": True,
                "data": result,
                "error": None
            }
        except Exception as e:
            return {
                "success": False,
                "data": None,
                "error": str(e)
            }
    
    def calculate_rewards(self, card_name: str, spend_amount: float, spend_category: str) -> Dict[str, Any]:
        """
        Calculate rewards for a specific card, amount, and category.
        
        Args:
            card_name: Name of the credit card
            spend_amount: Amount to be spent
            spend_category: Category of spend (e.g., 'flights', 'hotels', 'dining')
            
        Returns:
            Dictionary with reward calculation details
        """
        try:
            normalized_card_name = self.normalize_card_name(card_name)
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            query = """
                SELECT reward_rate, monthly_cap, exclusions, conditions
                FROM reward_rules
                WHERE card_name = ? AND spend_category = ?
            """
            cursor.execute(query, (normalized_card_name, spend_category))
            result = cursor.fetchone()
            
            if not result:
                query_general = """
                    SELECT reward_rate, monthly_cap, exclusions, conditions
                    FROM reward_rules
                    WHERE card_name = ? AND spend_category = 'general'
                """
                cursor.execute(query_general, (normalized_card_name,))
                result = cursor.fetchone()
            
            conn.close()
            
            if result:
                reward_rate, monthly_cap, exclusions, conditions = result
                
                base_points = spend_amount * reward_rate
                
                if monthly_cap and base_points > monthly_cap:
                    capped_points = monthly_cap
                    is_capped = True
                else:
                    capped_points = base_points
                    is_capped = False
                
                point_value = 0.5 # convert point to ruppe using estimation 1 point = 0.5 rupees
                rupee_value = capped_points * point_value
                
                return {
                    "success": True,
                    "card_name": normalized_card_name,
                    "spend_amount": spend_amount,
                    "spend_category": spend_category,
                    "reward_rate": reward_rate,
                    "base_points": base_points,
                    "final_points": capped_points,
                    "is_capped": is_capped,
                    "monthly_cap": monthly_cap,
                    "rupee_value": rupee_value,
                    "point_value_assumption": point_value,
                    "exclusions": exclusions,
                    "conditions": conditions,
                    "error": None
                }
            else:
                return {
                    "success": False,
                    "error": f"No reward rule found for {normalized_card_name} in category {spend_category}"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def compare_cards(self, calculations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Compare multiple card calculations and rank them.
        
        Args:
            calculations: List of calculation results from calculate_rewards
            
        Returns:
            Ranked list of cards with comparison details
        """
        try:
            valid_calcs = [c for c in calculations if c.get("success", False)]
            
            if not valid_calcs:
                return {
                    "success": False,
                    "error": "No valid calculations to compare"
                }
            
            sorted_calcs = sorted(valid_calcs, key=lambda x: x.get("rupee_value", 0), reverse=True)
            
            best_card = sorted_calcs[0]
            
            comparison = {
                "success": True,
                "best_card": best_card["card_name"],
                "best_value": best_card["rupee_value"],
                "rankings": [
                    {
                        "rank": i + 1,
                        "card_name": calc["card_name"],
                        "rupee_value": calc["rupee_value"],
                        "points": calc["final_points"],
                        "is_capped": calc.get("is_capped", False)
                    }
                    for i, calc in enumerate(sorted_calcs)
                ],
                "all_calculations": sorted_calcs
            }
            
            return comparison
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_all_cards(self) -> List[str]:
        """Get list of all available cards from database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT DISTINCT card_name FROM reward_rules")
            cards = [row[0] for row in cursor.fetchall()]
            conn.close()
            return cards
        except Exception as e:
            print(f"Error getting cards: {e}")
            return []
    
    def get_user_cards(self, user_id: str = None) -> List[str]:
        """Get cards owned by user (placeholder for now)"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='user_profiles'")
            table_exists = cursor.fetchone()
            
            if table_exists and user_id:
                cursor.execute("SELECT cards_owned FROM user_profiles WHERE user_id = ?", (user_id,))
                result = cursor.fetchone()
                if result and result[0]:
                    cards = json.loads(result[0])
                    conn.close()
                    return cards
            
            conn.close()
            return self.get_all_cards()
            
        except Exception as e:
            print(f"Error getting user cards: {e}")
            return self.get_all_cards()
    
    def close(self):
        """Close retriever connection"""
        if self.retriever:
            self.retriever.close()
