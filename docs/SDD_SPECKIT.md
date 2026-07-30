# SDD y Spec Kit — Desarrollo guiado por especificaciones

> Documento conceptual del curso. Explica **qué es el Desarrollo Guiado por
> Especificaciones (SDD, *Spec-Driven Development*)**, qué es **GitHub Spec Kit**,
> cómo se usan, con ejemplos de ESTE proyecto, y cierra comparándolos.
> Las referencias del final están verificadas a julio de 2026.

---

## 1. El problema que ambos resuelven: el "vibe coding"

Desde que existen agentes de codificación con IA (GitHub Copilot, Claude Code,
Cursor, Gemini CLI…), el patrón más común es: usted describe lo que quiere en un
prompt, recibe un bloque de código, **se ve bien… pero no hace exactamente lo que
necesitaba**. A eso se le llama *vibe coding*: programar "por vibra", iterando
prompts sin nunca escribir qué se quería construir.

El vibe coding es excelente para prototipos de una tarde y pésimo para software
serio, por tres razones:

1. **El prompt se pierde**: la "especificación" vivió 30 segundos en un chat.
2. **La IA rellena los vacíos con suposiciones**: todo lo que usted no dijo, el
   modelo lo inventó — y no siempre igual dos veces (la generación de código por
   LLM **no es determinista**, como advierte Thoughtworks).
3. **No hay contra qué verificar**: si no está escrito qué debía hacer, "parece
   que funciona" es el único criterio de aceptación.

En 2025 la industria convergió en la respuesta: volver a escribir
especificaciones — pero ahora como **artefactos ejecutables que alimentan a la
IA**. Esa práctica es el SDD.

## 2. ¿Qué es SDD (Spec-Driven Development)?

**Definición:** metodología en la que se escribe **QUÉ se quiere construir**
(requisitos, restricciones, criterios de aceptación) **antes** de generar
cualquier código, y se trata esa especificación — no el código — como la
**fuente de la verdad** del proyecto. Con IA, la especificación deja de ser
documentación pasiva: es el *input* directo del agente que genera el código.

> Thoughtworks (dic. 2025) lo define como "un paradigma que usa especificaciones
> de software bien elaboradas como prompts, asistidas por agentes de IA, para
> generar código ejecutable", y lo incluyó en su **Technology Radar Vol. 32**
> como técnica a adoptar.

### 2.1 La cadena de artefactos

El flujo típico separa tres preguntas que el vibe coding mezcla:

```
CONSTITUCIÓN  →  ESPECIFICACIÓN  →  PLAN TÉCNICO  →  TAREAS  →  CÓDIGO
(principios       (QUÉ construir      (CÓMO: stack,     (pasos      (generado y
 innegociables)    y para quién)       arquitectura)     ordenados)   verificado
                                                                      contra la spec)
```

- La **especificación** habla de usuarios, requisitos y criterios de aceptación
  — cero tecnología.
- El **plan** decide stack, estructura y patrones — cero requisitos nuevos.
- Las **tareas** trocean el plan en pasos pequeños y verificables.
- El **código** se genera (por IA o humanos) y se valida **contra la spec**, no
  contra la memoria de nadie.

### 2.2 Las tres interpretaciones de SDD (Thoughtworks)

No todo el mundo entiende lo mismo por SDD. Thoughtworks identifica tres "sabores":

| Interpretación | La fuente de verdad es… | Implicación |
|---|---|---|
| **Radical** | Solo la spec; el código es un subproducto regenerable/desechable | Se edita la spec y se regenera el código (como quien recompila) |
| **Conservadora** | El código; la spec impulsa la generación inicial | La spec arranca el trabajo, el código se mantiene a mano |
| **Intermedia** | Spec funcional + detalles técnicos conviven | "No basta con requisitos funcionales; hay que atender lo técnico" |

En la práctica de 2026, la mayoría de equipos opera en la intermedia: la spec
manda, pero el código generado se revisa, se prueba y se mantiene.

