#!/usr/bin/env python3
"""Generate coralline theme .conf files from the palettes bundled by the
VS Code extension "Best Themes Redefined" (lakshits11.best-themes-redefined).

The extension ships 92 entries, but ~40 are pure font-styling variants
(Italic / Bold / Bordered / No-Italic) that are color-identical — and a
statusline has no italics or borders. So we emit ONE conf per distinct
palette (~50). Themes with no published hex are reconstructed from their
source theme and tagged `# approximated` in the file header.

Each palette is described by 11 semantic colors; build_conf() maps them to
coralline's VL_BG_* / VL_FG_* variables:

    blue    -> dir            green  -> git-ok / FG_OK
    magenta -> project/style  yellow -> git-dirty / FG_WARN
    purple  -> model          red    -> cost / FG_HOT
    cyan    -> clock/duration
    bg      -> gauge gradient (7d=bg, 5h/ctx lifted toward fg) + dark pill text
    comment -> FG_DIM (brightened toward fg for readability)

Usage:  python3 gen-best-themes.py
Output: ~/.claude/coralline/themes/best-themes/<slug>.conf
"""

from pathlib import Path

# Output next to this script's repo: <repo>/themes/best-themes/
OUT = Path(__file__).resolve().parent.parent / "themes" / "best-themes"


def h2rgb(hx):
    hx = hx.lstrip("#")
    return (int(hx[0:2], 16), int(hx[2:4], 16), int(hx[4:6], 16))


def blend(c1, c2, t):
    a, b = h2rgb(c1), h2rgb(c2)
    return tuple(round(a[i] + (b[i] - a[i]) * t) for i in range(3))


def rgb(t):
    return f"{t[0]},{t[1]},{t[2]}"


def r(hx):
    return rgb(h2rgb(hx))


# Each theme: bg, fg, comment, red, green, yellow, blue, magenta, cyan, orange, purple
# Optional: approx=True (no published hex — reconstructed from source theme)
P = {}


def t(name, bg, fg, comment, red, green, yellow, blue, magenta, cyan, orange,
      purple, approx=False):
    P[name] = dict(bg=bg, fg=fg, comment=comment, red=red, green=green,
                   yellow=yellow, blue=blue, magenta=magenta, cyan=cyan,
                   orange=orange, purple=purple, approx=approx)


# ── Well-known palettes (accurate hex from upstream themes) ───────────────────
t("andromeda-mariana", "#1f2330", "#d5ced9", "#6c6783", "#ee5d43", "#96e072",
  "#ffe66d", "#7cb7ff", "#c74ded", "#00e8c6", "#f39c12", "#c74ded")
t("ayu-darkvenom", "#0a0e14", "#b3b1ad", "#626a73", "#f07178", "#aad94c",
  "#e6b450", "#59c2ff", "#d2a6ff", "#95e6cb", "#ff8f40", "#d2a6ff")
t("brogrammer", "#131313", "#d6dbe5", "#565656", "#f81118", "#2dc55e",
  "#ecba0f", "#2a84d2", "#bd25d3", "#1081d6", "#e5a807", "#aa17e6")
t("catppuccin", "#1e1e2e", "#cdd6f4", "#6c7086", "#f38ba8", "#a6e3a1",
  "#f9e2af", "#89b4fa", "#f5c2e7", "#94e2d5", "#fab387", "#cba6f7")
t("darcula", "#2b2b2b", "#a9b7c6", "#808080", "#ff6b68", "#6a8759", "#ffc66d",
  "#6897bb", "#9876aa", "#629755", "#cc7832", "#9876aa")
t("darcula-darker", "#1e1e1e", "#a9b7c6", "#707070", "#ff6b68", "#6a8759",
  "#ffc66d", "#6897bb", "#9876aa", "#629755", "#cc7832", "#9876aa")
t("dracula-redefined", "#282a36", "#f8f8f2", "#6272a4", "#ff5555", "#50fa7b",
  "#f1fa8c", "#8be9fd", "#ff79c6", "#8be9fd", "#ffb86c", "#bd93f9")
t("github-black", "#000000", "#c9d1d9", "#8b949e", "#ff7b72", "#3fb950",
  "#d29922", "#58a6ff", "#bc8cff", "#39c5cf", "#ffa657", "#bc8cff")
t("github-dark", "#0d1117", "#c9d1d9", "#8b949e", "#ff7b72", "#3fb950",
  "#d29922", "#58a6ff", "#bc8cff", "#39c5cf", "#ffa657", "#bc8cff")
