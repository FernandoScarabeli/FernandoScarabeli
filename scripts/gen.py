"""Gera os SVGs do README (versões dark e light).

Uso: python3 scripts/gen.py  ->  escreve em assets/
"""
import re
from html import escape
from pathlib import Path


def nbsp(svg):
    """Troca espaços dos nós de texto por U+00A0 para o alinhamento monoespaçado não colapsar."""
    return re.sub(r">([^<]+)<", lambda m: ">" + m.group(1).replace(" ", " ") + "<", svg)

OUT = Path(__file__).resolve().parent.parent / "assets"
OUT.mkdir(exist_ok=True)

MONO = "ui-monospace, SFMono-Regular, 'SF Mono', Menlo, Consolas, 'Liberation Mono', monospace"
SANS = "-apple-system, BlinkMacSystemFont, 'Segoe UI', 'Noto Sans', Helvetica, Arial, sans-serif"

THEMES = {
    "dark": dict(
        win="#0d1117", bar="#161b22", border="#30363d", fg="#e6edf3", dim="#7d8590",
        green="#3fb950", yellow="#d29922", cyan="#39c5cf", blue="#58a6ff",
        spring="#6db33f", purple="#bc8cff", card="#0d1117", code="#161b22", tint=0.12,
    ),
    "light": dict(
        win="#ffffff", bar="#f6f8fa", border="#d0d7de", fg="#1f2328", dim="#656d76",
        green="#1a7f37", yellow="#9a6700", cyan="#1b7c83", blue="#0969da",
        spring="#4e8a2a", purple="#8250df", card="#ffffff", code="#f6f8fa", tint=0.10,
    ),
}

W = 900

# ---------------------------------------------------------------------------
# 1. Header: terminal com o boot do Spring
# ---------------------------------------------------------------------------

FIGLET = {
    "S": [" ____  ", "/ ___| ", "\\___ \\ ", " ___) |", "|____/ "],
    "C": ["  ____ ", " / ___|", "| |    ", "| |___ ", " \\____|"],
    "A": ["    _    ", "   / \\   ", "  / _ \\  ", " / ___ \\ ", "/_/   \\_\\"],
    "R": [" ____  ", "|  _ \\ ", "| |_) |", "|  _ < ", "|_| \\_\\"],
    "B": [" ____  ", "| __ ) ", "|  _ \\ ", "| |_) |", "|____/ "],
    "E": [" _____ ", "| ____|", "|  _|  ", "| |___ ", "|_____|"],
    "L": [" _     ", "| |    ", "| |    ", "| |___ ", "|_____|"],
    "I": [" ___ ", "|_ _|", " | | ", " | | ", "|___|"],
}


def figlet(word):
    return ["".join(FIGLET[c][i] for c in word) for i in range(5)]


LOGS = [
    # (atraso em s, nível, classe, mensagem, destaque?)
    (0.00, "INFO", "FernandoApplication", "Starting FernandoApplication using Java 17", False),
    (0.30, "INFO", "ProfileResolver", 'Active profiles: "backend", "ufla-si"', False),
    (0.25, "INFO", "StackAutoConfiguration", "Loaded Spring Boot, Security, JWT, JPA, Flyway", False),
    (0.55, "INFO", "HikariPool", "HikariPool-1 - Added connection to PostgreSQL", False),
    (0.30, "INFO", "FlywayExecutor", 'Schema "fernando" is up to date', False),
    (0.35, "INFO", "RabbitAdmin", "Connected to RabbitMQ, declared 4 queues", False),
    (0.30, "INFO", "GatewayRouteLocator", "Routed /api/** to 5 microservices via BFFs", False),
    (0.25, "INFO", "HealthEndpoint", "Liveness & readiness probes: UP", False),
    (0.25, "INFO", "CodeReviewFilter", "Reviews, tests & docs required before merge", False),
    (0.30, "INFO", "RequestMappingHandler", "Mapped GET /stack, GET /projects, POST /contact", False),
    (0.40, "WARN", "CoffeeHealthIndicator", "Coffee level below 20%, refill recommended", False),
    (0.35, "INFO", "TomcatWebServer", "Tomcat started on port 8080 (http)", False),
    (0.30, "INFO", "FernandoApplication", "Started FernandoApplication in 4.291 seconds", True),
]


