from typing import List, Dict, Any, Optional
from ..profiles.loader import ProfileLoader
import re

class RecommendationEngine:
    """
    Local Rule-Based Recommendation Engine.
    Analyzes system context to suggest profiles without AI.
    """
    def __init__(self):
        self.loader = ProfileLoader()

    def recommend_profiles(self, audit_data: Dict, identity_data: Dict, machine_data: Dict) -> List[Dict]:
        recommendations = []
        profiles = []
        
        # Load all available profiles
        for name in self.loader.list_profiles():
            p = self.loader.load_profile(name)
            if p:
                profiles.append(p)
                
        # Context Extraction
        ram_gb = audit_data.get('ram_total_gb', 0)
        role = identity_data.get('role', '').lower()
        level = identity_data.get('level', 'beginner').lower()
        machine_type = machine_data.get('type', 'laptop').lower()
        machine_power = machine_data.get('power', 'mid').lower()
        
        for p in profiles:
            score = 50 # Base score
            reasons = []
            warnings = []
            
            # --- Rule 1: Hardware Constraints (RAM) ---
            if p.tier == 'full':
                if ram_gb < 8:
                    score -= 30
                    warnings.append(f"Low RAM ({ram_gb}GB) for Full tier")
                elif ram_gb >= 16:
                    score += 10
                    reasons.append("High RAM available for Full tier")
            
            # --- Rule 2: Machine Type (Server vs GUI) ---
            # Assume 'browsers' or explicit 'gui' tag means GUI needed
            is_gui_profile = 'browsers' in p.tags or 'gui' in p.tags or 'desktop' in p.tags
            if machine_type == 'server' and is_gui_profile:
                score -= 40
                warnings.append("Server machine typically doesn't need GUI apps")
                
            # --- Rule 3: User Role Matching ---
            # Simple keyword matching in tags or name
            if role in p.tags or role in p.name:
                score += 25
                reasons.append(f"Matches your role: {role}")
            
            # --- Rule 4: Skill Level & Tier ---
            if level == 'beginner' and p.tier == 'full':
                score -= 10
                warnings.append("Full tier might be overwhelming for beginners")
            elif level == 'pro' and p.tier == 'lite':
                score -= 5
                reasons.append("Lite tier might lack advanced tools")
            elif level == 'pro' and p.tier == 'full':
                score += 10
                reasons.append("Full tier matches Pro level")

            # --- Rule 5: Power Profile ---
            if machine_power == 'low' and p.tier == 'full':
                score -= 15
                warnings.append("Heavy profile for low-power machine")

            # Normalize Score
            score = max(0, min(100, score))
            
            recommendations.append({
                "profile": p.name,
                "tier": p.tier,
                "score": score,
                "reasons": reasons,
                "warnings": warnings,
                "tags": p.tags
            })
            
        # Sort by score desc
        recommendations.sort(key=lambda x: x['score'], reverse=True)
        return recommendations

    def recommend_packages(self, audit_data: Dict, identity_data: Dict) -> List[Dict]:
        return [] # TODO: Implement granular package recommendations
