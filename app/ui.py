def header(body: str) -> str:
    return f"""\
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <script type="module" src="https://cdn.jsdelivr.net/gh/starfederation/datastar@v1.0.0-RC.7/bundles/datastar.js"></script>
  <link rel="stylesheet" href="/static/output.css">
  
  <title>Document</title>
</head>
<body>
  {body} 
</body>
</html>
    """

def root_body():
    return f""" \
        <div class="container">
              <h1 class="text-3xl font-bold underline text-red-200"> Hello world! </h1>
            <div
            class="time"
            data-init="@get('/updates')"
            >
            Current time from element: <span id="currentTime">CURRENT_TIME</span>
            </div>
            <div
            class="time"
            >
            Current time from signal: <span data-text="$currentTime">CURRENT_TIME</span>
            </div>
            <div> 
              <button data-on:click="@get('/show-msg')">
                Show me the Message!
              </button>
              <p id='msg'> </p>
            </div>
        </div>
    """