t("github-dark-dimmed", "#22272e", "#adbac7", "#768390", "#f47067", "#6bc46d",
  "#daaa3f", "#6cb6ff", "#dcbdfb", "#56d4dd", "#f69d50", "#dcbdfb")
t("github-dark-high-contrast", "#0a0c10", "#f0f3f6", "#9ea7b3", "#ff9492",
  "#26cd4d", "#f0b72f", "#71b7ff", "#cb9eff", "#39c5cf", "#ffb757", "#cb9eff")
t("github-dark-colorblind", "#0d1117", "#c9d1d9", "#8b949e", "#ec8e2c",
  "#58a6ff", "#d29922", "#58a6ff", "#bc8cff", "#39c5cf", "#fdac54", "#bc8cff")
t("github-minimal", "#0d1117", "#c9d1d9", "#6e7681", "#f85149", "#3fb950",
  "#d29922", "#58a6ff", "#bc8cff", "#39c5cf", "#ffa657", "#bc8cff")
t("gruvbox-dark", "#282828", "#ebdbb2", "#928374", "#fb4934", "#b8bb26",
  "#fabd2f", "#83a598", "#d3869b", "#8ec07c", "#fe8019", "#d3869b")
t("gruvbox-extra-dark", "#1d2021", "#ebdbb2", "#928374", "#fb4934", "#b8bb26",
  "#fabd2f", "#83a598", "#d3869b", "#8ec07c", "#fe8019", "#d3869b")
t("gruvbox-material-dark", "#1d2021", "#d4be98", "#7c6f64", "#ea6962",
  "#a9b665", "#d8a657", "#7daea3", "#d3869b", "#89b482", "#e78a4e", "#d3869b")
t("horizon", "#1c1e26", "#d5d8da", "#6c6f93", "#e95678", "#29d398", "#fab795",
  "#26bbd9", "#ee64ac", "#59e3e3", "#f09483", "#b877db")
t("horizon-warm", "#1c1c1c", "#d5d8da", "#6c6f93", "#e95678", "#29d398",
  "#fab795", "#26bbd9", "#ee64ac", "#59e3e3", "#f09483", "#b877db")
t("laserwave", "#27212e", "#e0dfe1", "#91889b", "#eb64b9", "#3feabf", "#ffe261",
  "#40b4c4", "#eb64b9", "#3feabf", "#ffb85b", "#b381c5")
t("material-black", "#000000", "#eeffff", "#546e7a", "#f07178", "#c3e88d",
  "#ffcb6b", "#82aaff", "#c792ea", "#89ddff", "#f78c6c", "#c792ea")
t("material-high-contrast", "#0f111a", "#ffffff", "#4f5b66", "#ff5370",
  "#c3e88d", "#ffcb6b", "#82aaff", "#c792ea", "#89ddff", "#f78c6c", "#c792ea")
t("material-ocean", "#0f111a", "#8f93a2", "#464b5d", "#f07178", "#c3e88d",
  "#ffcb6b", "#82aaff", "#c792ea", "#89ddff", "#f78c6c", "#c792ea")
t("monokai-awesome", "#272822", "#f8f8f2", "#75715e", "#f92672", "#a6e22e",
  "#e6db74", "#66d9ef", "#fd5ff0", "#66d9ef", "#fd971f", "#ae81ff")
t("monokai-black", "#000000", "#f8f8f2", "#75715e", "#f92672", "#a6e22e",
  "#e6db74", "#66d9ef", "#fd5ff0", "#66d9ef", "#fd971f", "#ae81ff")
t("monokai-night-time", "#2d2a2e", "#fcfcfa", "#727072", "#ff6188", "#a9dc76",
  "#ffd866", "#78dce8", "#ff6188", "#78dce8", "#fc9867", "#ab9df2")
t("monokai-pirokai-arctic-frost", "#1b2433", "#e6edf3", "#5b6b80", "#ff5874",
  "#addb67", "#ffd866", "#82aaff", "#c792ea", "#7fdbca", "#f78c6c", "#c792ea",
  approx=True)
t("monokai-pirokai-beach-sunset", "#2a1f26", "#f4e8e0", "#7a6a72", "#ff6188",
  "#a9dc76", "#ffd866", "#ff9e64", "#ff79c6", "#78dce8", "#fc9867", "#ab9df2",
  approx=True)
t("monokai-winter-night", "#1a1b26", "#d6dae0", "#5a6172", "#ff6188", "#a9dc76",
  "#ffd866", "#7aa2f7", "#bb9af7", "#78dce8", "#fc9867", "#ab9df2", approx=True)
