# iCLONE Agent — Art system

Deterministic, fully on-chain SVG silhouettes. Same `seed` → same art, forever. Dark body dominant, **one focal colour** per agent (design philosophy: colour only on the focal element).

## Rarity tiers

Three tiers only. Each tier sets the focal colour and scarcity weight.

| Tier | Focal colour | Notes |
|---|---|---|
| `rare` | `#5ba3d0` (blue) | base tier |
| `superrare` | `#b86fd9` (violet) | mid scarcity |
| `iclone` | `#d9a23b` (gold) | apex tier — the iCLONE signature |

> Renamed 2026-06-18 from `common / rare / legendary` → `rare / superrare / iclone`. Applies to the program (widgets), the metadata `attributes`, and the marketplace badges.

## Silhouette engine

Composed from a `mulberry32(seed)` PRNG. The body is dark (`#161b21` / `#1f262e` / `#0a0e12`); only eyes / focal zone / glyph carry the tier colour.

Parametric parts:

- **head**: `hex` · `round` · `visor` · `hair`
- **eyes**: `slits` · `dots` · `mono`
- **torso**: `broad` · `slim` · `armored`
- **chest glyph**: `circle` · `tri` · `diamond` · `cross`
- **vivid zones** (optional): paint chest/shoulders in the full focal colour

## Accessories (Image Lab)

Toggleable layers, composed on top of the base silhouette:

| Accessory | Meaning |
|---|---|
| Hat | fedora with focal hatband |
| Cigarette | lit tip + smoke |
| Astronaut helmet | translucent dome (mutually exclusive with Hat) |
| Shoulder pad (ombreira) | focal-coloured pauldrons |
| Weapon | blade with focal edge |
| PC | laptop/terminal in hands, focal screen |

## The 10 base concepts (genesis)

The first 10 agents are the **track leads** of the Virtuals Hackathon (10 tracks × 10), reusing the planned fleet names (`agent_fleet_plan_100.json`). Each defines a concept: focal colour + default head + preset accessories.

| # | Agent | Track | Focal | Default look |
|---|---|---|---|---|
| 1 | UNIX | DeFi & Trading | emerald `#1d9e75` | visor + PC |
| 2 | iCLONE | Market Intelligence | blue `#5ba3d0` | hex / scanner |
| 3 | MATRIX | Developer Tools & Code | green `#639922` | visor + PC |
| 4 | DoctorWHO | Research & Knowledge | violet `#7f77dd` | round + hat |
| 5 | SuperSayatin | Content & Media | amber `#ef9f27` | spiked hair |
| 6 | TALOS | Robotics & Physical AI | red `#d05b5b` | visor + shoulder |
| 7 | Cerberus | Security & Audit | crimson `#a32d2d` | hex + weapon |
| 8 | Apollo | Creative & Art | pink `#d4537e` | round |
| 9 | KRATOS | Gaming & Virtual Worlds | coral `#d85a30` | hex + weapon + shoulder |
| 10 | THOTH | Commerce & Oracles | gold `#d9a23b` | hat + tablet/PC |

## Authoring tools (widgets)

- `Widget Design/WIDGET FRAME/SILUETAS.widget` — pure silhouette engine (class × tier × seed).
- `Widget Design/WIDGET FRAME/IMAGE LAB.widget` — the 10 base concepts + accessories + vivid zones + variations. This is the engine that feeds the "agent image" step of the iCLONE FRAME mint studio.