def header(t):
    fs, lh, cw = 13.5, 20, 8.15  # fonte, altura de linha, largura estimada do caractere
    x0, top = 24, 36 + 26
    rows = []  # (y, conteúdo svg, instante em que aparece)
    y = top
    t_now = 0.0

    # prompt digitado
    cmd = "./mvnw spring-boot:run"
    type_start, per_char = 0.5, 0.045
    steps = ";".join(str(round((i) * cw, 1)) for i in range(len(cmd) + 1))
    n = len(cmd) + 1
    key_times = ";".join(str(round(i / n, 4)) for i in range(n))
    prompt = (
        f'<text x="{x0}" y="{y}"><tspan fill="{t["green"]}">❯</tspan> '
        f'<tspan fill="{t["blue"]}">~/profile</tspan> </text>'
        f'<clipPath id="type"><rect x="{x0 + 12 * cw}" y="{y - 15}" height="20" width="0">'
        f'<animate attributeName="width" values="{steps}" keyTimes="{key_times}" calcMode="discrete" '
        f'begin="{type_start}s" dur="{len(cmd) * per_char:.2f}s" fill="freeze"/></rect></clipPath>'
        f'<text x="{x0 + 12 * cw}" y="{y}" clip-path="url(#type)" fill="{t["fg"]}">{escape(cmd)}</text>'
    )
    rows.append((y, prompt, None))
    t_now = type_start + len(cmd) * per_char + 0.35
    y += lh * 2

    # banner
    banner = figlet("SCARABELI")
    for i, line in enumerate(banner):
        rows.append((y, f'<text x="{x0}" y="{y}" fill="{t["spring"]}" font-weight="700" font-size="18">{escape(line)}</text>', t_now))
        y += 22
    ver = " :: Fernando Scarabeli ::        (v2026.11 · Java 17 · Spring Boot 3)"
    rows.append((y + 4, f'<text x="{x0}" y="{y + 4}"><tspan fill="{t["green"]}">{escape(ver[:26])}</tspan>'
                 f'<tspan fill="{t["dim"]}">{escape(ver[26:])}</tspan></text>', t_now + 0.15))
    y += lh * 2 + 4
    t_now += 0.6

    # logs
    clock = [10, 0, 0, 112]
    for delay, lvl, cls, msg, hl in LOGS:
        t_now += delay
        clock[3] += int(delay * 1000) + 37
        clock[2] += clock[3] // 1000
        clock[3] %= 1000
        ts = f"10:00:{clock[2]:02d}.{clock[3]:03d}"
        lvl_color = t["yellow"] if lvl == "WARN" else t["green"]
        msg_color = t["green"] if hl else t["fg"]
        weight = ' font-weight="700"' if hl else ""
        content = (
            f'<text x="{x0}" y="{y}">'
            f'<tspan fill="{t["dim"]}">{ts}</tspan>  '
            f'<tspan fill="{lvl_color}" font-weight="700">{lvl} </tspan> '
            f'<tspan fill="{t["dim"]}">[main]</tspan> '
            f'<tspan fill="{t["cyan"]}">{cls:<22}</tspan>'
            f'<tspan fill="{t["dim"]}"> : </tspan>'
            f'<tspan fill="{msg_color}"{weight}>{escape(msg)}</tspan></text>'
        )
        rows.append((y, content, t_now))
        y += lh

    # prompt final com cursor piscando
    t_now += 0.5
    y += lh
    final = (
        f'<text x="{x0}" y="{y}"><tspan fill="{t["green"]}">❯</tspan> '
        f'<tspan fill="{t["blue"]}">~/profile</tspan> </text>'
        f'<rect x="{x0 + 12 * cw}" y="{y - 13}" width="8" height="16" fill="{t["fg"]}">'
        f'<animate attributeName="opacity" values="1;0" dur="1s" calcMode="discrete" '
        f'repeatCount="indefinite" begin="{t_now:.2f}s"/></rect>'
    )
    rows.append((y, final, t_now))
    height = y + 26

    body = []
    for _, content, at in rows:
        if at is None:
            body.append(content)
        else:
            body.append(f'<g opacity="0"><set attributeName="opacity" to="1" begin="{at:.2f}s" fill="freeze"/>{content}</g>')

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{height}" viewBox="0 0 {W} {height}" role="img" aria-label="Spring Boot style boot log of Fernando Scarabeli: backend developer, Java 17, Spring Boot">
<rect x="0.5" y="0.5" width="{W - 1}" height="{height - 1}" rx="10" fill="{t["win"]}" stroke="{t["border"]}"/>
<path d="M0.5 36 V10.5 a10 10 0 0 1 10 -10 H{W - 10.5} a10 10 0 0 1 10 10 V36 Z" fill="{t["bar"]}"/>
<line x1="0.5" y1="36" x2="{W - 0.5}" y2="36" stroke="{t["border"]}"/>
<circle cx="20" cy="18" r="6" fill="#ff5f57"/><circle cx="40" cy="18" r="6" fill="#febc2e"/><circle cx="60" cy="18" r="6" fill="#28c840"/>
<text x="{W / 2}" y="22.5" text-anchor="middle" font-family="{SANS}" font-size="12.5" fill="{t["dim"]}">fernando@ufla: ~/profile — java</text>
<g font-family="{MONO}" font-size="{fs}" xml:space="preserve" style="white-space:pre">
{nbsp(chr(10).join(body))}
</g>
</svg>
'''


# ---------------------------------------------------------------------------
# 2. Card estilo Swagger UI
# ---------------------------------------------------------------------------

METHODS = {"GET": "#61affe", "POST": "#49cc90", "DELETE": "#f93e3e"}


def swagger_top(t):
    h = 132
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{h}" viewBox="0 0 {W} {h}" role="img" aria-label="Fernando Scarabeli API, version 1.0.0">
<g font-family="{SANS}">
<text x="2" y="40" font-size="30" font-weight="700" fill="{t["fg"]}">Fernando Scarabeli API</text>
<rect x="352" y="17" width="48" height="20" rx="10" fill="#7d8492"/>
<text x="376" y="31.5" text-anchor="middle" font-size="11.5" font-weight="700" fill="#fff">1.0.0</text>
<rect x="406" y="17" width="58" height="20" rx="10" fill="#89bf04"/>
<text x="435" y="31.5" text-anchor="middle" font-size="11.5" font-weight="700" fill="#fff">OAS 3.1</text>
<text x="2" y="68" font-size="14" fill="{t["blue"]}" font-family="{MONO}">https://github.com/FernandoScarabeli</text>
<text x="2" y="98" font-size="15" fill="{t["fg"]}">Backend developer · <tspan font-weight="700">Java</tspan> &amp; <tspan font-weight="700">Spring Boot</tspan> · Information Systems @ <tspan font-weight="700">UFLA</tspan> · Lavras, MG</text>
<text x="2" y="121" font-size="13" fill="{t["dim"]}">Click an endpoint to try it out.</text>
</g>
</svg>
'''


