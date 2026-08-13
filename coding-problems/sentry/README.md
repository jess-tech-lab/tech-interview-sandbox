# 1. Set up the environment

```bash
pip install -r requirements.txt
uvicorn solutions:app --reload
```

# 2. Integrate Sentry in the code

```bash

sentry_sdk.init(
    dsn="https://a9315b785dcd689a8893de37c7cc1502@o4511900949348352.ingest.us.sentry.io/4511900957147136",
    # Add data like request headers and IP for users,
    # see https://docs.sentry.io/platforms/python/data-management/data-collected/ for more info
    send_default_pii=True,
)
```

For issues like crashes, Sentry notifies automatically. Otherwise, can use `sentry_sdk.capture_message()` and `sentry_sdk.capture_exception()`.

Open a browser then send a request like

```
http://127.0.0.1:8000/api/v1/sync/1234567890/status
http://127.0.0.1:8000/api/v1/analytics/ratio?active_drivers=10&standby_drivers=0

```

Sentry will send an email and log the divide-by-zero error in console

[sentry_error](sentry_divide_0_error.png)
