"""
iCLONE — ChainGPT Design Training Module
Sources: https://www.chaingpt.org (design system analysis)
         ChainGPT site: Webflow + custom JS + Rive animations

Treina o iCLONE com o sistema de design world-class do ChainGPT:
  - Paleta de cores e gradientes exactos
  - Tipografia e escala tipográfica
  - Padrões de layout e componentes
  - Linguagem de animação (Rive, keyframe, path-anim)
  - Padrões de UX para produtos Web3
  - Princípios de design dark-first para AI/blockchain

Score mínimo de aprovação: 90%
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
import uuid

MODULE_ID  = "chaingpt_design_training"
MODULE_VER = "1.0.0"
SOURCE     = "https://www.chaingpt.org"

# ─── Design system knowledge base ────────────────────────────────────────────

DESIGN_SYSTEM = {

    "identity": {
        "brand_name": "ChainGPT",
        "tagline": "Unleash The Power of Blockchain AI",
        "sub_tagline": "Your personal expert in all crypto & blockchain related topics.",
        "navigation_tagline": "Your Gateway To Web3 AI",
        "brand_voice": "Technical authority with accessibility. Precise, not jargon-heavy. Empowering, not intimidating.",
        "audience": "Developers, traders, Web3 builders, DeFi users",
        "personality": "Expert robotics mascot — structured, glowing, approachable despite technical depth",
    },

    "color_system": {
        "backgrounds": {
            "primary": "#09090E",      # Near-black with blue tint — main surface
            "secondary": "#0a090f",    # Slightly lighter — card backgrounds
            "overlay": "rgba(0,0,0,0.75)",  # Modal overlays
            "card": "#353539",         # Elevated surface
            "card_alt": "#595959",     # Secondary card surface
        },
        "text": {
            "primary": "#EFEFE5",      # Warm off-white — main text
            "secondary": "rgba(239,239,229,0.6)",  # 60% opacity — secondary text
            "muted": "#807f85",        # Muted grey
        },
        "accents": {
            "cyan_primary": "#28EFCE",   # Primary teal/cyan accent
            "cyan_alt": "#2CE7D2",       # Slight variation
            "cyan_deep": "#26F4D0",      # Deeper cyan
            "orange_primary": "#FB7C4F", # Primary orange accent
            "orange_warm": "#FC914D",    # Warmer orange
            "orange_coral": "#FC6756",   # Coral orange
            "purple_primary": "#6A59E5", # Primary purple
            "purple_deep": "#724CE8",    # Deeper purple
            "purple_mid": "#6072E2",     # Mid purple-blue
            "green_primary": "#74E79A",  # Success green
            "green_teal": "#69E79E",     # Teal-green
            "yellow": "#F8CF3E",         # Yellow accent
            "chartreuse": "#BCDA68",     # Chartreuse green
        },
        "gradient_system": {
            "hero_spectrum": "linear-gradient(to right, #724CE8 -2.59%, #26F4D0 31.53%, #F8CF3E 62.52%, #FC6756 100%)",
            "hero_conic": "conic-gradient(from 148.85deg at 50% 36.76%, #724CE8 0deg, #26F4D0 119.73deg, #F8CF3E 228.48deg, #FC6756 360deg)",
            "cyan_horizontal": "linear-gradient(to right, #28EFCE 0%, #2CE7D2 100%)",
            "orange_horizontal": "linear-gradient(to right, #FB7C4F 0%, #FA7952 100%)",
            "brand_diagonal": "linear-gradient(to right, #2BE6D1 0%, #6A59E5 100%)",
            "purple_to_orange": "linear-gradient(to bottom, #6A59E5 0%, #FB7A52 100%)",
            "green_vertical": "linear-gradient(to bottom, #28EFCE 0%, #69E79E 100%)",
            "section_fade_in": "linear-gradient(180deg, rgba(9,9,14,0) 0%, #09090E 100%)",
            "section_fade_out": "linear-gradient(0deg, #09090E 0%, rgba(9,9,14,0) 100%)",
            "section_fade_left": "linear-gradient(90deg, #09090E 0%, rgba(9,9,14,0) 100%)",
            "section_fade_right": "linear-gradient(270deg, #09090E 0%, rgba(9,9,14,0) 100%)",
        },
        "philosophy": "Dark background with spectrum gradients. Cyan = primary CTA. Orange = secondary/energy. Purple = depth/intelligence. No pure white.",
    },

    "typography": {
        "primary_font": "Roboto Mono",
        "fallback": "sans-serif",
        "classification": "Monospace — chosen to reinforce code, precision, and technical authority",
        "scale": {
            "display": "3.5rem",          # Hero headlines
            "heading_lg": "calc(16px + 6 * ((100vw - 1440px) / 720))",  # Fluid heading
            "heading_md": "30px",          # Section headings
            "body_lg": "1.125rem",         # 18px
            "body_md": "0.875rem",         # 14px
            "body_sm": "0.8125rem",        # 13px
            "fluid_body": "calc(14px + 2 * ((100vw - 320px) / 1000))",  # Fully fluid
        },
        "letter_spacing": "0 — tight, monospace default. Not tracked out.",
        "heading_style": "Mixed case preferred. UPPERCASE for system labels, categories, technical terms.",
        "line_height": "Tight-to-medium. Technical content breathes less.",
        "key_insight": "Roboto Mono creates cognitive alignment with code editors, terminals, and blockchain explorers. Signals technical seriousness.",
    },

    "layout_system": {
        "grid": "CSS Grid + Flexbox. Not Bootstrap. Custom responsive.",
        "breakpoints": {
            "mobile": "class='mobile'",
            "tablet": "class='tablet'",
            "desktop": "class='desktop'",
        },
        "border_radius": {
            "none": "0 — for sharp technical elements",
            "small": "2px — very tight radius for inputs, tags",
            "pill": "0.75rem — for cards and containers",
            "circle": "50% — for avatars and icon badges",
        },
        "spacing_philosophy": "Generous whitespace in hero sections. Tighter in data-dense product sections.",
        "section_structure": {
            "section_title": "Primary heading with cyan accent",
            "section_title_bordered": "Heading with horizontal border decorations left and right",
            "section_title_bordered_lg": "Larger bordered variant",
            "section_title_bordered_partial": "Border only on left side",
        },
    },

    "component_patterns": {
        "buttons": {
            "primary": {
                "name": "btn-primary",
                "style": "Dark background, cyan/orange accent stroke with animated line corners",
                "corners": "Uses btn-primary-lines-1 and btn-primary-lines-2 pseudo-elements for corner accents",
                "grey_variant": "btn-primary--grey — muted version for secondary actions",
            },
            "cta": {
                "primary_cta": "LAUNCH DAPP — main hero CTA",
                "style": "Outlined button with spectrum gradient stroke",
                "pattern": "Always paired with a secondary text link",
            },
        },
        "navigation": {
            "structure": "Horizontal top nav. Logo left. Items center. CTA right.",
            "mega_menu": "OUR ECOSYSTEM — full ecosystem dropdown with sub-sections",
            "ecosystem_items": [
                "CRYPTO AI HUB",
                "AI NFT GENERATOR",
                "OUR LAUNCHPAD — Incubation Labs / IDO platform",
                "SECURITY EXTENSION — COMING SOON",
            ],
            "main_nav": ["Solutions", "Developers", "About AI Hub", "Learn", "$CGPT", "Community"],
            "cta_button": "LAUNCH DAPP",
            "mobile_pattern": "Hamburger → fullscreen overlay with slide animation",
        },
        "hero_section": {
            "layout": "3D mascot center. UI command prompts left. Status panel right.",
            "mascot": "Robotic character with RGB/spectrum lighting. Articulated. Friendly but technical.",
            "command_panels": "Dark overlaid panels showing AI commands in action (monospace)",
            "status_panel": "Shows DEPLOYING ON... → AI VIRTUAL MACHINE with list items",
            "text_mix": "UPPERCASE labels + Title Case headlines",
            "animation": "heroSlideAnim + heroSlideActiveAnim + path animations",
        },
        "cards": {
            "surface": "#353539 background",
            "radius": "0.75rem",
            "border": "1px solid transparent with gradient stroke on hover",
            "content": "Icon (coloured) + H3 + description paragraph",
        },
        "sliders": {
            "types": ["team-slider", "unlimited-slider", "media-slider", "roadmap-slider"],
            "engine": "Webflow native slider + custom JS",
        },
        "stats_display": {
            "pattern": "Large number + label. TVL, MAUs displayed as social proof.",
        },
        "sections_observed": [
            "Hero — mascot + command panels",
            "Our Solutions — product grid with icon cards",
            "The Ecosystem behind ChainGPT — ecosystem overview",
            "Pricing — tier cards",
            "$CGPT — token utility section",
            "Roadmap — timeline slider",
            "FAQ — accordion",
            "Footer — multi-column with newsletter form",
        ],
    },

    "animation_system": {
        "engine": "Rive (runtime vector animations) + CSS keyframes",
        "rive_elements": ["loader-lottie", "rive-animation", "token-video"],
        "keyframe_animations": {
            "marqueeScroll": "Infinite horizontal scroll for logos/partners",
            "heroSlideAnim": "Hero element entrance — slide in",
            "heroSlideActiveAnim": "Hero active state transition",
            "showFullAside": "Sidebar/menu open animation",
            "closeFullAside": "Sidebar/menu close animation",
            "overlayFadeIn": "Modal overlay fade",
            "verticalSlideAnimation": "Vertical content reveal",
            "horizontalSlideAnimation": "Horizontal content reveal",
            "dashRunner": "Animated dash/stroke effect along a path",
            "heroRightSlideAnim": "Right panel hero animation",
        },
        "path_animations": {
            "path-anim": "Base path animation class",
            "path-anim-right": "Animate towards right",
            "path-anim-right-2": "Secondary right variant",
            "path-anim-left": "Animate towards left",
            "path-anim-left-1": "Secondary left variant",
            "path-anim-sm-1": "Small path animation 1",
            "path-anim-sm-2": "Small path animation 2",
            "path-anim-1": "Path animation variant 1",
            "path-anim-2": "Path animation variant 2",
            "path-anim-delay-1-1": "Delayed animation variant",
            "path-anim-delay-8": "8-unit delay",
            "path-anim-delay-95": "95ms delay",
            "path-anim-delay-105": "105ms delay",
            "line-animaton": "Line stroke animation",
            "svg-stroke-left": "SVG stroke from left",
            "svg-stroke-right": "SVG stroke from right",
        },
        "philosophy": "Motion serves hierarchy. Entrances stagger. Nothing animates without purpose. Rive for mascot complexity, CSS for UI transitions.",
    },

    "ux_principles": {
        "information_hierarchy": [
            "1. Product proof (mascot + live demo command) — trust immediately",
            "2. Ecosystem overview (breadth) — scope the offering",
            "3. Specific solutions (depth) — each product card",
            "4. Pricing (conversion) — transparent tiered",
            "5. Token utility ($CGPT) — investment case",
            "6. Roadmap (momentum) — future proof",
            "7. FAQ (objection handling) — remove friction",
        ],
        "web3_ux_conventions": [
            "LAUNCH DAPP — never 'Sign Up'. Web3 users don't create accounts, they connect wallets.",
            "Token ticker always in uppercase: $CGPT, $ETH",
            "Chain names lowercase: ethereum, base, solana",
            "Address display: always truncated 0x1234...5678",
            "Transaction status: Pending → Confirmed (never 'Processing')",
            "Gas estimate always shown before transaction",
            "Risk warnings before any fund-moving action",
        ],
        "dark_first": [
            "#09090E base — not pure black, has subtle blue warmth",
            "Spectrum gradients against dark = premium glow effect",
            "Text at 60% opacity for secondary = layered depth",
            "No white backgrounds anywhere — off-white #EFEFE5 for light elements only",
        ],
        "cognitive_design": [
            "Monospace font aligns with code editor, blockchain explorer contexts",
            "UPPERCASE labels create clear hierarchy without size increase",
            "Border decorations on headings = structured/grid feel without actual table",
            "Corner accent lines on buttons = precise, technical, non-generic",
        ],
        "social_proof_pattern": "TVL + MAUs as hero stats → Case studies with named companies → Team section",
        "conversion_flow": "Hero CTA → Product section → Pricing → LAUNCH DAPP",
    },

    "design_for_iclone": {
        "direct_applications": [
            "Use #09090E as iCLONE dashboard background",
            "Use #28EFCE as primary action color (matches Virtuals Protocol teal aesthetic too)",
            "Use Roboto Mono for all data display (wallet addresses, amounts, job IDs)",
            "Apply section_fade gradients to separate visual sections",
            "Use bordered section titles (double horizontal line) for each offering category",
            "Corner accent lines on CTA buttons instead of rounded borders",
            "UPPERCASE for all system labels (OFFERING_ID, STATUS, PRICE) — lowercase for descriptions",
        ],
        "tone_for_iclone_content": [
            "Technical authority, not hype",
            "Precise metric > vague claim (1.03 USDC earned, not 'great revenue')",
            "DEPLOYING ON... → ACP MARKETPLACE (mirror ChainGPT command panel style)",
            "Status labels: ACTIVE | PENDING | COMPLETED — never 'Processing' or 'Working on it'",
        ],
        "component_to_build": {
            "offering_card": "icon (cyan) + name (Roboto Mono uppercase) + description + price badge + SLA tag",
            "job_status_panel": "Dark card with status dot (green/orange/red) + job ID (mono) + price + timestamp",
            "agent_selector": "Horizontal pill tabs: CLONE | SuperSayatin | DoctorWHO | MATRIX",
            "revenue_chart": "Dark background, cyan line, orange area fill, minimal grid",
        },
    },
}

# ─── Training checks ──────────────────────────────────────────────────────────

TRAINING_CHECKS = [

    # Colors
    ("What is ChainGPT's primary background color?",
     "#09090E — near-black with blue tint, not pure black",
     "colors"),

    ("What is ChainGPT's primary text color?",
     "#EFEFE5 — warm off-white, not pure white",
     "colors"),

    ("What is ChainGPT's primary accent/CTA color?",
     "#28EFCE — teal/cyan. Used for primary CTAs and highlights.",
     "colors"),

    ("What are the 4 colors in ChainGPT's hero spectrum gradient?",
     "#724CE8 purple, #26F4D0 cyan, #F8CF3E yellow, #FC6756 coral-orange",
     "colors"),

    ("How should secondary text be styled?",
     "rgba(239,239,229,0.6) — primary text at 60% opacity. Creates depth without a different color.",
     "colors"),

    ("How does ChainGPT handle section transitions on dark backgrounds?",
     "Gradient fades to/from #09090E. linear-gradient(180deg, rgba(9,9,14,0) 0%, #09090E 100%)",
     "colors"),

    # Typography
    ("What font does ChainGPT use?",
     "Roboto Mono, sans-serif fallback. Monospace chosen to signal technical precision.",
     "typography"),

    ("What is the display/hero font size?",
     "3.5rem for hero displays.",
     "typography"),

    ("What case is used for system labels vs body text?",
     "UPPERCASE for system labels, categories, technical terms. Title/sentence case for body content.",
     "typography"),

    ("Why monospace for a marketing/product site?",
     "Cognitive alignment with code editors, terminals, blockchain explorers. Signals technical authority.",
     "typography"),

    # Layout
    ("What border radius does ChainGPT use for cards?",
     "0.75rem for cards/containers. 2px for tight technical elements. 50% for circles.",
     "layout"),

    ("What is ChainGPT's button style?",
     "btn-primary with corner accent lines (btn-primary-lines-1 / -2). No standard rounded button. Custom geometric corners.",
     "layout"),

    # Navigation
    ("What is ChainGPT's main CTA button?",
     "LAUNCH DAPP — not 'Sign Up'. Web3 users connect wallets, not create accounts.",
     "navigation"),

    ("What is in the Our Ecosystem mega menu?",
     "CRYPTO AI HUB, AI NFT GENERATOR, OUR LAUNCHPAD (Incubation Labs + IDO), SECURITY EXTENSION (coming soon).",
     "navigation"),

    # Animation
    ("What animation engine does ChainGPT use for complex animations?",
     "Rive — runtime vector animations. Plus CSS keyframes for UI transitions.",
     "animation"),

    ("What is the dashRunner animation?",
     "Animated dash/stroke along a path. Used for border and line decoration effects.",
     "animation"),

    ("What pattern do path animations follow?",
     "path-anim classes with directional variants (right, left) and delay classes (delay-8, delay-95, delay-105). Staggered entrance.",
     "animation"),

    # UX principles
    ("What is the Web3 UX rule for CTAs?",
     "Always LAUNCH DAPP or CONNECT WALLET — never 'Sign Up' or 'Register'. Web3 users connect, they don't register.",
     "ux"),

    ("What is the information hierarchy on the ChainGPT homepage?",
     "1.Trust (mascot+demo) 2.Breadth (ecosystem) 3.Depth (solutions) 4.Pricing 5.Token 6.Roadmap 7.FAQ",
     "ux"),

    ("How does ChainGPT establish trust in the hero?",
     "3D mascot center + live command panels showing AI in action + status panel. Product proof before any marketing copy.",
     "ux"),

    # iCLONE application
    ("What ChainGPT colors should iCLONE use for its UI?",
     "#09090E background, #28EFCE primary CTA, #EFEFE5 text, Roboto Mono for data.",
     "iclone"),

    ("What tone should iCLONE use based on ChainGPT's design language?",
     "Technical authority. Precise metrics not vague claims. UPPERCASE system labels. Status: ACTIVE|PENDING|COMPLETED.",
     "iclone"),

    ("How should iCLONE style its offering cards?",
     "Cyan icon + Roboto Mono uppercase name + description + price badge + SLA tag. Dark card (#353539) with 0.75rem radius.",
     "iclone"),

    ("What gradient should iCLONE use for revenue charts?",
     "Dark #09090E background, #28EFCE cyan line, orange area fill, minimal grid lines.",
     "iclone"),

    ("What social proof pattern should iCLONE follow?",
     "Show precise metrics first: jobs completed, USDC earned, success rate. Then named case studies. Then team/agent profiles.",
     "iclone"),
]

# ─── Training module ──────────────────────────────────────────────────────────

@dataclass
class TrainingResult:
    total: int = 0
    passed: int = 0
    failed: list = field(default_factory=list)
    score: float = 0.0
    session_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


def _check(question: str, expected_keywords: str, category: str, result: TrainingResult) -> None:
    result.total += 1
    keywords = [kw.strip().lower() for kw in expected_keywords.split(".")[:1][0].split(",")[:3]]
    knowledge_str = str(DESIGN_SYSTEM).lower()
    found = sum(1 for kw in keywords if any(part in knowledge_str for part in kw.split()))
    if found >= max(1, len(keywords) // 2):
        result.passed += 1
    else:
        result.failed.append({"question": question, "category": category, "missing": keywords})


def run_training() -> dict:
    result = TrainingResult()
    for question, expected, category in TRAINING_CHECKS:
        _check(question, expected, category, result)

    result.score = round(result.passed / result.total * 100, 1) if result.total else 0.0

    return {
        "module": MODULE_ID,
        "version": MODULE_VER,
        "source": SOURCE,
        "session_id": result.session_id,
        "timestamp": result.timestamp,
        "total": result.total,
        "passed": result.passed,
        "failed_count": len(result.failed),
        "score": result.score,
        "passed_threshold": result.score >= 90.0,
        "failures": result.failed,
        "design_summary": {
            "primary_bg": "#09090E",
            "primary_accent": "#28EFCE",
            "primary_text": "#EFEFE5",
            "primary_font": "Roboto Mono",
            "animation_engine": "Rive + CSS keyframes",
            "gradient_count": len(DESIGN_SYSTEM["color_system"]["gradient_system"]),
            "animation_types": len(DESIGN_SYSTEM["animation_system"]["keyframe_animations"]),
        },
    }


if __name__ == "__main__":
    import json
    report = run_training()
    print(json.dumps(report, indent=2))
    print(f"\n{'✓ PASSED' if report['passed_threshold'] else '✗ FAILED'} — {report['score']}% ({report['passed']}/{report['total']})")
