# BhoomiSync workstation design system

## Intent and surfaces
Dense desktop GIS operations workspace. Surface 0 cool neutral application canvas; surface 1 main white registry/work area; surface 2 tool/inspector background. Flat dividers establish groups; no card grid or decorative hero.

## Tokens
Primary family Segoe UI/system sans (local, no font download). 13px body, 11–12px metadata, 13px panel heading, 17px section, 24px page heading. Map Review uses a 14px context heading. Tabular numeric values; restrained monospace only for IDs/CRS. 4/8/12/16/20/24/32px spacing. 4px control radius and 4px panel maximum. One-pixel subtle/default/strong borders. Shadows only on map overlays and popovers.

Colors: neutral slate navigation, near-black text, muted slate metadata, deep teal primary action. Teal harmonized boundaries; charcoal cadastral; blue dashed municipal; indigo GNSS; muted gray-violet buildings; amber new/modified change; red removed/conflict; orange review. Status colors describe evidence, not decorations. Matched polygons use 4% teal fill; status appears principally on their stroke. Selection has a contrasting dark stroke, teal inset and 12% fill.

## Components and interaction
One Lucide line-icon family at 16px/1.6px stroke. Three button weights: primary, bordered secondary, quiet/icon. Buttons 30–32px high with descriptive titles/aria labels. Visible 2px focus outline; disabled actions show stable labels. Forms use 32px aligned controls. Tables have 36–44px rows, sticky headers, left text/right numeric alignment, subdued row hover and explicit keyboard row activation. Shared status dot/text avoids badge proliferation.

Map toolbar: zoom, fit extent, focus selection, reset north/view, layers and source comparison; every tool actually changes the map. Layers grouped by master/reference/survey/change/diagnostics with real feature counts. Comparison enables cadastral/municipal boundaries without opaque fills. Inspector header stays fixed; evidence, source IDs, conflicts, changes and explanation scroll independently. No approval action because the API provides no decision-write endpoint.

## Desktop layout
200px sidebar; 52px workspace bar; 42px map context toolbar; 344px inspector. Map consumes remaining width/height. Body has no desktop overflow; registries and inspector scroll internally. At 1366x768, center map remains >780px wide. At 1920x1080 it expands without stretched cards. Below 1100px navigation becomes a compact icon rail; below 760px inspector is a toggleable drawer. Map stays usable, with reduced toolbar labels.

## Truthful metadata
Synthetic dataset notice is one inline label with a disclosure tooltip. Run ID and actual processing duration come from API. Session-observed completion time is labeled when displayed; no invented server timestamps. No fake resolved filter, government authority, accuracy probability, imagery or human approval persistence.

## Visual identity refinement

The follow-up visual pass uses an ink/navy command shell, mineral cyan and pale lime signal accents. `identity.css` adds the shared visual treatment: indexed navigation, a layered brand emblem, stronger typography, tinted table headers, hover feedback, semantic metric values and a refined inspector. Reduced-motion preferences disable decorative transitions.

Map Review defaults to a night palette with cyan master boundaries, blue municipal comparison, indigo GNSS, amber review and red conflicts. The sun/moon control switches actual MapLibre paint properties between night and daylight, without replacing geometry or fetching a basemap. A compact overlay uses the completed snapshot's actual parcel and review counts. No backend code or endpoint contracts changed.
