HEAD = """
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Outfit:wght@400..700&display=swap" rel="stylesheet">
<style>
html,body{margin:0;background:#000;color:#f4f4f2;font-family:Outfit,"Helvetica Neue",Arial,system-ui,sans-serif;-webkit-font-smoothing:antialiased}
.bar{display:flex;flex-wrap:wrap;justify-content:center;gap:8px 28px;padding:34px 20px 0;font-size:12px;font-weight:500;letter-spacing:.16em;text-transform:uppercase}
.bar a{color:#f4f4f2;text-decoration:none}.bar a:hover{color:#c9f542}
.head{max-width:1200px;margin:0 auto;padding:clamp(48px,8vw,110px) 20px 24px}
.head h1{margin:0;font-weight:650;font-size:clamp(46px,9vw,140px);line-height:.95;letter-spacing:-.05em}
.head p{max-width:36em;margin:28px 0 0;color:#d6d6d2;font-size:18px;line-height:1.55}
.head code{font:400 15px ui-monospace,Menlo,monospace;color:#c9f542}
.swagger-ui{font-family:inherit}
.swagger-ui .wrapper{max-width:1200px;padding:0 20px}
.swagger-ui .info,.swagger-ui .scheme-container{display:none}
.swagger-ui *{color:#f4f4f2!important;font-family:inherit}
.swagger-ui svg{fill:#f4f4f2}
.swagger-ui a:not(.nostyle){color:#c9f542!important}
.swagger-ui .opblock-summary-description,.swagger-ui .parameter__type,.swagger-ui .parameter__in,.swagger-ui .prop-type{color:#8d8d89!important}
.swagger-ui .parameter__name.required span,.swagger-ui .parameter__name.required:after{color:#ff5b49!important}
.swagger-ui .opblock-tag{padding:30px 0 14px;font-size:24px;font-weight:500;border-bottom:1px solid #242422}
.swagger-ui .opblock{margin:0 0 12px;border:1px solid #3a3a37;border-radius:0;background:#000;box-shadow:none}
.swagger-ui .opblock.opblock-post{border-color:#c9f542;background:rgba(201,245,66,.04)}
.swagger-ui .opblock .opblock-summary{border-bottom:0}
.swagger-ui .opblock .opblock-summary-method{min-width:84px;border-radius:0;background:#f4f4f2;color:#000!important;font-weight:600}
.swagger-ui .opblock.opblock-post .opblock-summary-method{background:#c9f542}
.swagger-ui .opblock .opblock-summary-path{font-weight:500}
.swagger-ui .opblock .opblock-section-header{background:#0b0b0b;box-shadow:none;border-bottom:1px solid #242422}
.swagger-ui .opblock-body pre.microlight,.swagger-ui .highlight-code>.microlight{background:#0b0b0b!important;border:1px solid #242422;border-radius:0}
.swagger-ui input[type=text],.swagger-ui input[type=password],.swagger-ui input[type=search],.swagger-ui select,.swagger-ui textarea{background:#000;border:1px solid #3a3a37;border-radius:0;box-shadow:none}
.swagger-ui textarea.curl{background:#0b0b0b}
.swagger-ui table thead tr th,.swagger-ui table thead tr td{border-bottom:1px solid #242422}
.swagger-ui .btn{border:1px solid #f4f4f2;border-radius:0;background:transparent;box-shadow:none;font-weight:500}
.swagger-ui .btn.execute{background:#c9f542;border-color:#c9f542;color:#000!important}
.swagger-ui .btn.cancel{border-color:#ff5b49}
.swagger-ui .responses-inner,.swagger-ui .opblock-body .opblock-description-wrapper{background:transparent}
</style>
"""

TOP = """
<nav class="bar">
<a href="https://mayank-gupta-develop.github.io/llm-eval-harness/">LLM Eval Harness</a>
<a href="https://mayank-gupta-develop.github.io/llm-eval-harness/#try">Try it</a>
<a href="/openapi.json">OpenAPI JSON</a>
<a href="https://github.com/mayank-gupta-develop/llm-eval-harness">Source</a>
</nav>
<header class="head">
<h1>API reference</h1>
<p>Reading is open. Creating test cases and runs needs an <code>x-api-key</code> header. The demo endpoint needs no key and runs the two string scorers. On the free tier, the first request after a quiet spell can take up to a minute.</p>
</header>
"""
