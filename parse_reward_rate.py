import re

def parse_reward_rate(reward_rate_text: str) -> float:
    """
    Parse text-based reward rate into numerical value.
    
    Examples:
        "5 EDGE Miles per ₹100" -> 5.0
        "3.33 points per ₹100" -> 3.33
        "5% cashback" -> 0.05
        "1 point per ₹200" -> 0.5
        "2X rewards" -> 2.0
    
    Args:
        reward_rate_text: Text description of reward rate
        
    Returns:
        Numerical reward rate (points per rupee)
    """
    
    if not reward_rate_text or reward_rate_text == "Not specified":
        return 0.0
    
    reward_rate_text = reward_rate_text.lower().strip()
    
    # Pattern 1: "X points/miles per ₹Y" or "X points/miles per Y"
    pattern1 = r'(\d+\.?\d*)\s*(?:edge\s*miles|miles|points|reward\s*points?)\s*per\s*₹?(\d+)'
    match = re.search(pattern1, reward_rate_text)
    if match:
        points = float(match.group(1))
        rupees = float(match.group(2))
        return points / rupees
    
    # Pattern 2: "X% cashback" or "X percent"
    pattern2 = r'(\d+\.?\d*)%|(\d+\.?\d*)\s*percent'
    match = re.search(pattern2, reward_rate_text)
    if match:
        percentage = float(match.group(1) or match.group(2))
        return percentage / 100
    
    # Pattern 3: "Xx rewards" or "X times"
    pattern3 = r'(\d+\.?\d*)x|(\d+\.?\d*)\s*times'
    match = re.search(pattern3, reward_rate_text)
    if match:
        multiplier = float(match.group(1) or match.group(2))
        return multiplier
    
    # Pattern 4: Just a number
    pattern4 = r'^(\d+\.?\d*)$'
    match = re.search(pattern4, reward_rate_text)
    if match:
        return float(match.group(1))
    
    # Default: return 0 if can't parse
    print(f"⚠️ Could not parse reward rate: '{reward_rate_text}', returning 0.0")
    return 0.0


def test_parser():
    """Test the reward rate parser"""
    
    test_cases = [
        ("5 EDGE Miles per ₹100", 0.05),
        ("3.33 points per ₹100", 0.0333),
        ("5% cashback", 0.05),
        ("1 point per ₹200", 0.005),
        ("2X rewards", 2.0),
        ("5x", 5.0),
        ("3.3", 3.3),
        ("Not specified", 0.0),
    ]
    
    print("Testing Reward Rate Parser")
    print("=" * 60)
    
    for text, expected in test_cases:
        result = parse_reward_rate(text)
        status = "✓" if abs(result - expected) < 0.0001 else "✗"
        print(f"{status} '{text}' -> {result:.4f} (expected {expected:.4f})")
    
    print("=" * 60)


if __name__ == "__main__":
    test_parser()
