from agent_tools import CreditCardTools

tools = CreditCardTools()

# Test card name normalization
print("Testing card name mapping:")
print(f"Axis_Atlas -> {tools.normalize_card_name('Axis_Atlas')}")
print(f"HDFC_Infinia -> {tools.normalize_card_name('HDFC_Infinia')}")
print()

# Test calculation with normalized name
print("Testing calculation:")
result = tools.calculate_rewards("Axis_Atlas", 50000, "flights")
print(f"Success: {result['success']}")
if result['success']:
    print(f"Card: {result['card_name']}")
    print(f"Rupee Value: ₹{result['rupee_value']:,.2f}")
else:
    print(f"Error: {result['error']}")

tools.close()
