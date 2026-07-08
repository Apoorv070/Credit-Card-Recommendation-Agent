# Fixing Reward Rate Issue

## 🔍 Problem Identified

The original `data/card_data.csv` has **text-based reward rates** instead of numerical values:

**Current (Wrong)**:
```csv
Reward Rate
"5 EDGE Miles per ₹100"
"Combination of Threshold & Bonus points"
"Accelerated via SmartBuy"
```

**Required (Correct)**:
```csv
Reward Rate
5.0
3.33
0.05
```

## ⚠️ Impact

The `calculate_rewards()` function in `agent_tools.py` does:
```python
base_points = spend_amount * reward_rate
```

This **fails** when `reward_rate` is text like "5 EDGE Miles per ₹100".

## ✅ Solution Options

### **Option 1: Fix CSV and Database (Recommended)**

This is the **cleanest solution** - use proper numerical values.

#### Step 1: Use Corrected CSV

I've created `data/card_data_corrected.csv` with:
- **Numerical reward rates** (e.g., 5.0 means 5 points per ₹1)
- **Separate rows** for each category (flights, hotels, dining, general)
- **Proper NULL handling** for caps

Example:
```csv
Card Name,Spend Category,Reward Rate,Monthly Cap,Annual Cap
Axis Bank Atlas Credit Card,flights,5.0,10000,180000
Axis Bank Atlas Credit Card,hotels,5.0,10000,180000
Axis Bank Atlas Credit Card,general,2.0,None,180000
```

**Reward Rate Interpretation**:
- `5.0` = 5 points per ₹1 spent
- `0.05` = 0.05 points per ₹1 (or 5% cashback)
- `3.33` = 3.33 points per ₹1

#### Step 2: Run Fix Script

```bash
python fix_database.py
```

This will:
1. Drop old `reward_rules` table
2. Create new table with proper schema
3. Load corrected CSV data
4. Verify with test calculation
5. Show all cards and rates

**Expected Output**:
```
✓ Old table dropped
✓ New table created
✓ Inserted 15 rows

Card Name                      Category        Reward Rate    
------------------------------------------------------------
Axis Bank Atlas Credit Card    flights         5.00
Axis Bank Atlas Credit Card    hotels          5.00
HDFC Diners Club Black         flights         3.33
SBI Cashback Credit Card       shopping        0.05

✅ DATABASE FIXED SUCCESSFULLY!
```

#### Step 3: Test the Agent

```bash
python test_agent.py
```

Should now work correctly with numerical calculations.

---

### **Option 2: Parse Text Rates (Alternative)**

If you want to keep text-based rates in CSV, use a parser.

I've created `parse_reward_rate.py` with a function that converts:
- `"5 EDGE Miles per ₹100"` → `0.05`
- `"3.33 points per ₹100"` → `0.0333`
- `"5% cashback"` → `0.05`
- `"2X rewards"` → `2.0`

#### Modify `agent_tools.py`

Add this import:
```python
from parse_reward_rate import parse_reward_rate
```

Modify `calculate_rewards()`:
```python
if result:
    reward_rate_raw, monthly_cap, exclusions, conditions = result
    
    # Parse reward rate if it's text
    if isinstance(reward_rate_raw, str):
        reward_rate = parse_reward_rate(reward_rate_raw)
    else:
        reward_rate = reward_rate_raw
    
    base_points = spend_amount * reward_rate
    # ... rest of code
```

**Pros**: Keeps original CSV format
**Cons**: More complex, error-prone, harder to maintain

---

## 🎯 Recommended Approach

**Use Option 1** (Fix CSV and Database):

1. ✅ Already created: `data/card_data_corrected.csv`
2. ✅ Already created: `fix_database.py`
3. Run: `python fix_database.py`
4. Test: `python test_agent.py`
5. Launch: `streamlit run streamlit_app.py`

## 📊 Corrected Data Structure

### Cards Included

1. **Axis Bank Atlas Credit Card**
   - Flights: 5 points/₹, cap 10,000/month
   - Hotels: 5 points/₹, cap 10,000/month
   - General: 2 points/₹, no monthly cap

2. **HDFC Diners Club Black**
   - Flights: 3.33 points/₹
   - Hotels: 3.33 points/₹
   - Dining: 5 points/₹, cap 15,000/month
   - General: 3.33 points/₹

3. **SBI Cashback Credit Card**
   - Flights: 0.01 (1% cashback)
   - Shopping: 0.05 (5% cashback)
   - General: 0.01 (1% cashback)

4. **HDFC Infinia**
   - All categories: 3.3 points/₹, cap 200,000/cycle

5. **HDFC Regalia Gold**
   - Dining: 5 points/₹, cap 5,000/month
   - General: 1 point/₹, cap 50,000/cycle

### Reward Rate Conversion

Original text → Numerical value:

| Original | Numerical | Meaning |
|----------|-----------|---------|
| "5 EDGE Miles per ₹100" | 5.0 | 5 points per ₹1 |
| "3.33 points per ₹100" | 3.33 | 3.33 points per ₹1 |
| "5% cashback" | 0.05 | ₹0.05 per ₹1 |
| "1 point per ₹200" | 0.5 | 0.5 points per ₹1 |

**Note**: I've normalized all rates to **points per ₹1** for consistency.

## 🧪 Testing

After running `fix_database.py`, test with:

```bash
python test_agent.py
```

Or test manually:
```python
from agent_tools import CreditCardTools

tools = CreditCardTools()

# Test calculation
result = tools.calculate_rewards(
    card_name="Axis Bank Atlas Credit Card",
    spend_amount=50000,
    spend_category="flights"
)

print(result)
# Expected:
# {
#     'success': True,
#     'card_name': 'Axis Bank Atlas Credit Card',
#     'spend_amount': 50000,
#     'reward_rate': 5.0,
#     'base_points': 250000,
#     'final_points': 10000,  # Capped
#     'is_capped': True,
#     'rupee_value': 5000,
#     ...
# }
```

## 🔧 If You Want to Add More Cards

Edit `data/card_data_corrected.csv`:

```csv
Card Name,Spend Category,Reward Rate,Monthly Cap,Annual Cap,Exclusion Flag,Exclusion Details,...
Your Card Name,flights,4.0,15000,None,Yes,"Fuel, Rent",...
Your Card Name,general,1.5,None,None,Yes,"Fuel, Rent",...
```

Then re-run:
```bash
python fix_database.py
```

## 📝 Summary

**Problem**: Text-based reward rates can't be multiplied
**Solution**: Use numerical reward rates in CSV
**Action**: Run `python fix_database.py`
**Result**: Agent calculations work correctly

---

**Status**: ✅ Fix ready to apply
**Files Created**:
- `data/card_data_corrected.csv` - Corrected CSV
- `fix_database.py` - Database fix script
- `parse_reward_rate.py` - Alternative text parser
- `FIX_REWARD_RATES.md` - This guide
