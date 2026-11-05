import os
import sys
import uvicorn

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    print("==================================================")
    print(" CareConnect AI -- Healthcare Assistance Agent")
    print(f" Server starting on port {port}")
    print(" Guardrails: NON-DIAGNOSTIC & NON-PRESCRIPTION ACTIVE")
    print("==================================================")
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=False)