t("night-owl", "#011627", "#d6deeb", "#637777", "#ef5350", "#addb67", "#c5e478",
  "#82aaff", "#c792ea", "#7fdbca", "#f78c6c", "#c792ea")
t("nord-cold", "#242933", "#d8dee9", "#4c566a", "#bf616a", "#a3be8c", "#ebcb8b",
  "#81a1c1", "#b48ead", "#88c0d0", "#d08770", "#b48ead")
t("nord-dark", "#2e3440", "#d8dee9", "#4c566a", "#bf616a", "#a3be8c", "#ebcb8b",
  "#81a1c1", "#b48ead", "#88c0d0", "#d08770", "#b48ead")
t("one-dark-pro", "#282c34", "#abb2bf", "#5c6370", "#e06c75", "#98c379",
  "#e5c07b", "#61afef", "#c678dd", "#56b6c2", "#d19a66", "#c678dd")
t("one-monokai", "#282c34", "#abb2bf", "#5c6370", "#ef596f", "#89ca78",
  "#e5c07b", "#61afef", "#c678dd", "#56b6c2", "#d19a66", "#c678dd")
t("one-monokai-darker", "#21252b", "#abb2bf", "#5c6370", "#ef596f", "#89ca78",
  "#e5c07b", "#61afef", "#c678dd", "#56b6c2", "#d19a66", "#c678dd")
t("panda-syntax", "#292a2b", "#e6e6e6", "#676b79", "#ff4b82", "#19f9d8",
  "#ffb86c", "#45a9f9", "#ff75b5", "#6fc1ff", "#ffb86c", "#b084eb")
t("poimandres-dark", "#1b1e28", "#a6accd", "#767c9d", "#d0679d", "#5de4c7",
  "#fffac2", "#add7ff", "#fcc5e9", "#5de4c7", "#f78c6c", "#a48fe1")
t("poimandres-darker", "#171922", "#a6accd", "#767c9d", "#d0679d", "#5de4c7",
  "#fffac2", "#add7ff", "#fcc5e9", "#5de4c7", "#f78c6c", "#a48fe1")
t("poimandres-black", "#000000", "#a6accd", "#767c9d", "#d0679d", "#5de4c7",
  "#fffac2", "#add7ff", "#fcc5e9", "#5de4c7", "#f78c6c", "#a48fe1")
t("seti-black", "#000000", "#cacecd", "#41535b", "#cd3f45", "#8dc149",
  "#e6cd69", "#55b5db", "#a074c4", "#55dbbe", "#db7b55", "#9068d8")
t("shades-of-purple", "#2d2b55", "#ffffff", "#a599e9", "#ff628c", "#3ad900",
  "#fad000", "#9d8df1", "#ff628c", "#80fcff", "#fb9e00", "#b362ff")
t("shades-of-purple-super-dark", "#1e1e3f", "#ffffff", "#a599e9", "#ff628c",
  "#3ad900", "#fad000", "#9d8df1", "#ff628c", "#80fcff", "#fb9e00", "#b362ff")
t("snazzy", "#282a36", "#eff0eb", "#686868", "#ff5c57", "#5af78e", "#f3f99d",
  "#57c7ff", "#ff6ac1", "#9aedfe", "#ff9f43", "#ff6ac1")
t("synthwave-84", "#262335", "#f0eff1", "#848bbd", "#fe4450", "#72f1b8",
  "#fede5d", "#03edf9", "#ff7edb", "#03edf9", "#f97e72", "#b893ce")
t("synthwave-black-no-neon", "#241b2f", "#f0eff1", "#7c7196", "#fe4450",
  "#72f1b8", "#fede5d", "#36f9f6", "#ff7edb", "#36f9f6", "#f97e72", "#b893ce")
t("tomorrow-night-minimal", "#1d1f21", "#c5c8c6", "#969896", "#cc6666",
  "#b5bd68", "#f0c674", "#81a2be", "#b294bb", "#8abeb7", "#de935f", "#b294bb")
t("xcode-catalina", "#292a30", "#dfdfe0", "#7f8c98", "#ff8170", "#78c2b3",
  "#d9c97c", "#6bdfff", "#ff7ab2", "#6bdfff", "#ffa14f", "#b281eb")
t("xcode-fusion", "#1f1f24", "#dfdfe0", "#7f8c98", "#ff8170", "#67b7a4",
  "#d9c97c", "#4eb0cc", "#ff7ab2", "#6bdfff", "#ffa14f", "#b281eb")