### 2.3 SDD no es la cascada (waterfall) de vuelta

Crítica frecuente: "¿escribir documentos antes de programar? Eso es waterfall".
Diferencias clave:

- En cascada, la especificación se escribía **una vez**, en meses, y se
  desactualizaba al primer cambio. En SDD la spec es **viva**: se edita en
  minutos y el código se regenera/ajusta con la IA.
- En cascada el costo de iterar era altísimo; con agentes de IA, iterar
  spec→código cuesta minutos, así que se puede ser ágil **y** tener specs.
- La spec de SDD es **pequeña y por funcionalidad** (una feature = una spec),
  no un tomo monolítico del sistema entero.

### 2.4 Advertencias honestas (estado del arte 2026)

- **No determinismo:** la misma spec puede producir código distinto en dos
  corridas. La spec reduce la varianza; no la elimina.
- **Desviación y alucinación:** el agente puede ignorar partes de la spec.
  Por eso los flujos serios incluyen fases de verificación (checklists,
  análisis de consistencia) y **CI/CD robusto** — los tests siguen siendo el
  árbitro final.
- **Specs basura → código basura:** SDD desplaza el esfuerzo de "escribir
  código" a "pensar con precisión". Si la spec es vaga, la IA vuelve a rellenar
  con suposiciones y se regresa al vibe coding con más pasos.

## 3. ¿Qué es GitHub Spec Kit?

**Definición:** el **toolkit de código abierto (MIT)** de GitHub que implementa
SDD para agentes de codificación. Liberado en **septiembre de 2025**, en 2026 es
el estándar de facto: 125k+ estrellas y soporte para **más de 30 agentes**
(GitHub Copilot, Claude Code, Cursor, Gemini CLI, Codex CLI, Windsurf, Goose…).

Spec Kit NO genera código por sí mismo: instala en su repositorio **plantillas y
comandos slash** que disciplinan al agente de IA que usted ya usa.

### 3.1 Instalación (CLI `specify`)

```bash
# con el gestor de paquetes uv
uv tool install specify-cli --from git+https://github.com/github/spec-kit.git
specify init mi-proyecto --integration copilot   # o claude, cursor, gemini…
```

Esto crea `.specify/` con plantillas y registra los comandos en su agente.

### 3.2 El flujo de comandos (v0.11+, junio 2026)

| Orden | Comando | Qué produce |
|---|---|---|
| 1 | `/speckit.constitution` | `constitution.md` — principios innegociables del proyecto |
| 2 | `/speckit.specify` | `spec.md` — el QUÉ: requisitos, historias, criterios de aceptación |
| 2b | `/speckit.clarify` | Preguntas sobre lo subespecificado ANTES de planear |
| 3 | `/speckit.plan` | `plan.md` + artefactos técnicos: `research.md`, `data-model.md`, `contracts/`, `quickstart.md` |
| 4 | `/speckit.tasks` | `tasks.md` — lista de tareas accionables y ordenadas |
| 4b | `/speckit.analyze` | Análisis de consistencia entre spec ↔ plan ↔ tasks |
| 4c | `/speckit.checklist` | Checklists de calidad que validan los requisitos |
| 5 | `/speckit.implement` | Ejecuta las tareas → **código funcionando** |
| — | `/speckit.taskstoissues` | Convierte tareas en issues de GitHub |
| — | `/speckit.converge` | Compara el código existente contra la spec y anota lo que falta |

La idea central: **cada fase produce un archivo Markdown que la siguiente fase
lee**. El humano revisa y corrige los .md (baratos de editar) antes de que se
conviertan en código (caro de corregir).

### 3.3 Los artefactos de Spec Kit

```
constitution.md   ¿Bajo qué principios? (no cambia por feature)
spec.md           ¿QUÉ y para quién?      ← /speckit.specify
plan.md           ¿CÓMO técnicamente?     ← /speckit.plan
research.md       ¿Por qué estas decisiones? (alternativas evaluadas)
data-model.md     Entidades, campos, relaciones
contracts/        Contratos de API (endpoints, formatos)
quickstart.md     Cómo arrancar y validar rápido
tasks.md          ¿En qué orden? pasos verificables
```