def hex_rgba(color, a):
    c = color.lstrip("#")
    r, g, b = (int(c[i:i + 2], 16) for i in (0, 2, 4))
    return f"rgba({r},{g},{b},{a})"


def endpoint_head(t, method, path, summary, status=None, y=4, expanded=False):
    c = METHODS[method]
    status_svg = ""
    if status:
        code, label = status
        status_svg = (
            f'<text x="{W - 52}" y="{y + 25}" text-anchor="end" font-family="{MONO}" font-size="13" '
            f'font-weight="700" fill="{c}">{code} <tspan fill="{t["dim"]}" font-weight="400">{label}</tspan></text>'
        )
    chevron = (
        f'<path d="M{W - 34} {y + 17} l6 6 l6 -6" fill="none" stroke="{t["fg"]}" stroke-width="2" '
        f'transform="{"rotate(180 %d %d)" % (W - 28, y + 20) if expanded else ""}"/>'
    )
    return (
        f'<rect x="6" y="{y + 5}" width="76" height="30" rx="3" fill="{c}"/>'
        f'<text x="44" y="{y + 25}" text-anchor="middle" font-family="{SANS}" font-size="14" font-weight="700" fill="#fff">{method}</text>'
        f'<text x="96" y="{y + 25}" font-family="{MONO}" font-size="16" font-weight="700" fill="{t["fg"]}">{escape(path)}</text>'
        f'<text x="{96 + len(path) * 9.8 + 14}" y="{y + 25}" font-family="{SANS}" font-size="13.5" fill="{t["dim"]}">{escape(summary)}</text>'
        f'{status_svg}{chevron}'
    )


