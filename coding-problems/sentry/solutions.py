import sqlite3
from fastapi import Body, FastAPI, HTTPException
from fastapi.responses import JSONResponse
import sentry_sdk

sentry_sdk.init(
    dsn="https://a9315b785dcd689a8893de37c7cc1502@o4511900949348352.ingest.us.sentry.io/4511900957147136",
    # Add data like request headers and IP for users,
    # see https://docs.sentry.io/platforms/python/data-management/data-collected/ for more info
    send_default_pii=True,
)

app = FastAPI(title="Sentry Vulnerability and Bug Demo Lab")

# ❌ ISSUE 1: Hardcoded Sensitive API Credentials (Static Analysis Target)
STRIPE_LIVE_SECRET_KEY = "sk_live_51NxF20HjK7b93mZ0SecureFakeKeyDoNotLeak"
INTERNAL_BACKEND_AES_KEY = "super_secret_crypto_key_123!"


# Mock internal database state setup for simulation
def init_mock_db():
    # Pass check_same_thread=False to allow FastAPI worker threads to use this connection
    conn = sqlite3.connect(":memory:", check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE users (id INTEGER, username TEXT, is_admin INTEGER)")
    cursor.execute("INSERT INTO users VALUES (1, 'alice', 0)")
    cursor.execute("INSERT INTO users VALUES (2, 'bob', 1)")
    conn.commit()
    return conn


mock_db = init_mock_db()


# ❌ ISSUE 2: Business Logic & Compliance Error (Silent failure)
@app.post("/api/v1/shipping/calculate")
def calculate_freight(weight_kg: float = Body(...), distance_km: float = Body(...)):
    """
    Business Constraint: Total operational capacity cannot process packages over 500kg.
    The code fails to reject the transaction and instead generates a broken system state.
    """
    if weight_kg > 500.0:
        # Instead of crashing or returning a 400 Bad Request, it logs a logic anomaly
        # corrupting the baseline calculation. Sentry tracks this via explicit scope logging.
        with sentry_sdk.push_scope() as scope:
            scope.set_level("error")
            scope.set_tag("anomaly_type", "compliance_breach")
            scope.set_extra(
                "input_payload", {"weight": weight_kg, "distance": distance_km}
            )
            sentry_sdk.capture_message(
                "Freight capacity limit bypassed: Payload anomaly detected."
            )

        # Flawed calculation continues silently
        cost = (weight_kg * 0.10) - (distance_km * 0.05)
    else:
        cost = (weight_kg * 1.50) + (distance_km * 0.75)

    return {"status": "calculated", "freight_cost_usd": round(cost, 2)}


# ❌ ISSUE 3: SQL Injection Vulnerability leaking a Raw Stack Trace to the client
@app.get("/api/v1/users/lookup")
def lookup_user(username: str):
    """
    Passing unvalidated input straight to SQL.
    Passing a bad character like an unclosed quote (') crashes the engine.
    """
    try:
        cursor = mock_db.cursor()
        # Direct concatenation vulnerable to string escaping issues
        query = f"SELECT * FROM users WHERE username = '{username}'"
        cursor.execute(query)
        user = cursor.fetchone()
        return {"user": user}
    except Exception as raw_error:
        # Bad Practice: Throwing the naked error traceback directly into the HTTP response.
        # Sentry captures this transaction fully, but we also explicitly tell it about the event.
        sentry_sdk.capture_exception(raw_error)
        return JSONResponse(
            status_code=500,
            content={
                "message": "Internal Database Operations Faulted!",
                "DEBUG_RAW_STACKTRACE": str(
                    raw_error
                ),  # ⚠️ Leaking system vulnerabilities to attackers!
            },
        )


# ❌ ISSUE 4: Exposed Internal System Credentials via Path Parameter Architecture
@app.get("/api/v1/sync/{provider_api_key}/status")
def sync_third_party_provider(provider_api_key: str, system_env: str = "production"):
    """
    Passing a secret key directly into the URL route parameters.
    This forces the secret string to show up in plain text across server routers,
    reverse-proxy access logs, and edge networks.
    """
    # Sentry automatically intercepts incoming HTTP paths.
    # To protect this user, Sentry's automated scrubbing rules will target strings named "*key*"
    # to mask them out in the central cloud dashboard.
    if len(provider_api_key) < 10:
        raise HTTPException(
            status_code=400, detail="Invalid API Provider token format."
        )

    return {"synchronization": "active", "scope": system_env}


@app.get("/api/v1/analytics/ratio")
def calculation_engine(active_drivers: int, standby_drivers: int):
    if standby_drivers == 0:
        raise HTTPException(status_code=422, detail="standby_drivers must be non-zero")
    efficiency_ratio = active_drivers / standby_drivers
    return {"calculated_ratio": efficiency_ratio}