### 3.4 Ejemplo con ESTE proyecto

Este repositorio aplica exactamente esa estructura, escrita a mano con fines
didácticos (sin el CLI): cada componente tiene su kit numerado en orden de
lectura en `docs/spec_kit/` (raíz), `api_generica/docs/spec_kit/`,
`api_facturas/docs/spec_kit/` y `front_flask/docs/spec_kit/`:

```
1_constitution.md → 2_spec.md → 3_plan.md → 4_research.md
→ 5_data_model.md → 6_contracts.md → 7_quickstart.md → 8_tasks.md
```

Ejercicio propuesto: tome el kit de `api_generica/docs/spec_kit/`, entrégueselo
a un agente de IA en una carpeta vacía con la instrucción "construye el proyecto
siguiendo 8_tasks.md fase por fase" y compare el resultado contra los criterios
de aceptación de `2_spec.md`. Eso ES spec-driven development.

Un fragmento real de spec de este proyecto (note el estilo: verificable, sin
tecnología en los requisitos, con criterios de aceptación medibles):

```markdown
### RF6 — Verificar contraseña
`POST /api/{tabla}/verificar-contrasena` con query params campo_usuario,
campo_contrasena, valor_usuario, valor_contrasena.
- Busca el hash almacenado y lo compara con BCrypt.
- 200 contraseña válida · 404 usuario no existe · 401 contraseña incorrecta.

## Criterios de aceptación
6. POST /api/usuario?campos_encriptar=contrasena guarda la contraseña como
   hash BCrypt de 60 caracteres (verificable en la tabla)...
```

## 4. El ecosistema SDD más allá de Spec Kit (2025–2026)

- **AWS Kiro** (julio 2025): IDE agéntico de Amazon construido ALREDEDOR de
  specs. Su flujo genera `requirements.md` (historias de usuario en notación
  **EARS** — *Easy Approach to Requirements Syntax*: "WHEN … THE SYSTEM SHALL …"),
  `design.md` y `tasks.md` antes de escribir código.
- **BMAD-METHOD**: framework comunitario de agentes por rol (analista, PM,
  arquitecto, dev) que producen y consumen specs.
- **Tessl** y la corriente *spec-as-source*: la interpretación radical — el
  código como artefacto compilado desde la spec.
- Para el **Technology Radar Vol. 32** de Thoughtworks y la cobertura en
  martinfowler.com, la pregunta en 2026 ya no es *si* usar SDD sino *cuál
  implementación* usar.

## 5. Comparación final: SDD vs Spec Kit

La comparación correcta no es "cuál es mejor": **son cosas de distinta
categoría**. SDD es la *metodología*; Spec Kit es una *herramienta* que la
implementa. Es la misma relación que hay entre "control de versiones" y "Git".

| Dimensión | **SDD** (metodología) | **Spec Kit** (herramienta) |
|---|---|---|
| ¿Qué es? | Un paradigma/práctica de ingeniería: la spec manda sobre el código | Un toolkit open source (MIT) de GitHub que operacionaliza SDD |
| ¿Quién lo define? | La industria (Thoughtworks, GitHub, AWS, comunidad académica) | GitHub (repo `github/spec-kit`) |
| ¿De qué depende? | De disciplina del equipo; se puede hacer con cualquier editor y agente | Del CLI `specify` + un agente de IA compatible (30+) |
| Artefactos | Los que el equipo decida (una spec puede ser un doc, un test, un contrato OpenAPI) | Fijos y con plantilla: constitution, spec, plan, research, data-model, contracts, quickstart, tasks |
| Proceso | Libre: solo exige "spec antes que código" y verificación contra la spec | Guiado por comandos: `/speckit.specify → clarify → plan → tasks → analyze → implement` |
| Flexibilidad | Total (interpretación radical, conservadora o intermedia) | Opinionada: una carpeta por feature, fases en orden, el agente lee los .md |
| Sin IA, ¿sirve? | Sí — SDD existía como idea antes de los LLM (specs, TDD, diseño por contrato son parientes) | Poco — Spec Kit está diseñado específicamente para dirigir agentes de IA |
| Alternativas equivalentes | — (es la categoría) | AWS Kiro, BMAD-METHOD, Tessl, plantillas manuales (como las de este repo) |
| Riesgos propios | Specs vagas o desactualizadas → vuelve el vibe coding con burocracia | Acoplamiento a su estructura/plantillas; sobrecarga para cambios triviales |
| En este proyecto | La práctica: escribimos QUÉ→CÓMO→TAREAS antes de tocar código | La estructura de nuestros `spec_kit/` replica sus artefactos (a mano, con numeración didáctica) |