# ── Reconstructed palettes (no published hex — derived from source/aesthetic) ─
t("blueberry-banana", "#1a1b2e", "#e8e6f0", "#5c5f87", "#ff5c8a", "#9ee37d",
  "#ffe066", "#6c8cff", "#c792ea", "#7fe0d4", "#ffb86c", "#b48cff", approx=True)
t("calm-darkvenom", "#16161e", "#c0caf5", "#565f89", "#f7768e", "#9ece6a",
  "#e0af68", "#7aa2f7", "#bb9af7", "#7dcfff", "#ff9e64", "#bb9af7", approx=True)
t("cosmic", "#0b0c1e", "#d7d9f0", "#5a5d82", "#ff5d8f", "#5eead4", "#fbbf24",
  "#818cf8", "#e879f9", "#22d3ee", "#fb923c", "#a78bfa", approx=True)
t("dark-phoenix", "#181818", "#e6e0da", "#6e5f55", "#ff5722", "#8bc34a",
  "#ffc107", "#42a5f5", "#ec407a", "#26c6da", "#ff7043", "#ab47bc", approx=True)
t("darwin", "#1c1f26", "#cdd3de", "#5b6270", "#e06c75", "#98c379", "#e5c07b",
  "#61afef", "#c678dd", "#56b6c2", "#d19a66", "#c678dd", approx=True)
t("ethereal-aura", "#13131f", "#dcdcf0", "#56567a", "#ff7eb6", "#7ee7c7",
  "#ffd97d", "#8ab4f8", "#d7a0ff", "#7adcd8", "#ffab70", "#bda0ff", approx=True)
t("ethereal-gaze", "#0e1320", "#d2dcf0", "#4f5a7a", "#ff6f91", "#73e0b8",
  "#ffe08a", "#7cb0ff", "#c79bff", "#74d6d6", "#ff9e6b", "#a99bff", approx=True)
t("ethereal-quest", "#161420", "#e0d8f0", "#5e5680", "#ff85a1", "#8ce0a8",
  "#ffd166", "#8aa6ff", "#cf9bff", "#84dcc6", "#ffa872", "#b59bff", approx=True)
t("ethereal-zen", "#14181c", "#d6dde0", "#566066", "#e8909a", "#9cc5a1",
  "#e8c98a", "#8fb0c4", "#bda0c8", "#8fc7c0", "#e0a880", "#a99bc0", approx=True)
t("karma", "#16161c", "#cbccd1", "#555761", "#e35535", "#5fd38d", "#f2c14e",
  "#4ab1d4", "#c75ddb", "#3fd0c9", "#e8804f", "#a86fe0", approx=True)
t("lunar", "#0d1b2a", "#e0e6ed", "#52617a", "#e06c75", "#7fd1ae", "#e3c46a",
  "#5b9bd5", "#c792ea", "#69d2e7", "#e8a06a", "#9b8cff", approx=True)
t("midnight-city", "#15171c", "#cdd2da", "#545a66", "#e95f6b", "#7fc8a9",
  "#e6c068", "#5aa9e6", "#c78fe0", "#56c5c5", "#e69356", "#a97fe0", approx=True)
t("mystic-cyan", "#0a1620", "#cfe8ec", "#456370", "#ff6b81", "#5fe0c0",
  "#ffd56b", "#3fc7e6", "#9bd0ff", "#2fe0d4", "#ff9e6b", "#7fb0ff", approx=True)
t("neon-city-darkvenom", "#0d0e1a", "#e0e0f0", "#4a4d70", "#ff2e63", "#1fe0a8",
  "#ffe600", "#00b4ff", "#ff4fd9", "#00e0d4", "#ff7a45", "#b14dff", approx=True)
t("neovim", "#16161e", "#c0caf5", "#565f89", "#f7768e", "#9ece6a", "#e0af68",
  "#7aa2f7", "#bb9af7", "#7dcfff", "#ff9e64", "#bb9af7", approx=True)
t("ocean-night", "#0f1b2d", "#cdd9e5", "#4a5a70", "#e06c75", "#8fd6a9",
  "#e8c46a", "#5b9bd5", "#c792ea", "#69d2e7", "#e8a06a", "#9b8cff", approx=True)
t("outrun-space", "#0d0221", "#ffffff", "#5a4a7a", "#ff297a", "#54f6b3",
  "#ffcc00", "#2de2e6", "#ff6ac1", "#2de2e6", "#ff6611", "#9d4edd", approx=True)
