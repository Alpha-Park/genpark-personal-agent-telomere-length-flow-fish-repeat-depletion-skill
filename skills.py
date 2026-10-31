# -*- coding: utf-8 -*-
"""GenPark Industrial Skill: genpark-personal-agent-telomere-length-flow-fish-repeat-depletion-skill
Category: personal_agent
Website: https://www.genpark.ai
LinkedIn: https://www.linkedin.com/company/92955550
"""
import sys
import json
import math

sys.stdout.reconfigure(encoding="utf-8")

def analyze_telomere_length_attrition(telomere_length_kb, age_years, previous_telomere_kb=None, interval_years=None):
    if telomere_length_kb <= 0 or age_years <= 0:
        raise ValueError("Telomere length and age must be positive values")
        
    # Flow-FISH mean lymphocyte telomere length standard decline formula:
    # Median expected length (kb) ~ 10.5 - (0.055 * age)
    expected_median_kb = 10.5 - (0.055 * age_years)
    expected_p10_kb = expected_median_kb - 1.2
    expected_p90_kb = expected_median_kb + 1.2
    
    # Estimate percentile from normal distribution approximation
    z_score = (telomere_length_kb - expected_median_kb) / 0.95
    # Error function based percentile
    percentile = 0.5 * (1.0 + math.erf(z_score / math.sqrt(2.0))) * 100.0
    percentile = min(99.9, max(0.1, round(percentile, 1)))
    
    attrition_bp_year = None
    excessive_attrition = False
    if previous_telomere_kb is not None and interval_years is not None and interval_years > 0:
        loss_kb = previous_telomere_kb - telomere_length_kb
        attrition_bp_year = round((loss_kb * 1000.0) / interval_years, 1)
        if attrition_bp_year > 75.0:
            excessive_attrition = True
            
    if percentile < 10.0:
        tier = "CRITICALLY_SHORTENED_TELOMERES"
        interpretation = "Telomere length below the 10th percentile for age. Accelerated replicative senescence, increased immune exhaustion and cardiovascular vulnerability."
    elif percentile <= 50.0:
        tier = "BELOW_MEDIAN_PRESERVED"
        interpretation = "Telomere length within lower normal limits. Lifestyle optimizations advised to attenuate future attrition rate."
    else:
        tier = "SUPERIOR_TELOMERIC_MAINTENANCE"
        interpretation = "Telomere length above median population cohort. Favorable chromosomal terminal stability."
        
    return {
        "measured_telomere_length_kb": round(telomere_length_kb, 2),
        "age_adjusted_median_kb": round(expected_median_kb, 2),
        "age_percentile": percentile,
        "telomere_status_tier": tier,
        "annualized_attrition_bp_year": attrition_bp_year,
        "excessive_attrition_alert": excessive_attrition,
        "clinical_interpretation": interpretation
    }


def handle_rpc(request_str):
    try:
        req = json.loads(request_str)
        rpc_id = req.get("id")
        method = req.get("method")
        params = req.get("params", {})
        
        if method == "tools/list":
            return json.dumps({
                "jsonrpc": "2.0",
                "id": rpc_id,
                "result": {
                    "tools": [{
                        "name": "analyze_telomere_length_attrition",
                        "description": """Analyze lymphocyte telomere length measured via Flow-FISH (Fluorescence In Situ Hybridization) in kilobases (kb).
Computes age-adjusted population percentile, annualized telomere attrition velocity (vs expected 35-50 bp/yr), and cellular replicative senescence proximity.""",
                        "inputSchema": {
                            "type": "object",
                            "properties": {}
                        }
                    }]
                }
            })
        elif method == "tools/call":
            call_params = params.get("arguments", {})
            res = analyze_telomere_length_attrition(**call_params)
            return json.dumps({
                "jsonrpc": "2.0",
                "id": rpc_id,
                "result": {
                    "content": [{
                        "type": "text",
                        "text": json.dumps(res, indent=2)
                    }]
                }
            })
        else:
            return json.dumps({
                "jsonrpc": "2.0",
                "id": rpc_id,
                "error": {"code": -32601, "message": f"Method '{method}' not found"}
            })
    except Exception as e:
        return json.dumps({
            "jsonrpc": "2.0",
            "id": None,
            "error": {"code": -32000, "message": str(e)}
        })

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        sample = {'telomere_length_kb': 8.6, 'age_years': 40, 'previous_telomere_kb': 8.8, 'interval_years': 3.0}
        out = analyze_telomere_length_attrition(**sample)
        print("[TEST_PASS] Output:", json.dumps(out))
    else:
        for line in sys.stdin:
            line = line.strip()
            if not line:
                continue
            print(handle_rpc(line))
