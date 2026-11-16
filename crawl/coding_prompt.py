"""Frozen coding prompt (codebook v0.3, dimensions D2-D4), output schema, and item loading.
Shared by every LLM coding run so that all models receive identical instructions."""
import json

SUB = ['NONE', 'ISO25010:functional suitability', 'ISO25010:performance efficiency', 'ISO25010:compatibility',
       'ISO25010:interaction capability', 'ISO25010:reliability', 'ISO25010:security', 'ISO25010:maintainability',
       'ISO25010:flexibility', 'ISO25010:safety', 'Constraint:physical', 'Constraint:legal', 'Constraint:cultural',
       'Constraint:environmental', 'Constraint:design & implementation', 'Constraint:interface']
SCHEMA = {
    'type': 'object',
    'properties': {
        'evidence': {'type': 'string', 'description': 'Verbatim span(s) from the decision text that justify the labels.'},
        'mood': {'type': 'string', 'enum': ['INDICATIVE', 'OPTATIVE']},
        'locus': {'type': 'string', 'enum': ['ENV', 'INTERFACE', 'MACHINE', 'NA']},
        'concern': {'type': 'string', 'enum': ['FUNCTIONAL', 'PERFORMANCE', 'SPECIFIC-QUALITY', 'CONSTRAINT', 'PROJECT-PROCESS', 'NA']},
        'subcode': {'type': 'string', 'enum': SUB},
    },
    'required': ['evidence', 'mood', 'locus', 'concern', 'subcode'],
    'additionalProperties': False,
}
SYSTEM = """You are a requirements engineering researcher coding decisions recorded in spec-driven development artifacts written with AI coding agents. Apply the codebook exactly; do not invent categories.

Each item is one recorded decision: a question with its answer, an assumption, a delegated topic, or a design decision. Code what the text states, not what you guess the project is.

D2 MOOD (Zave & Jackson 1997, "Four Dark Corners of Requirements Engineering")
- INDICATIVE: states how the world is, independent of the system (domain knowledge, facts about users, environment, existing external systems or services). Test: would the statement remain true if the system were never built? If yes, INDICATIVE.
- OPTATIVE: states what the system should be or do, or records a choice about the system.
INDICATIVE also covers properties of machines that already exist in the environment (Zave & Jackson: the environment includes existing systems): availability or behaviour of external services, APIs, models, third-party libraries and tools; facts about existing code, data, infrastructure, or capacity; expectations about users, markets, or competitors; statements that something works, is sufficient, or holds. Such statements are INDICATIVE even when phrased with "will" or "should", because they are not choices about the system being built.
If INDICATIVE, set locus=NA, concern=NA, subcode=NONE.

D3 LOCUS (Gunter, Gunter, Jackson & Zave 2000, WRSPM reference model). Only for OPTATIVE.
- ENV: refers only to environment phenomena: goals, business rules, outcomes in the world.
- INTERFACE: refers to phenomena shared at the machine boundary: inputs, outputs, UI behaviour, error messages shown, API contracts exposed to external parties.
- MACHINE: refers to phenomena hidden inside the machine: internal architecture, libraries, frameworks, data structures, algorithms, file layout, internal configuration.
Test: can an observer outside the machine check the decision without seeing the code? If no, MACHINE.

D4 CONCERN (Glinz 2007, "On Non-Functional Requirements", concern-based taxonomy). Only for OPTATIVE. Ask in order and take the first YES:
1. FUNCTIONAL: stated to specify system behaviour, data, input, or reaction to input stimuli?
2. PERFORMANCE: stated because of timing, processing or reaction speed, data volume, or throughput?
3. SPECIFIC-QUALITY: stated to specify a specific quality the system or a component shall have? Set subcode to the ISO/IEC 25010:2023 characteristic.
4. CONSTRAINT: any other restriction about what the system shall do or how, or a prescribed solution or solution element? Set subcode to the Glinz constraint type (physical, legal, cultural, environmental, design & implementation, interface).
5. PROJECT-PROCESS: about the project or development process rather than the system (testing strategy, CI, phasing, conventions, documentation tasks).
For FUNCTIONAL, PERFORMANCE, and PROJECT-PROCESS set subcode=NONE.

Worked examples:
- "Q: How long should sessions last? A: 30 minutes, then automatic logout" -> OPTATIVE, INTERFACE, FUNCTIONAL, NONE
- "Users access the app from company laptops on the corporate VPN" -> INDICATIVE, NA, NA, NONE
- "Use SQLite with WAL mode for local storage" -> OPTATIVE, MACHINE, CONSTRAINT, Constraint:design & implementation
- "Expand component tests to cover reconnect and unread counts" -> OPTATIVE, NA, PROJECT-PROCESS, NONE
- "Passwords must be hashed; only admins can delete projects" -> OPTATIVE, INTERFACE, SPECIFIC-QUALITY, ISO25010:security

Boundary rules:
R1. If OPTATIVE and locus=MACHINE, concern must be CONSTRAINT (subcode Constraint:design & implementation) or PROJECT-PROCESS; FUNCTIONAL, PERFORMANCE and SPECIFIC-QUALITY require locus ENV or INTERFACE.
R2. If the text states an explicit reason for the decision, classify the concern by that reason (subject to R1).
R3. INTERFACE includes phenomena shared with other programs, processes, devices, or files edited by users; use MACHINE only if nothing outside the machine can observe the decision.
R4. A business rule about domain entities is ENV even if its effect is displayed; use INTERFACE only when the decision is about the display or interaction itself.
R5. A delegated item naming a topic without a value is coded by the concern of the topic (e.g., visual look -> SPECIFIC-QUALITY, ISO25010:interaction capability).

For PROJECT-PROCESS decisions set locus=NA. Quote the supporting text in evidence before deciding."""

def load(path):
    return [json.loads(l) for l in open(path)]

def user_msg(d):
    txt = f"Q: {d['text']}\nA: {d['answer']}" if d.get('answer') else d['text']
    return f"Decision text:\n<decision>\n{txt}\n</decision>"

def items_all():
    D = load('data/decisions.jsonl')
    return [d for d in D if d['provenance'] in ('ASKED', 'ASSUMED', 'DELEGATED') and d['lang_en']]