**Regla mental para el examen:** *SDD es el "qué hacer" (escribir la
especificación primero y tratarla como fuente de verdad); Spec Kit es un "con
qué hacerlo" (comandos y plantillas de GitHub para que un agente de IA siga esa
disciplina).* Se puede hacer SDD sin Spec Kit — este repositorio lo demuestra —
pero no tiene sentido usar Spec Kit sin adoptar SDD.

---

## Referencias (verificadas — julio de 2026)

**Fuentes primarias:**

1. GitHub — *Spec-driven development with AI: Get started with a new open source
   toolkit* (blog oficial del lanzamiento, sep. 2025):
   <https://github.blog/ai-and-ml/generative-ai/spec-driven-development-with-ai-get-started-with-a-new-open-source-toolkit/>
2. Repositorio oficial `github/spec-kit` (MIT, 125k+ ⭐, comandos y CLI `specify`):
   <https://github.com/github/spec-kit>
3. Documentación oficial de Spec Kit: <https://github.github.com/spec-kit/>
4. Thoughtworks — Liu Shangqi, *Spec-driven development: Unpacking one of 2025's
   key new AI-assisted engineering practices* (4 dic. 2025; las tres
   interpretaciones y las advertencias sobre no determinismo):
   <https://www.thoughtworks.com/en-us/insights/blog/agile-engineering-practices/spec-driven-development-unpacking-2025-new-engineering-practices>
5. Thoughtworks Technology Podcast — *What is spec-driven development?*:
   <https://www.thoughtworks.com/insights/podcasts/technology-podcasts/what-is-spec-driven-development>
6. AWS Kiro — documentación de specs (EARS, requirements/design/tasks):
   <https://kiro.dev/docs/specs/>

**Análisis y guías recientes:**

7. MarkTechPost — *Meet GitHub Spec-Kit: An Open Source Toolkit for Spec-Driven
   Development with AI Coding Agents* (8 may. 2026):
   <https://www.marktechpost.com/2026/05/08/meet-github-spec-kit-an-open-source-toolkit-for-spec-driven-development-with-ai-coding-agents/>
8. DevOps.com — *GitHub's Spec Kit Puts the Spec Back in Software Development*:
   <https://devops.com/githubs-spec-kit-puts-the-spec-back-in-software-development/>
9. BCMS — *Spec-Driven Development (SDD): The Definitive 2026 Guide*:
   <https://www.thebcms.com/blog/spec-driven-development/>
10. Augment Code — *Spec-Driven Development vs Waterfall: Key Differences*:
    <https://www.augmentcode.com/guides/spec-driven-development-vs-waterfall>

**En este repositorio (ejemplos aplicados):**

- Kit raíz: [`docs/spec_kit/`](spec_kit/2_spec.md) ·
  [API Genérica](../api_generica/docs/spec_kit/2_spec.md) ·
  [API Facturas](../api_facturas/docs/spec_kit/2_spec.md) ·
  [Front Flask](../front_flask/docs/spec_kit/2_spec.md)