def endpoint(t, method, path, summary, status=None):
    c = METHODS[method]
    h = 50
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{h}" viewBox="0 0 {W} {h}" role="img" aria-label="{method} {path}: {escape(summary)}">
<rect x="0.5" y="1.5" width="{W - 1}" height="{h - 6}" rx="4" fill="{hex_rgba(c, t["tint"])}" stroke="{c}"/>
<g transform="translate(0 -2)">{endpoint_head(t, method, path, summary, status)}</g>
</svg>
'''


def json_lines(t, data_lines):
    """data_lines: lista de listas de (texto, tipo). tipo: p=pontuação, k=chave, s=string."""
    colors = {"p": t["fg"], "k": t["purple"], "s": t["green"]}
    return [
        "".join(f'<tspan fill="{colors[k]}">{escape(txt)}</tspan>' for txt, k in line)
        for line in data_lines
    ]


def kv(key, values, last=False):
    parts = [("  ", "p"), (f'"{key}"', "k"), (": ", "p")]
    if isinstance(values, list):
        parts.append(("[", "p"))
        for i, v in enumerate(values):
            parts.append((f'"{v}"', "s"))
            if i < len(values) - 1:
                parts.append((", ", "p"))
        parts.append(("]", "p"))
    else:
        parts.append((f'"{values}"', "s"))
    if not last:
        parts.append((",", "p"))
    return parts


STACK = [
    ("languages", ["Java 17+", "SQL", "TypeScript"]),
    ("spring", ["Boot", "Data JPA", "Security", "Cloud Gateway", "Actuator", "Validation"]),
    ("architecture", ["REST", "Microservices", "API Gateway", "BFF", "Event-driven"]),
    ("messaging", ["RabbitMQ"]),
    ("data", ["PostgreSQL", "Hibernate", "Flyway", "MinIO"]),
    ("security", ["JWT", "Role-based access control"]),
    ("testing", ["JUnit 5", "Mockito"]),
    ("infra", ["Docker", "Docker Compose", "Kubernetes", "Linux", "CI/CD"]),
    ("docs", ["OpenAPI", "Swagger"]),
    ("tooling", ["Maven", "Git"]),
]


def endpoint_stack(t):
    c = METHODS["GET"]
    lines = [[("{", "p")]] + [kv(k, v, i == len(STACK) - 1) for i, (k, v) in enumerate(STACK)] + [[("}", "p")]]
    rendered = json_lines(t, lines)
    lh = 21
    code_top = 156
    code_h = len(rendered) * lh + 24
    h = code_top + code_h + 28
    code = nbsp("\n".join(
        f'<text x="40" y="{code_top + 26 + i * lh}">{ln}</text>' for i, ln in enumerate(rendered)
    ))
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{h}" viewBox="0 0 {W} {h}" role="img" aria-label="GET /stack returns: Java 17+, SQL, TypeScript, Spring Boot, Data JPA, Security, Cloud Gateway, Actuator, Validation, REST, Microservices, API Gateway, BFF, Event-driven, RabbitMQ, PostgreSQL, Hibernate, Flyway, MinIO, JWT, RBAC, JUnit 5, Mockito, Docker, Docker Compose, Kubernetes, Linux, CI/CD, OpenAPI, Swagger, Maven, Git">
<rect x="0.5" y="1.5" width="{W - 1}" height="{h - 6}" rx="4" fill="{hex_rgba(c, t["tint"])}" stroke="{c}"/>
<g transform="translate(0 -2)">{endpoint_head(t, "GET", "/stack", "Main stack", expanded=True)}</g>
<line x1="1" y1="44" x2="{W - 1}" y2="44" stroke="{c}"/>
<g font-family="{SANS}">
<text x="20" y="76" font-size="14" font-weight="700" fill="{t["fg"]}">Responses</text>
<rect x="{W - 120}" y="58" width="100" height="28" rx="4" fill="none" stroke="{t["dim"]}"/>
<text x="{W - 70}" y="77" text-anchor="middle" font-size="13" font-weight="700" fill="{t["fg"]}">Try it out</text>
<line x1="20" y1="96" x2="{W - 20}" y2="96" stroke="{t["border"]}"/>
<text x="20" y="118" font-size="12" font-weight="700" fill="{t["dim"]}">Code</text>
<text x="110" y="118" font-size="12" font-weight="700" fill="{t["dim"]}">Response body</text>
<text x="20" y="144" font-size="14" font-weight="700" fill="{t["fg"]}" font-family="{MONO}">200</text>
<text x="110" y="144" font-size="13" fill="{t["dim"]}" font-family="{MONO}">application/json</text>
</g>
<rect x="20" y="{code_top}" width="{W - 40}" height="{code_h}" rx="6" fill="{t["code"]}" stroke="{t["border"]}"/>
<g font-family="{MONO}" font-size="14" xml:space="preserve" style="white-space:pre">
{code}
</g>
</svg>
'''


ENDPOINTS = {
    "about": ("GET", "/about", "Who I am, on LinkedIn", None),
    "projects": ("GET", "/projects", "defesa-pronta, citogenetica, GradeUFLA", None),
    "contact": ("POST", "/contact", "Let's talk, on LinkedIn", ("201", "Created")),
    "bugs": ("DELETE", "/bugs", "Tests, code review and coffee", ("204", "No Content")),
}


def main():
    for name, t in THEMES.items():
        suffix = "" if name == "light" else "-dark"
        files = {
            f"boot{suffix}.svg": header(t),
            f"api{suffix}.svg": swagger_top(t),
            f"api-stack{suffix}.svg": endpoint_stack(t),
        }
        for key, (m, p, s, st) in ENDPOINTS.items():
            files[f"api-{key}{suffix}.svg"] = endpoint(t, m, p, s, st)
        for fname, svg in files.items():
            (OUT / fname).write_text(svg, encoding="utf-8")
            print("ok", fname)


if __name__ == "__main__":
    main()