t("pink-panther", "#1f1320", "#f5ddf0", "#6e5570", "#ff4d94", "#9be36b",
  "#ffd166", "#7a9bff", "#ff7ad9", "#7fe0d4", "#ff9e6b", "#d07aff", approx=True)
t("rose-noctis", "#191724", "#e0def4", "#6e6a86", "#eb6f92", "#9ccfd8",
  "#f6c177", "#3e8fb0", "#c4a7e7", "#9ccfd8", "#ea9a97", "#c4a7e7", approx=True)
t("sia-synthwave", "#1a1126", "#f6e9ff", "#5e4a78", "#ff3c8e", "#3ce8c0",
  "#ffe45e", "#5b8cff", "#ff6ad5", "#26e0e0", "#ff8c42", "#b14dff", approx=True)
t("slime", "#10160f", "#d6e6cf", "#566052", "#e8665a", "#7bd86a", "#d6c84e",
  "#5bb6a0", "#c08fd0", "#5fd0a8", "#e0954e", "#9b8cd0", approx=True)
t("slime-extra-dark", "#0a0f09", "#d6e6cf", "#4a5247", "#e8665a", "#7bd86a",
  "#d6c84e", "#5bb6a0", "#c08fd0", "#5fd0a8", "#e0954e", "#9b8cd0", approx=True)
t("stellar", "#0e1426", "#d3d9f0", "#4e5675", "#f56c8a", "#6fe0b4", "#ffd56b",
  "#6c9bff", "#c79bff", "#5fd6e0", "#ff9e6b", "#a78bff", approx=True)
t("sweet-dark", "#1a1c23", "#dee2f0", "#565a73", "#f4517a", "#54d6a0",
  "#f7c95c", "#5b9bf3", "#c792ea", "#5fd0d6", "#f78c6c", "#a78bfa", approx=True)
t("zenith", "#0f1117", "#d8dde6", "#4f5666", "#e85c6b", "#6fcf97", "#e8c46a",
  "#5b9bd5", "#bb86fc", "#56c5c5", "#e8a06a", "#bb86fc", approx=True)

# Mapping of the 92 extension entries onto the distinct palettes above
# (font-styling variants collapse; statuslines have no italic/bold/border).
FOLD_NOTE = """\
# Folded from the 92 'Best Themes Redefined' entries: Italic / Bold /
# Bordered / No-Italic variants share one palette (a statusline renders no
# italics or borders), so each distinct palette appears once here.
"""


def build_conf(name, p):
    bg, fg, cm = p["bg"], p["fg"], p["comment"]
    ctx = blend(bg, fg, 0.14)
    h5 = blend(bg, fg, 0.07)
    dim = blend(cm, fg, 0.40)  # brighten comment toward fg for readability
    approx = "  (approximated — reconstructed from source theme)" if p["approx"] else ""
    return f"""\
# coralline theme: best-themes/{name}{approx}
# Ported from the "Best Themes Redefined" VS Code extension
# (lakshits11.best-themes-redefined). Editor palette mapped to statusline roles.

# ── Accent pills ───────────────────────────────────────────────────────────────
VL_BG_DIR="{r(p['blue'])}"
VL_BG_PROJECT="{r(p['magenta'])}"
VL_BG_GIT_OK="{r(p['green'])}"
VL_BG_GIT_DIRTY="{r(p['orange'])}"
VL_BG_MODEL="{r(p['purple'])}"
VL_BG_COST="{r(p['red'])}"
VL_BG_CLOCK="{r(p['cyan'])}"
VL_BG_STYLE="{r(p['magenta'])}"
VL_BG_DURATION="{r(p['cyan'])}"

# ── Gauges — gradient lifting off the editor background ─────────────────────────
VL_BG_CTX="{rgb(ctx)}"
VL_BG_5H="{rgb(h5)}"
VL_BG_7D="{r(bg)}"
VL_BG_LINES="{rgb(ctx)}"

# ── Foregrounds ─────────────────────────────────────────────────────────────────
VL_FG_TEXT="{r(bg)}"
VL_FG_DIM="{rgb(dim)}"
VL_FG_OK="{r(p['green'])}"
VL_FG_WARN="{r(p['yellow'])}"
VL_FG_HOT="{r(p['red'])}"
"""


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    n = 0
    for name in sorted(P):
        (OUT / f"{name}.conf").write_text(build_conf(name, P[name]))
        n += 1
    print(f"wrote {n} themes to {OUT}")


if __name__ == "__main__":
    main()
