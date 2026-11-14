"""
Visualization and UI Component Module for Smart Campus Navigator
Fundamentals of AI (CF321) - Project 1

Visual Design Engine:
- Modern, premium, clean, and sophisticated university navigation system.
- Professional 2D/2.5D architectural campus map inspired by commercial navigation platforms.
- Authentic university landscape: manicured formal quads, organic canopy tree groves,
  travertine plaza with fountain, Olympic running track and pitch, scenic lake with boardwalk,
  and perimeter ring road with pedestrian crosswalks.
- Distinctive architectural university landmarks with realistic proportions, depth shadows,
  pediments, domes, skylights, and clean high-contrast readable name labels.
- Single selected route rendering with turn-by-turn glow casing, directional waypoints,
  and polished GPS location pins.
- Full Light and Dark theme support with commercial SaaS aesthetics.
- Seamless Map View / Nodes View toggle operating on the real campus graph.
- Scrollable dropdown selector supporting all campus landmarks.
"""

import pygame
import math
import time
from typing import Dict, List, Optional, Tuple, Callable, Any, Union

pygame.font.init()

# ==============================================================================
# DISPLAY NAMES MAPPING (Readable names for university landmarks)
# ==============================================================================
DISPLAY_NAMES: Dict[str, str] = {
    "MAIN_GATE": "Main Gate",
    "CS_BUILDING": "Computer Science",
    "STUDENT_CENTER": "Student Center",
    "SPORTS_COMPLEX": "Sports Complex",
    "ENGINEERING": "Engineering",
    "LIBRARY": "Library",
    "ADMINISTRATION": "Administration",
    "SCIENCE_BUILDING": "Science Building",
    "CAFETERIA": "Cafeteria",
    "DORMITORY": "Dormitory",
}

# ==============================================================================
# 1. COLOR THEMES
# ==============================================================================
THEMES = {
    "light": {
        "name": "Light Mode",
        # App Background & Navigation Surfaces
        "bg_app": (248, 250, 252),          # Ultra-clean slate-50
        "bg_header": (255, 255, 255),       # Pure white header
        "bg_card": (255, 255, 255),         # Crisp white card surface
        "bg_card_alt": (248, 250, 252),     # Soft slate-50 card surface
        "bg_card_hover": (241, 245, 249),   # Slate-100 hover state
        "border": (226, 232, 240),          # Refined 1px slate-200 border
        "border_light": (241, 245, 249),    # Subtle divider line
        "border_focus": (37, 99, 235),      # Royal blue focus ring

        # Typography
        "text_primary": (15, 23, 42),       # Deep slate-900 (crisp high contrast)
        "text_secondary": (71, 85, 105),    # Slate-600
        "text_muted": (148, 163, 184),      # Slate-400
        "text_white": (255, 255, 255),

        # Primary Brand Colors (Modern Corporate University Tier)
        "primary": (37, 99, 235),           # Royal Blue 600
        "primary_hover": (29, 78, 216),     # Royal Blue 700
        "primary_light": (239, 246, 255),   # Blue 50
        "secondary": (100, 116, 139),       # Slate 500
        "secondary_hover": (71, 85, 105),   # Slate 600
        "success": (16, 185, 129),          # Emerald 500
        "danger": (239, 68, 68),            # Rose / Red 500
        "danger_hover": (220, 38, 38),      # Rose 600
        "warning": (245, 158, 11),          # Amber 500
        "purple": (124, 58, 237),           # Violet 600
        "purple_light": (245, 243, 255),
        "orange": (234, 88, 12),            # Orange 600
        "orange_light": (255, 247, 237),
        "teal": (13, 148, 136),             # Teal 600
        "teal_light": (240, 253, 250),

        # Campus Environment & Landscape
        "map_bg": (236, 245, 234),          # Natural parkland green
        "map_lawn_dark": (216, 235, 212),   # Manicured quad turf
        "map_lawn_light": (244, 250, 242),  # Highlighted courtyard lawn
        "map_walkway": (244, 242, 236),     # Limestone paved pedestrian esplanade
        "map_walkway_border": (214, 210, 200),# Crisp walkway stone edging
        "map_walkway_closed": (254, 202, 202),
        "map_road": (80, 92, 108),          # Asphalt campus ring road
        "map_road_line": (255, 255, 255),   # Crisp white road stripes
        "map_lake": (125, 188, 225),        # Clear campus lake
        "map_lake_deep": (85, 155, 205),    # Deep water core
        "map_lake_border": (195, 218, 210), # Soft natural shore
        "map_tree": (58, 125, 78),          # Forest green canopy
        "map_tree_light": (92, 168, 106),   # Sunlit canopy highlight
        "map_tree_shadow": (196, 216, 194), # Soft ground shadow
        "map_curb": (203, 213, 225),

        # Building Art & Labels
        "bldg_facade": (252, 250, 246),     # Clean architectural sandstone
        "bldg_brick": (196, 82, 62),        # Collegiate Georgian brick
        "bldg_shadow": (195, 202, 212),     # Soft realistic drop shadow
        "bldg_border": (205, 212, 222),     # Clean architectural bevel
        "bldg_roof": (48, 82, 142),         # Deep imperial navy roof
        "bldg_roof_dome": (37, 99, 235),    # Cobalt dome
        "bldg_roof_alt": (194, 65, 45),     # Terracotta hip roof
        "bldg_roof_tech": (51, 65, 85),     # Modern dark slate tech roof
        "bldg_window": (186, 225, 250),     # Reflective daylight glass
        "bldg_label_bg": (15, 23, 42),      # High-contrast slate-900 pill
        "bldg_badge_bg": (30, 58, 138),     # Sapphire department badge

        # Route Lines (4 distinct high-visibility colors)
        "route_primary": (37, 99, 235),     # Optimal: Royal Blue
        "route_primary_glow": (191, 219, 254),
        "route_alt1": (234, 88, 12),        # Alt 1: Vibrant Sunset Orange
        "route_alt1_glow": (254, 215, 170),
        "route_alt2": (124, 58, 237),       # Alt 2: Royal Violet / Purple
        "route_alt2_glow": (221, 214, 254),
        "route_alt3": (13, 148, 136),       # Alt 3: Emerald / Teal
        "route_alt3_glow": (153, 246, 228),
        "route_alt": (234, 88, 12),         # Fallback alias

        # Nodes View Specific (Clean Blueprint / CAD Aesthetic)
        "nodes_bg": (248, 250, 252),
        "nodes_grid": (226, 232, 240),
        "node_fill": (255, 255, 255),
        "node_border": (30, 58, 138),
        "node_text": (15, 23, 42),
        "edge_line": (148, 163, 184),
        "edge_closed": (239, 68, 68),
    },
    "dark": {
        "name": "Dark Mode",
        # App Background & Navigation Surfaces
        "bg_app": (11, 15, 25),             # Deep midnight obsidian
        "bg_header": (17, 24, 39),          # Slate-900
        "bg_card": (19, 29, 49),            # Dark blue-slate card surface
        "bg_card_alt": (15, 23, 42),        # Slate-900 inner card
        "bg_card_hover": (30, 41, 59),      # Slate-800 hover
        "border": (34, 49, 78),             # Clean dark slate border
        "border_light": (26, 38, 62),
        "border_focus": (59, 130, 246),     # Luminous blue focus

        # Typography
        "text_primary": (248, 250, 252),    # Crisp pure white
        "text_secondary": (148, 163, 184),  # Slate-400
        "text_muted": (100, 116, 139),      # Slate-500
        "text_white": (255, 255, 255),

        # Primary Brand Colors
        "primary": (59, 130, 246),          # Luminous Blue 500
        "primary_hover": (37, 99, 235),     # Blue 600
        "primary_light": (30, 58, 138),
        "secondary": (148, 163, 184),
        "secondary_hover": (203, 213, 225),
        "success": (16, 185, 129),
        "danger": (248, 113, 113),
        "danger_hover": (239, 68, 68),
        "warning": (251, 191, 36),
        "purple": (167, 139, 250),
        "purple_light": (67, 30, 120),
        "orange": (251, 146, 60),
        "orange_light": (124, 45, 18),
        "teal": (45, 212, 191),
        "teal_light": (19, 78, 74),

        # Campus Environment & Landscape (Night Navigation Map)
        "map_bg": (15, 23, 24),             # Deep midnight green
        "map_lawn_dark": (12, 18, 20),      # Dark quad turf
        "map_lawn_light": (18, 28, 30),
        "map_walkway": (38, 48, 65),        # Paved walkways
        "map_walkway_border": (50, 64, 88),
        "map_walkway_closed": (127, 29, 29),
        "map_road": (22, 28, 40),           # Dark perimeter road
        "map_road_line": (100, 116, 139),
        "map_lake": (20, 50, 80),           # Dark lagoon
        "map_lake_deep": (12, 34, 58),
        "map_lake_border": (30, 65, 75),
        "map_tree": (22, 60, 42),           # Night canopy
        "map_tree_light": (35, 88, 62),
        "map_tree_shadow": (8, 14, 15),
        "map_curb": (40, 55, 75),

        # Building Art & Labels
        "bldg_facade": (34, 44, 64),        # Dark architectural granite
        "bldg_brick": (110, 45, 38),
        "bldg_shadow": (8, 12, 18),
        "bldg_border": (50, 68, 96),
        "bldg_roof": (26, 38, 68),
        "bldg_roof_dome": (45, 95, 185),
        "bldg_roof_alt": (130, 45, 35),
        "bldg_roof_tech": (28, 36, 52),
        "bldg_window": (245, 215, 130),     # Warm illuminated interior windows
        "bldg_label_bg": (15, 23, 42),
        "bldg_badge_bg": (37, 99, 235),

        # Route Lines (Luminous Neon in Dark Mode)
        "route_primary": (96, 165, 250),    # Luminous Cyan-Blue
        "route_primary_glow": (29, 78, 216),
        "route_alt1": (251, 146, 60),       # Luminous Sunset Orange
        "route_alt1_glow": (154, 52, 18),
        "route_alt2": (192, 132, 252),      # Luminous Purple
        "route_alt2_glow": (107, 33, 168),
        "route_alt3": (52, 211, 153),       # Luminous Mint / Teal
        "route_alt3_glow": (15, 118, 110),
        "route_alt": (251, 146, 60),

        # Nodes View Specific
        "nodes_bg": (13, 18, 30),
        "nodes_grid": (22, 32, 52),
        "node_fill": (19, 29, 49),
        "node_border": (96, 165, 250),
        "node_text": (248, 250, 252),
        "edge_line": (51, 65, 85),
        "edge_closed": (248, 113, 113),
    }
}


# ==============================================================================
# 2. FONT MANAGER
# ==============================================================================
class FontManager:
    _cache: Dict[Tuple[int, bool, bool], pygame.font.Font] = {}

    @classmethod
    def get(cls, size: int, bold: bool = False, italic: bool = False) -> pygame.font.Font:
        key = (size, bold, italic)
        if key not in cls._cache:
            font_names = ["Segoe UI", "SF Pro Text", "Helvetica Neue", "Arial", "sans-serif"]
            font_obj = None
            for name in font_names:
                try:
                    font_obj = pygame.font.SysFont(name, size, bold=bold, italic=italic)
                    if font_obj:
                        break
                except Exception:
                    continue
            if font_obj is None:
                font_obj = pygame.font.Font(None, size)
                font_obj.set_bold(bold)
                font_obj.set_italic(italic)
            cls._cache[key] = font_obj
        return cls._cache[key]


# ==============================================================================
# 3. DRAWING PRIMITIVES & HELPERS
# ==============================================================================
def draw_rounded_rect(
    surface: pygame.Surface,
    color: Tuple[int, int, int],
    rect: pygame.Rect,
    radius: int = 8,
    border_color: Optional[Tuple[int, int, int]] = None,
    border_width: int = 1
):
    """Draws a crisp rectangle with rounded corners and optional clean 1px border."""
    if rect.w <= 0 or rect.h <= 0:
        return
    r = max(0, min(radius, rect.w // 2, rect.h // 2))
    pygame.draw.rect(surface, color, rect, border_radius=r)
    if border_color and border_width > 0:
        pygame.draw.rect(surface, border_color, rect, width=border_width, border_radius=r)


def draw_shadowed_card(
    surface: pygame.Surface,
    rect: pygame.Rect,
    card_color: Tuple[int, int, int],
    border_color: Tuple[int, int, int],
    radius: int = 12
):
    """Draws an elevated card with subtle multi-tier soft drop shadow."""
    if rect.w <= 0 or rect.h <= 0:
        return
    # Subtle ambient shadow
    s_rect1 = pygame.Rect(rect.x + 1, rect.y + 2, rect.w, rect.h)
    draw_rounded_rect(surface, (0, 0, 0, 14), s_rect1, radius=radius + 1)
    s_rect2 = pygame.Rect(rect.x, rect.y + 1, rect.w, rect.h)
    draw_rounded_rect(surface, (0, 0, 0, 18), s_rect2, radius=radius)
    # Crisp card surface
    draw_rounded_rect(surface, card_color, rect, radius=radius, border_color=border_color, border_width=1)


# ==============================================================================
# 4. INTERACTIVE BUTTON
# ==============================================================================
class Button:
    """Modern interactive button with hover feedback, icon rendering, and clean styles."""

    def __init__(
        self,
        rect: pygame.Rect,
        text: str,
        callback: Callable[[], None],
        style: str = "primary",  # 'primary', 'secondary', 'danger_light', 'success_light', 'pill', 'outline'
        icon: Optional[str] = None,
        font_size: int = 12,
        border_radius: int = 8
    ):
        self.rect = rect
        self.text = text
        self.callback = callback
        self.style = style
        self.icon = icon
        self.font_size = font_size
        self.border_radius = border_radius
        self.is_hovered = False
        self.is_pressed = False

    def handle_event(self, event: pygame.event.Event) -> bool:
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.is_pressed = True
                return True
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.is_pressed:
                self.is_pressed = False
                if self.rect.collidepoint(event.pos):
                    if self.callback:
                        self.callback()
                    return True
        return False

    def draw(self, surface: pygame.Surface, theme: Dict[str, Any]):
        if self.style == "primary":
            bg_col = theme["primary_hover"] if self.is_hovered else theme["primary"]
            text_col = theme["text_white"]
            border_col = None
        elif self.style == "danger_light":
            bg_col = (254, 226, 226) if self.is_hovered else (254, 242, 242) if theme["name"] == "Light Mode" else (75, 20, 20)
            text_col = theme["danger"]
            border_col = (252, 165, 165) if theme["name"] == "Light Mode" else (120, 30, 30)
        elif self.style == "success_light":
            bg_col = (209, 250, 229) if self.is_hovered else (236, 253, 245) if theme["name"] == "Light Mode" else (20, 60, 45)
            text_col = (5, 150, 105) if theme["name"] == "Light Mode" else (52, 211, 153)
            border_col = (110, 231, 183) if theme["name"] == "Light Mode" else (30, 100, 70)
        elif self.style == "pill":
            bg_col = theme["bg_card_hover"] if self.is_hovered else theme["bg_card"]
            text_col = theme["text_primary"]
            border_col = theme["border"]
        elif self.style == "outline":
            bg_col = theme["bg_card_hover"] if self.is_hovered else theme["bg_card"]
            text_col = theme["text_secondary"]
            border_col = theme["border"]
        else:
            bg_col = theme["bg_card_hover"] if self.is_hovered else theme["bg_card"]
            text_col = theme["text_primary"]
            border_col = theme["border"]

        draw_rounded_rect(surface, bg_col, self.rect, self.border_radius, border_color=border_col, border_width=1)

        font = FontManager.get(self.font_size, bold=(self.style == "primary"))
        label_surf = font.render(self.text, True, text_col)

        start_x = self.rect.centerx - label_surf.get_width() // 2

        if self.icon == "search":
            ic_x = self.rect.centerx - (label_surf.get_width() + 20) // 2
            pygame.draw.circle(surface, text_col, (ic_x + 5, self.rect.centery - 2), 4, 2)
            pygame.draw.line(surface, text_col, (ic_x + 8, self.rect.centery + 1), (ic_x + 12, self.rect.centery + 5), 2)
            start_x = ic_x + 18
        elif self.icon == "nodes":
            ic_x = self.rect.centerx - (label_surf.get_width() + 20) // 2
            cy = self.rect.centery
            pygame.draw.circle(surface, text_col, (ic_x + 3, cy - 3), 2)
            pygame.draw.circle(surface, text_col, (ic_x + 12, cy - 3), 2)
            pygame.draw.circle(surface, text_col, (ic_x + 7, cy + 4), 2)
            pygame.draw.line(surface, text_col, (ic_x + 3, cy - 3), (ic_x + 7, cy + 4), 1)
            pygame.draw.line(surface, text_col, (ic_x + 12, cy - 3), (ic_x + 7, cy + 4), 1)
            start_x = ic_x + 16
        elif self.icon == "map":
            ic_x = self.rect.centerx - (label_surf.get_width() + 20) // 2
            cy = self.rect.centery
            pygame.draw.rect(surface, text_col, (ic_x + 2, cy - 5, 11, 10), 1)
            pygame.draw.line(surface, text_col, (ic_x + 5, cy - 5), (ic_x + 5, cy + 5), 1)
            pygame.draw.line(surface, text_col, (ic_x + 9, cy - 5), (ic_x + 9, cy + 5), 1)
            start_x = ic_x + 16
        elif self.icon == "close_road":
            ic_x = self.rect.centerx - (label_surf.get_width() + 18) // 2
            cy = self.rect.centery
            pygame.draw.circle(surface, text_col, (ic_x + 4, cy), 5, 1)
            pygame.draw.line(surface, text_col, (ic_x + 1, cy - 3), (ic_x + 7, cy + 3), 2)
            start_x = ic_x + 14
        elif self.icon == "reopen_road":
            ic_x = self.rect.centerx - (label_surf.get_width() + 18) // 2
            cy = self.rect.centery
            pygame.draw.arc(surface, text_col, (ic_x, cy - 5, 10, 10), 0.5, 5.5, 2)
            start_x = ic_x + 14
        elif self.icon == "history":
            ic_x = self.rect.centerx - (label_surf.get_width() + 18) // 2
            cy = self.rect.centery
            pygame.draw.circle(surface, text_col, (ic_x + 4, cy), 5, 1)
            pygame.draw.line(surface, text_col, (ic_x + 4, cy - 3), (ic_x + 4, cy), 1)
            pygame.draw.line(surface, text_col, (ic_x + 4, cy), (ic_x + 7, cy), 1)
            start_x = ic_x + 14

        label_y = self.rect.centery - label_surf.get_height() // 2
        surface.blit(label_surf, (start_x, label_y))


# ==============================================================================
# 5. DROPDOWN COMPONENT
# ==============================================================================
class Dropdown:
    """Scrollable dropdown selector supporting all campus landmarks with visible scrollbar."""

    def __init__(
        self,
        rect: pygame.Rect,
        options: List[Tuple[str, str]],
        selected_id: str,
        on_change: Optional[Callable[[str], None]] = None,
        icon_type: Optional[str] = None,
        placeholder: str = "Select..."
    ):
        self.rect = rect
        self.options = options
        self.selected_id = selected_id
        self.on_change = on_change
        self.icon_type = icon_type
        self.placeholder = placeholder
        self.is_open = False
        self.hovered_index = -1
        self.scroll_offset = 0
        self.item_height = 34
        self.max_visible = 6
        self.is_dragging_scrollbar = False

    def get_selected_label(self) -> str:
        for opt_id, label in self.options:
            if opt_id == self.selected_id:
                return label
        return self.placeholder

    def set_selected_id(self, opt_id: str):
        self.selected_id = opt_id

    def _get_dropdown_rect(self, window_height: Optional[int] = None) -> pygame.Rect:
        visible_count = min(len(self.options), self.max_visible)
        menu_h = visible_count * self.item_height
        if window_height and (self.rect.bottom + menu_h + 8 > window_height) and (self.rect.top - menu_h - 4 >= 0):
            return pygame.Rect(self.rect.x, self.rect.top - menu_h - 4, self.rect.w, menu_h)
        return pygame.Rect(self.rect.x, self.rect.bottom + 4, self.rect.w, menu_h)

    def _get_scrollbar_track(self, drop_rect: pygame.Rect) -> pygame.Rect:
        return pygame.Rect(drop_rect.right - 10, drop_rect.y + 4, 6, drop_rect.h - 8)

    def _get_scrollbar_thumb(self, drop_rect: pygame.Rect) -> pygame.Rect:
        track = self._get_scrollbar_track(drop_rect)
        total_items = max(1, len(self.options))
        visible_count = min(len(self.options), self.max_visible)
        max_scroll = max(1, total_items - visible_count)
        thumb_h = max(20, int((visible_count / total_items) * track.h))
        thumb_travel = track.h - thumb_h
        thumb_y = track.y + int((self.scroll_offset / max_scroll) * thumb_travel)
        return pygame.Rect(track.x, thumb_y, track.w, thumb_h)

    def handle_event(self, event: pygame.event.Event, window_height: Optional[int] = None) -> bool:
        max_scroll = max(0, len(self.options) - self.max_visible)

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.is_open = not self.is_open
                return True
            elif self.is_open:
                drop_rect = self._get_dropdown_rect(window_height)
                if drop_rect.collidepoint(event.pos):
                    if len(self.options) > self.max_visible:
                        track = self._get_scrollbar_track(drop_rect)
                        if track.collidepoint(event.pos):
                            self.is_dragging_scrollbar = True
                            rel_y = event.pos[1] - track.y
                            ratio = max(0.0, min(1.0, rel_y / max(1, track.h)))
                            self.scroll_offset = int(ratio * max_scroll)
                            return True

                    item_area_w = drop_rect.w - (14 if len(self.options) > self.max_visible else 0)
                    if event.pos[0] <= drop_rect.x + item_area_w:
                        clicked_idx = (event.pos[1] - drop_rect.y) // self.item_height + self.scroll_offset
                        if 0 <= clicked_idx < len(self.options):
                            self.selected_id = self.options[clicked_idx][0]
                            self.is_open = False
                            if self.on_change:
                                self.on_change(self.selected_id)
                            return True
                else:
                    self.is_open = False
                    self.is_dragging_scrollbar = False
                    return False

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.is_dragging_scrollbar:
                self.is_dragging_scrollbar = False
                return True

        elif event.type == pygame.MOUSEWHEEL and self.is_open:
            self.scroll_offset = max(0, min(max_scroll, self.scroll_offset - event.y))
            return True

        elif event.type == pygame.MOUSEMOTION and self.is_open:
            drop_rect = self._get_dropdown_rect(window_height)
            if self.is_dragging_scrollbar:
                track = self._get_scrollbar_track(drop_rect)
                thumb = self._get_scrollbar_thumb(drop_rect)
                travel = track.h - thumb.h
                if travel > 0:
                    rel_y = event.pos[1] - track.y - (thumb.h // 2)
                    ratio = max(0.0, min(1.0, rel_y / travel))
                    self.scroll_offset = int(ratio * max_scroll)
                return True

            if drop_rect.collidepoint(event.pos):
                self.hovered_index = (event.pos[1] - drop_rect.y) // self.item_height + self.scroll_offset
            else:
                self.hovered_index = -1

        return False

    def draw(self, surface: pygame.Surface, theme: Dict[str, Any]):
        border_col = theme["border_focus"] if self.is_open else theme["border"]
        draw_rounded_rect(surface, theme["bg_card"], self.rect, 8, border_color=border_col, border_width=1 if not self.is_open else 2)

        text_start_x = self.rect.x + 12
        if self.icon_type == "start_pin":
            px, py = self.rect.x + 16, self.rect.centery
            pygame.draw.circle(surface, theme["success"], (px, py), 5)
            pygame.draw.circle(surface, (255, 255, 255), (px, py), 2)
            text_start_x = self.rect.x + 30
        elif self.icon_type == "dest_pin":
            px, py = self.rect.x + 16, self.rect.centery
            pygame.draw.circle(surface, theme["danger"], (px, py), 5)
            pygame.draw.circle(surface, (255, 255, 255), (px, py), 2)
            text_start_x = self.rect.x + 30
        elif self.icon_type == "road":
            px, py = self.rect.x + 16, self.rect.centery
            pygame.draw.line(surface, theme["text_secondary"], (px - 5, py), (px + 5, py), 2)
            text_start_x = self.rect.x + 28

        font = FontManager.get(12, bold=False)
        label_text = self.get_selected_label()
        if len(label_text) > 22:
            label_text = label_text[:20] + "..."
        label_surf = font.render(label_text, True, theme["text_primary"])
        surface.blit(label_surf, (text_start_x, self.rect.centery - label_surf.get_height() // 2))

        # Chevron
        chev_x = self.rect.right - 16
        chev_y = self.rect.centery
        if self.is_open:
            pts = [(chev_x - 4, chev_y + 2), (chev_x, chev_y - 2), (chev_x + 4, chev_y + 2)]
        else:
            pts = [(chev_x - 4, chev_y - 2), (chev_x, chev_y + 2), (chev_x + 4, chev_y - 2)]
        pygame.draw.lines(surface, theme["text_secondary"], False, pts, 2)

    def draw_menu(self, surface: pygame.Surface, theme: Dict[str, Any], window_height: Optional[int] = None):
        if not self.is_open or not self.options:
            return

        drop_rect = self._get_dropdown_rect(window_height)
        draw_shadowed_card(surface, drop_rect, theme["bg_card"], theme["border"], radius=8)

        old_clip = surface.get_clip()
        surface.set_clip(drop_rect)

        font = FontManager.get(12)
        visible_count = min(len(self.options), self.max_visible)
        has_scrollbar = len(self.options) > self.max_visible
        content_w = drop_rect.w - (14 if has_scrollbar else 0)

        for i in range(visible_count):
            opt_idx = i + self.scroll_offset
            if opt_idx >= len(self.options):
                break

            opt_id, opt_label = self.options[opt_idx]
            item_rect = pygame.Rect(drop_rect.x, drop_rect.y + i * self.item_height, content_w, self.item_height)

            if opt_idx == self.hovered_index:
                draw_rounded_rect(surface, theme["bg_card_hover"], item_rect, 4)
            elif opt_id == self.selected_id:
                draw_rounded_rect(surface, theme["primary_light"], item_rect, 4)

            dot_color = theme["primary"] if opt_id == self.selected_id else theme["text_muted"]
            pygame.draw.circle(surface, dot_color, (item_rect.x + 14, item_rect.centery), 3)

            text_col = theme["primary"] if opt_id == self.selected_id else theme["text_primary"]
            txt_surf = font.render(opt_label, True, text_col)
            surface.blit(txt_surf, (item_rect.x + 24, item_rect.centery - txt_surf.get_height() // 2))

            if i < visible_count - 1:
                pygame.draw.line(surface, theme["border_light"], (item_rect.x + 8, item_rect.bottom - 1), (item_rect.right - 8, item_rect.bottom - 1), 1)

        # Draw Visible Scrollbar
        if has_scrollbar:
            track = self._get_scrollbar_track(drop_rect)
            draw_rounded_rect(surface, theme["border_light"], track, radius=3)
            thumb = self._get_scrollbar_thumb(drop_rect)
            thumb_col = theme["primary"] if self.is_dragging_scrollbar else theme["text_muted"]
            draw_rounded_rect(surface, thumb_col, thumb, radius=3)

        surface.set_clip(old_clip)


# ==============================================================================
# 6. VERTICAL ZOOM PILL
# ==============================================================================
class VerticalZoomPill:
    """Vertical unified zoom pill [ + / - ] matching modern map platforms."""

    def __init__(self, rect: pygame.Rect, on_zoom_in: Callable[[], None], on_zoom_out: Callable[[], None]):
        self.rect = rect
        self.on_zoom_in = on_zoom_in
        self.on_zoom_out = on_zoom_out
        self.top_hover = False
        self.bot_hover = False

    def handle_event(self, event: pygame.event.Event) -> bool:
        if event.type == pygame.MOUSEMOTION:
            if self.rect.collidepoint(event.pos):
                self.top_hover = event.pos[1] < self.rect.centery
                self.bot_hover = not self.top_hover
            else:
                self.top_hover = False
                self.bot_hover = False
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                if event.pos[1] < self.rect.centery:
                    self.on_zoom_in()
                else:
                    self.on_zoom_out()
                return True
        return False

    def draw(self, surface: pygame.Surface, theme: Dict[str, Any]):
        draw_shadowed_card(surface, self.rect, theme["bg_card"], theme["border"], radius=8)
        pygame.draw.line(surface, theme["border"], (self.rect.x + 3, self.rect.centery), (self.rect.right - 3, self.rect.centery), 1)

        font = FontManager.get(15, bold=True)
        p_surf = font.render("+", True, theme["primary"] if self.top_hover else theme["text_primary"])
        surface.blit(p_surf, (self.rect.centerx - p_surf.get_width() // 2, self.rect.y + 4))

        m_surf = font.render("-", True, theme["primary"] if self.bot_hover else theme["text_primary"])
        surface.blit(m_surf, (self.rect.centerx - m_surf.get_width() // 2, self.rect.centery + 3))


# ==============================================================================
# 7. CAMPUS MAP RENDERER (Commercial Grade University Navigation)
# ==============================================================================
class CampusMapRenderer:
    """
    Renders an architectural university campus navigation map:
    - Perimeter ring road with curb and pedestrian crosswalks.
    - Manicured formal quads, organic tree groves, and landscaping.
    - Central travertine plaza with tiered fountain.
    - Olympic running track, regulation soccer pitch, and campus parking bays.
    - Natural organic lake with multi-tier water depths and wooden boardwalk.
    - Authentic 2.5D architectural landmarks with distinct roofs, pediments, and cupolas.
    - Clean readable labels using human names (e.g. Main Gate, Library).
    - Single turn-by-turn route visualization with glow casing and waypoints.
    - Polished GPS origin and destination markers with soft radar rings.
    - CAD blueprint Nodes View on real graph data.
    """

    def __init__(self, map_rect: pygame.Rect):
        self.base_rect = map_rect
        self.zoom_level = 1.0
        self.pan_x = 0.0
        self.pan_y = 0.0
        self.show_labels = True
        self.show_roads = True
        self.view_mode = "map"  # 'map' or 'nodes'
        self.selected_route_idx: Optional[int] = 0

        self._update_controls()

    def _update_controls(self):
        # Bottom-right zoom pill
        zoom_rect = pygame.Rect(self.base_rect.right - 42, self.base_rect.bottom - 74, 28, 56)
        self.map_zoom_ctrl = VerticalZoomPill(zoom_rect, self.zoom_in, self.zoom_out)

        # Bottom-left view toggle button inside map
        btn_txt = "Switch to Nodes View" if self.view_mode == "map" else "Switch to Map View"
        btn_w = 170 if self.view_mode == "map" else 160
        btn_rect = pygame.Rect(self.base_rect.x + 14, self.base_rect.bottom - 46, btn_w, 32)
        self.btn_switch_view = Button(
            rect=btn_rect,
            text=btn_txt,
            callback=self.toggle_view_mode,
            style="pill",
            icon="nodes" if self.view_mode == "map" else "map",
            font_size=11,
            border_radius=8
        )

    def update_rect(self, map_rect: pygame.Rect):
        self.base_rect = map_rect
        self._update_controls()

    def toggle_view_mode(self):
        self.view_mode = "nodes" if self.view_mode == "map" else "map"
        self._update_controls()

    def set_view_mode(self, mode: str):
        if mode in ("map", "nodes"):
            self.view_mode = mode
            self._update_controls()

    def zoom_in(self):
        self.zoom_level = min(1.5, self.zoom_level + 0.1)

    def zoom_out(self):
        self.zoom_level = max(0.85, self.zoom_level - 0.1)

    def reset_view(self):
        self.zoom_level = 1.0
        self.pan_x = 0.0
        self.pan_y = 0.0

    def world_to_screen(self, norm_x: float, norm_y: float) -> Tuple[int, int]:
        """
        Projects normalized coordinates [0.0, 1.0] to screen pixels.
        Calibrated so North (MAIN_GATE at norm_y=0.91) is at the TOP
        and South (ENGINEERING at norm_y=0.16) is at the BOTTOM.
        """
        center_x = self.base_rect.centerx + self.pan_x
        center_y = self.base_rect.centery + self.pan_y

        usable_w = (self.base_rect.w - 120) * self.zoom_level
        usable_h = (self.base_rect.h - 90) * self.zoom_level

        sx = center_x + (norm_x - 0.5) * usable_w
        sy = center_y - (norm_y - 0.5) * usable_h
        return int(sx), int(sy)

    def handle_event(self, event: pygame.event.Event) -> bool:
        if self.map_zoom_ctrl.handle_event(event):
            return True
        if self.btn_switch_view.handle_event(event):
            return True
        return False

    def draw_map(
        self,
        surface: pygame.Surface,
        graph: Any,
        best_path: List[str],
        alt_paths: Union[List[List[str]], Optional[List[str]]],
        start_id: str,
        goal_id: str,
        theme: Dict[str, Any],
        selected_route_idx: Optional[int] = 0
    ):
        """Dispatches drawing to either illustrated Map View or technical Nodes View."""
        self.selected_route_idx = selected_route_idx

        # Compile all available routes in order
        all_routes = []
        if best_path and len(best_path) > 1:
            all_routes.append({
                "idx": 0,
                "path": best_path,
                "color": theme["route_primary"],
                "glow": theme["route_primary_glow"],
                "name": "Optimal Route"
            })

        alt_colors = [
            (theme["route_alt1"], theme["route_alt1_glow"]),
            (theme["route_alt2"], theme["route_alt2_glow"]),
            (theme["route_alt3"], theme["route_alt3_glow"]),
        ]

        if alt_paths:
            if len(alt_paths) > 0 and isinstance(alt_paths[0], str):
                normalized_alts: List[List[str]] = [alt_paths]  # type: ignore
            else:
                normalized_alts = alt_paths  # type: ignore
        else:
            normalized_alts = []

        for a_idx, a_path in enumerate(normalized_alts[:3]):
            if a_path and len(a_path) > 1:
                col, glow = alt_colors[a_idx % len(alt_colors)]
                all_routes.append({
                    "idx": a_idx + 1,
                    "path": a_path,
                    "color": col,
                    "glow": glow,
                    "name": f"Alternative Route {a_idx + 1}"
                })

        # Determine the single active route to draw
        active_route = None
        if all_routes and self.selected_route_idx is not None:
            if 0 <= self.selected_route_idx < len(all_routes):
                active_route = all_routes[self.selected_route_idx]
            else:
                active_route = all_routes[0]

        clip_rect = self.base_rect
        old_clip = surface.get_clip()
        surface.set_clip(clip_rect)

        if self.view_mode == "nodes":
            self._draw_nodes_view(surface, graph, active_route, start_id, goal_id, theme)
        else:
            self._draw_illustrated_map_view(surface, graph, active_route, start_id, goal_id, theme)

        # Draw Start and Destination Markers
        self._draw_markers(surface, graph, start_id, goal_id, theme, has_route=(active_route is not None))

        # Draw Compass Rose in upper-left
        self._draw_compass(surface, theme)

        # Draw Floating Controls (Zoom pill & View Switcher)
        self.map_zoom_ctrl.draw(surface, theme)
        self.btn_switch_view.draw(surface, theme)

        surface.set_clip(old_clip)

    # ==========================================================================
    # 7A. ILLUSTRATED MAP VIEW (Architectural Campus Visualization)
    # ==========================================================================
    def _draw_illustrated_map_view(
        self,
        surface: pygame.Surface,
        graph: Any,
        active_route: Optional[Dict[str, Any]],
        start_id: str,
        goal_id: str,
        theme: Dict[str, Any]
    ):
        # 1. Base Map Container (soft parkland lawn)
        draw_rounded_rect(surface, theme["map_bg"], self.base_rect, radius=14, border_color=theme["border"], border_width=1)

        # 2. Draw Decorative Features (Perimeter Road, Quads, Plaza, Fountain, Track, Lake, Tree Groves)
        self._draw_landscape(surface, theme)

        # 3. Draw Campus Walkways
        if self.show_roads:
            self._draw_walkways(surface, graph, theme)

        # 4. Draw ONLY the single active selected route (underneath buildings/labels)
        if active_route:
            self._draw_single_route(surface, graph, active_route["path"], active_route["color"], active_route["glow"], theme)

        # 5. Draw Architectural Buildings
        self._draw_buildings(surface, graph, start_id, goal_id, theme)

        # 6. Draw Closed Walkway Badges
        self._draw_closed_badges(surface, graph, theme)

    def _draw_landscape(self, surface: pygame.Surface, theme: Dict[str, Any]):
        """Renders authentic campus parkland: perimeter road, quads, central plaza, fountain, lake, and tree groves."""
        # A. Formal Campus Quads (Soft textured lawn panels)
        quad_panels = [
            (0.50, 0.57, 180, 220), # Central Quad around plaza
            (0.26, 0.52, 90, 110),  # West Quad (CS to Student Center)
            (0.76, 0.58, 90, 120),  # East Quad (Dormitory to Cafeteria)
        ]
        for qx, qy, qw, qh in quad_panels:
            qsx, qsy = self.world_to_screen(qx, qy)
            qw_px = int(qw * self.zoom_level)
            qh_px = int(qh * self.zoom_level)
            q_rect = pygame.Rect(qsx - qw_px // 2, qsy - qh_px // 2, qw_px, qh_px)
            draw_rounded_rect(surface, theme["map_lawn_dark"], q_rect, radius=16)

        # B. Outer Perimeter Campus Ring Road
        road_inset = int(14 * self.zoom_level)
        road_w = int(24 * self.zoom_level)
        r_rect = pygame.Rect(
            self.base_rect.x + road_inset,
            self.base_rect.y + road_inset,
            self.base_rect.w - 2 * road_inset,
            self.base_rect.h - 2 * road_inset
        )
        if r_rect.w > 100 and r_rect.h > 100:
            pygame.draw.rect(surface, theme["map_curb"], r_rect, width=road_w + 4, border_radius=28)
            pygame.draw.rect(surface, theme["map_road"], r_rect, width=road_w, border_radius=26)

            # White dashed centerline on perimeter road
            inner_loop = pygame.Rect(r_rect.x + road_w // 2, r_rect.y + road_w // 2, r_rect.w - road_w, r_rect.h - road_w)
            if inner_loop.w > 60 and inner_loop.h > 60:
                self._draw_dashed_rect(surface, inner_loop, theme["map_road_line"], width=2, dash=8, gap=8, radius=20)

            # Pedestrian Zebra Crosswalk at Main Gate (Top)
            gate_x, _ = self.world_to_screen(0.50, 0.91)
            cw_y = r_rect.y + road_w // 2
            for bar_x in range(gate_x - 18, gate_x + 20, 6):
                pygame.draw.line(surface, (255, 255, 255), (bar_x, cw_y - road_w // 2 + 2), (bar_x, cw_y + road_w // 2 - 2), 3)

        # C. Central Travertine Plaza & Tiered Fountain (Between Administration and Library)
        fount_sx, fount_sy = self.world_to_screen(0.50, 0.57)
        r_outer = int(46 * self.zoom_level)
        r_inner = int(22 * self.zoom_level)

        # Paved circular travertine terrace with concentric stone rings
        pygame.draw.circle(surface, theme["map_walkway_border"], (fount_sx, fount_sy), r_outer + 3)
        pygame.draw.circle(surface, theme["map_walkway"], (fount_sx, fount_sy), r_outer)
        pygame.draw.circle(surface, theme["map_lawn_dark"], (fount_sx, fount_sy), r_outer - 6, 2)
        pygame.draw.circle(surface, theme["map_walkway_border"], (fount_sx, fount_sy), r_inner + 4)

        # Fountain stone basin & water
        pygame.draw.circle(surface, (180, 205, 225), (fount_sx, fount_sy), r_inner + 2)
        pygame.draw.circle(surface, theme["map_lake"], (fount_sx, fount_sy), r_inner)
        pygame.draw.circle(surface, (255, 255, 255), (fount_sx, fount_sy), r_inner - 4, 1)

        # Fountain tiered pedestal & spray
        pygame.draw.circle(surface, theme["map_walkway_border"], (fount_sx, fount_sy), 8)
        pygame.draw.circle(surface, (255, 255, 255), (fount_sx, fount_sy), 4)
        pygame.draw.circle(surface, theme["primary"], (fount_sx, fount_sy), 2)

        # D. Olympic Running Track & Stadium at Sports Complex (Bottom-Left)
        # Positioned adjacent to the arena building so both are fully visible
        sp_sx, sp_sy = self.world_to_screen(0.20, 0.18)
        track_sx, track_sy = sp_sx - int(28 * self.zoom_level), sp_sy + int(14 * self.zoom_level)
        track_w, track_h = int(98 * self.zoom_level), int(60 * self.zoom_level)
        track_rect = pygame.Rect(track_sx - track_w // 2, track_sy - track_h // 2, track_w, track_h)

        # Red clay / terracotta rubber track
        draw_rounded_rect(surface, (194, 65, 45), track_rect, radius=26)
        for lw_off in (4, 8, 12):
            l_rect = pygame.Rect(track_rect.x + lw_off, track_rect.y + lw_off, track_w - 2 * lw_off, track_h - 2 * lw_off)
            if l_rect.w > 10 and l_rect.h > 10:
                draw_rounded_rect(surface, (255, 255, 255), l_rect, radius=max(2, 26 - lw_off), border_color=(255, 255, 255), border_width=1)

        # Regulation soccer pitch inside track
        pitch_rect = pygame.Rect(track_rect.x + 14, track_rect.y + 14, track_w - 28, track_h - 28)
        draw_rounded_rect(surface, (68, 160, 76), pitch_rect, radius=12)
        pygame.draw.line(surface, (255, 255, 255), (pitch_rect.centerx, pitch_rect.top + 2), (pitch_rect.centerx, pitch_rect.bottom - 2), 1)
        pygame.draw.circle(surface, (255, 255, 255), (pitch_rect.centerx, pitch_rect.centery), max(2, int(6 * self.zoom_level)), 1)
        pygame.draw.rect(surface, (255, 255, 255), (pitch_rect.left + 1, pitch_rect.centery - 8, 6, 16), 1)
        pygame.draw.rect(surface, (255, 255, 255), (pitch_rect.right - 7, pitch_rect.centery - 8, 6, 16), 1)

        # Parking lot adjacent to Sports Complex
        pk_sx, pk_sy = sp_sx - int(10 * self.zoom_level), sp_sy + int(48 * self.zoom_level)
        pk_w, pk_h = int(74 * self.zoom_level), int(26 * self.zoom_level)
        pk_rect = pygame.Rect(pk_sx - pk_w // 2, pk_sy - pk_h // 2, pk_w, pk_h)
        draw_rounded_rect(surface, (80, 92, 108), pk_rect, radius=4)
        for ci, cx_off in enumerate([-22, -11, 0, 11, 22]):
            pygame.draw.line(surface, (200, 212, 226), (pk_rect.centerx + cx_off, pk_rect.top + 2), (pk_rect.centerx + cx_off, pk_rect.bottom - 2), 1)
            car_col = [(220, 50, 50), (255, 255, 255), (37, 99, 235), (234, 179, 8), (51, 65, 85)][ci % 5]
            pygame.draw.rect(surface, car_col, (pk_rect.centerx + cx_off - 3, pk_rect.top + 4, 7, 10), border_radius=2)

        # E. Natural Lake & Wooden Boardwalk at Science Building (Bottom-Right)
        # Positioned to the east of Science Building so the pavilion overlooks the lake
        sb_sx, sb_sy = self.world_to_screen(0.78, 0.20)
        lake_sx, lake_sy = sb_sx + int(44 * self.zoom_level), sb_sy + int(8 * self.zoom_level)
        lake_w, lake_h = int(112 * self.zoom_level), int(72 * self.zoom_level)
        lake_rect = pygame.Rect(lake_sx - lake_w // 2, lake_sy - lake_h // 2, lake_w, lake_h)

        pygame.draw.ellipse(surface, theme["map_lake_border"], (lake_rect.x - 3, lake_rect.y - 3, lake_rect.w + 6, lake_rect.h + 6))
        pygame.draw.ellipse(surface, theme["map_lake"], lake_rect)
        deep_rect = pygame.Rect(lake_rect.x + 16, lake_rect.y + 12, lake_rect.w - 32, lake_rect.h - 24)
        if deep_rect.w > 10 and deep_rect.h > 10:
            pygame.draw.ellipse(surface, theme.get("map_lake_deep", theme["map_lake"]), deep_rect)

        # Wooden boardwalk pier extending from Science Building edge into lake
        bw_w = int(22 * self.zoom_level)
        bw_h = int(8 * self.zoom_level)
        bw_rect = pygame.Rect(lake_rect.left - int(6 * self.zoom_level), lake_rect.centery - bw_h // 2, bw_w, bw_h)
        draw_rounded_rect(surface, (168, 120, 80), bw_rect, radius=2)
        for b_x in range(bw_rect.left + 3, bw_rect.right - 2, 4):
            pygame.draw.line(surface, (120, 80, 50), (b_x, bw_rect.top), (b_x, bw_rect.bottom), 1)

        rip_col = (255, 255, 255) if theme["name"] == "Light Mode" else (70, 130, 195)
        pygame.draw.arc(surface, rip_col, (lake_rect.centerx - 18, lake_rect.centery - 8, 36, 16), 0.3, 2.6, 2)
        pygame.draw.arc(surface, rip_col, (lake_rect.centerx - 8, lake_rect.centery + 6, 24, 10), 0.5, 2.8, 1)

        # F. Cafeteria Outdoor Dining Patio (Middle-Right)
        cafe_sx, cafe_sy = self.world_to_screen(0.75, 0.44)
        patio_rect = pygame.Rect(cafe_sx - int(32 * self.zoom_level), cafe_sy + int(14 * self.zoom_level), int(64 * self.zoom_level), int(18 * self.zoom_level))
        draw_rounded_rect(surface, theme["map_walkway"], patio_rect, radius=4, border_color=theme["map_walkway_border"])
        for ox in (-20, 0, 20):
            px, py = cafe_sx + ox, patio_rect.centery
            pygame.draw.circle(surface, (180, 170, 160), (px + 1, py + 1), 5)
            umb_col = [(234, 88, 12), (37, 99, 235), (16, 185, 129)][(ox + 20) // 20 % 3]
            pygame.draw.circle(surface, umb_col, (px, py), 5)
            pygame.draw.circle(surface, (255, 255, 255), (px, py), 1)

        # G. Organic Campus Tree Groves (Varied multi-lobe canopy trees framing quads)
        tree_groves = [
            # Top entrance parkland
            (0.18, 0.78, "shade", 13), (0.34, 0.82, "ornamental", 11),
            (0.66, 0.82, "ornamental", 11), (0.82, 0.78, "shade", 13),
            # West campus quad
            (0.15, 0.52, "shade", 12), (0.36, 0.52, "shade", 14),
            # East campus quad
            (0.64, 0.58, "shade", 13), (0.85, 0.52, "ornamental", 11),
            # Central fountain plaza grove
            (0.39, 0.65, "shade", 12), (0.61, 0.65, "shade", 12),
            (0.39, 0.49, "shade", 12), (0.61, 0.49, "shade", 12),
            # South academic parkland
            (0.15, 0.32, "shade", 12), (0.36, 0.30, "shade", 13),
            (0.64, 0.34, "ornamental", 11), (0.85, 0.32, "shade", 12),
            # South border grove
            (0.38, 0.10, "shade", 13), (0.62, 0.10, "shade", 13), (0.84, 0.10, "shade", 13)
        ]
        for tx, ty, kind, base_r in tree_groves:
            tsx, tsy = self.world_to_screen(tx, ty)
            r = int(base_r * self.zoom_level)
            self._draw_organic_tree(surface, tsx, tsy, r, kind, theme)

    def _draw_organic_tree(
        self,
        surface: pygame.Surface,
        cx: int,
        cy: int,
        radius: int,
        kind: str,
        theme: Dict[str, Any]
    ):
        """Renders natural multi-lobed canopy tree with realistic ground shadow and sunlit highlight."""
        # Ground shadow
        pygame.draw.ellipse(surface, theme["map_tree_shadow"], (cx - radius, cy - radius // 2 + 3, radius * 2 + 4, radius + 4))

        canopy_col = theme["map_tree"]
        high_col = theme["map_tree_light"]
        if kind == "ornamental":
            # Soft blossom / spring green tint
            canopy_col = (72, 138, 92) if theme["name"] == "Light Mode" else (30, 75, 52)
            high_col = (110, 185, 130) if theme["name"] == "Light Mode" else (50, 115, 80)

        # Multi-lobe natural foliage
        sub_r = max(4, int(radius * 0.7))
        lobes = [
            (cx - radius // 3, cy + radius // 4, sub_r),
            (cx + radius // 3, cy + radius // 4, sub_r),
            (cx, cy - radius // 4, int(radius * 0.85)),
        ]
        for lx, ly, lr in lobes:
            pygame.draw.circle(surface, canopy_col, (lx, ly), lr)

        # Sunlit crown highlight
        hl_r = max(2, int(radius * 0.5))
        pygame.draw.circle(surface, high_col, (cx - radius // 4, cy - radius // 4), hl_r)

    def _draw_dashed_rect(self, surface: pygame.Surface, rect: pygame.Rect, color: Tuple[int, int, int], width: int = 2, dash: int = 8, gap: int = 8, radius: int = 20):
        self._draw_dashed_line(surface, (rect.left + radius, rect.top), (rect.right - radius, rect.top), color, width, dash, gap)
        self._draw_dashed_line(surface, (rect.left + radius, rect.bottom), (rect.right - radius, rect.bottom), color, width, dash, gap)
        self._draw_dashed_line(surface, (rect.left, rect.top + radius), (rect.left, rect.bottom - radius), color, width, dash, gap)
        self._draw_dashed_line(surface, (rect.right, rect.top + radius), (rect.right, rect.bottom - radius), color, width, dash, gap)

    def _draw_walkways(self, surface: pygame.Surface, graph: Any, theme: Dict[str, Any]):
        """Renders campus walkways connecting buildings with smooth joins."""
        unique_edges = graph.get_all_unique_edges()
        road_width = int(12 * self.zoom_level)
        border_width = road_width + 4

        # Pass 1: Border casings
        for walkway in unique_edges:
            loc_u = graph.get_location(walkway.u)
            loc_v = graph.get_location(walkway.v)
            if not loc_u or not loc_v:
                continue

            ux, uy = self.world_to_screen(loc_u.x, loc_u.y)
            vx, vy = self.world_to_screen(loc_v.x, loc_v.y)

            border_col = theme["danger"] if not walkway.is_open else theme["map_walkway_border"]
            pygame.draw.line(surface, border_col, (ux, uy), (vx, vy), border_width)
            pygame.draw.circle(surface, border_col, (ux, uy), border_width // 2)
            pygame.draw.circle(surface, border_col, (vx, vy), border_width // 2)

        # Pass 2: Smooth pavement fill
        for walkway in unique_edges:
            loc_u = graph.get_location(walkway.u)
            loc_v = graph.get_location(walkway.v)
            if not loc_u or not loc_v:
                continue

            ux, uy = self.world_to_screen(loc_u.x, loc_u.y)
            vx, vy = self.world_to_screen(loc_v.x, loc_v.y)

            pave_col = theme["map_walkway_closed"] if not walkway.is_open else theme["map_walkway"]
            pygame.draw.line(surface, pave_col, (ux, uy), (vx, vy), road_width)
            pygame.draw.circle(surface, pave_col, (ux, uy), road_width // 2)
            pygame.draw.circle(surface, pave_col, (vx, vy), road_width // 2)

    def _draw_single_route(
        self,
        surface: pygame.Surface,
        graph: Any,
        path: List[str],
        color: Tuple[int, int, int],
        glow_color: Tuple[int, int, int],
        theme: Dict[str, Any]
    ):
        """
        Renders ONLY the single active selected route down the centerline of walkways.
        Outer glow casing, solid vibrant route line, crisp core pinstripe, and directional waypoints.
        """
        if not path or len(path) < 2:
            return

        points = []
        for node_id in path:
            loc = graph.get_location(node_id)
            if loc:
                points.append(self.world_to_screen(loc.x, loc.y))

        if len(points) < 2:
            return

        route_width = int(6 * self.zoom_level)
        glow_width = route_width + 8

        # 1. Outer Glow Casing
        for i in range(len(points) - 1):
            p1, p2 = points[i], points[i + 1]
            pygame.draw.line(surface, glow_color, p1, p2, glow_width)
            pygame.draw.circle(surface, glow_color, p1, glow_width // 2)
            pygame.draw.circle(surface, glow_color, p2, glow_width // 2)

        # 2. Solid Vibrant Route Line
        for i in range(len(points) - 1):
            p1, p2 = points[i], points[i + 1]
            pygame.draw.line(surface, color, p1, p2, route_width)
            pygame.draw.circle(surface, color, p1, route_width // 2)
            pygame.draw.circle(surface, color, p2, route_width // 2)

        # 3. Inner Crisp Core & Directional Waypoints
        for i in range(len(points) - 1):
            p1, p2 = points[i], points[i + 1]
            pygame.draw.line(surface, (255, 255, 255), p1, p2, max(1, route_width // 3))

            mid_x = (p1[0] + p2[0]) // 2
            mid_y = (p1[1] + p2[1]) // 2
            pygame.draw.circle(surface, (255, 255, 255), (mid_x, mid_y), 4)
            pygame.draw.circle(surface, color, (mid_x, mid_y), 2)

    def _draw_buildings(self, surface: pygame.Surface, graph: Any, start_id: str, goal_id: str, theme: Dict[str, Any]):
        """
        Renders architectural university landmarks with realistic proportions,
        refined 2.5D depth, custom roofs/porticos, and high-contrast human-readable name labels.
        """
        font_label = FontManager.get(10, bold=True)
        bldg_w = int(62 * self.zoom_level)
        bldg_h = int(38 * self.zoom_level)

        for loc in graph.get_all_locations():
            bx, by = self.world_to_screen(loc.x, loc.y)

            # Drop shadow
            rect_main = pygame.Rect(bx - bldg_w // 2, by - bldg_h // 2, bldg_w, bldg_h)
            shadow_rect = pygame.Rect(rect_main.x + 2, rect_main.y + 3, bldg_w, bldg_h)
            draw_rounded_rect(surface, theme["bldg_shadow"], shadow_rect, radius=6)

            # Main Building Facade
            facade_col = theme["bldg_brick"] if loc.id in ("CAFETERIA", "DORMITORY") else theme["bldg_facade"]
            draw_rounded_rect(surface, facade_col, rect_main, radius=6, border_color=theme["bldg_border"], border_width=1)

            # Distinct Architectural Details per Landmark
            if loc.id == "MAIN_GATE":
                # Classical stone ceremonial archway
                draw_rounded_rect(surface, (244, 246, 248), rect_main, radius=6)
                pygame.draw.rect(surface, (190, 200, 212), (bx - 10, rect_main.y + 4, 20, rect_main.h - 4), border_radius=3)
                pygame.draw.rect(surface, theme["map_bg"], (bx - 6, rect_main.y + 8, 12, rect_main.h - 8), border_radius=3)
                # Gate pediment & gold finial
                pygame.draw.polygon(surface, (210, 222, 235), [(bx, rect_main.top - 6), (rect_main.x + 2, rect_main.top + 2), (rect_main.right - 2, rect_main.top + 2)])
                pygame.draw.circle(surface, theme["warning"], (bx, rect_main.top - 7), 2)

            elif loc.id == "ADMINISTRATION":
                # Stately neoclassical hall with central columns and cupola dome
                roof_h = int(12 * self.zoom_level)
                roof_rect = pygame.Rect(rect_main.x, rect_main.y, bldg_w, roof_h)
                draw_rounded_rect(surface, theme["bldg_roof"], roof_rect, radius=5)
                # Cobalt dome cupola
                dome_r = int(9 * self.zoom_level)
                pygame.draw.circle(surface, theme["bldg_roof_dome"], (bx, roof_rect.top - 2), dome_r)
                pygame.draw.circle(surface, (255, 255, 255), (bx, roof_rect.top - 2), dome_r, 1)
                pygame.draw.circle(surface, theme["warning"], (bx, roof_rect.top - dome_r - 2), 2)
                # Neoclassical columns
                for col_x in (-12, -4, 4, 12):
                    pygame.draw.line(surface, (255, 255, 255), (bx + col_x, roof_rect.bottom), (bx + col_x, rect_main.bottom - 3), 2)

            elif loc.id == "LIBRARY":
                # Grand central library with collegiate gothic terracotta roof
                roof_h = int(13 * self.zoom_level)
                roof_rect = pygame.Rect(rect_main.x, rect_main.y, bldg_w, roof_h)
                draw_rounded_rect(surface, theme["bldg_roof_alt"], roof_rect, radius=5)
                # Pediment & skylight
                pygame.draw.polygon(surface, (225, 95, 78), [(bx, roof_rect.top - 5), (bx - 12, roof_rect.top + 3), (bx + 12, roof_rect.top + 3)])
                pygame.draw.rect(surface, theme["bldg_window"], (bx - 6, roof_rect.centery - 2, 12, 4), border_radius=1)
                # Columns
                for col_x in (-14, -7, 0, 7, 14):
                    pygame.draw.line(surface, (255, 255, 255), (bx + col_x, roof_rect.bottom), (bx + col_x, rect_main.bottom - 3), 2)

            elif loc.id == "CS_BUILDING":
                # Contemporary glass tech pavilion with rooftop solar panels
                roof_h = int(12 * self.zoom_level)
                roof_rect = pygame.Rect(rect_main.x, rect_main.y, bldg_w, roof_h)
                draw_rounded_rect(surface, theme["bldg_roof_tech"], roof_rect, radius=5)
                # Solar panel grid
                for sx_off in (-14, 0, 14):
                    pygame.draw.rect(surface, (30, 58, 138), (bx + sx_off - 5, roof_rect.centery - 3, 10, 6), border_radius=1)
                    pygame.draw.rect(surface, (96, 165, 250), (bx + sx_off - 5, roof_rect.centery - 3, 10, 6), 1, border_radius=1)
                # Windows
                for wx in (-14, -5, 4, 13):
                    pygame.draw.rect(surface, theme["bldg_window"], (bx + wx, rect_main.centery, 5, 7), border_radius=1)

            elif loc.id == "ENGINEERING":
                # Industrial STEM complex with saw-tooth skylights
                roof_h = int(12 * self.zoom_level)
                roof_rect = pygame.Rect(rect_main.x, rect_main.y, bldg_w, roof_h)
                draw_rounded_rect(surface, theme["bldg_roof_tech"], roof_rect, radius=5)
                for st_x in range(roof_rect.left + 6, roof_rect.right - 6, 10):
                    pts = [(st_x, roof_rect.bottom - 2), (st_x + 5, roof_rect.top + 2), (st_x + 5, roof_rect.bottom - 2)]
                    pygame.draw.polygon(surface, theme["bldg_window"], pts)
                for wx in (-14, -4, 5, 15):
                    pygame.draw.rect(surface, theme["bldg_window"], (bx + wx - 2, by + 4, 5, 6), border_radius=1)

            elif loc.id == "SCIENCE_BUILDING":
                # Research wing overlooking the lake with bio-dome atrium
                roof_h = int(12 * self.zoom_level)
                roof_rect = pygame.Rect(rect_main.x, rect_main.y, bldg_w, roof_h)
                draw_rounded_rect(surface, theme["bldg_roof"], roof_rect, radius=5)
                dome_x = rect_main.left + 12
                pygame.draw.circle(surface, (140, 220, 240), (dome_x, roof_rect.centery), 6)
                pygame.draw.circle(surface, (255, 255, 255), (dome_x, roof_rect.centery), 6, 1)
                for wx in (2, 10, 18):
                    pygame.draw.rect(surface, theme["bldg_window"], (bx + wx, by + 3, 5, 6), border_radius=1)

            elif loc.id == "STUDENT_CENTER":
                # Modern student union with glass entrance atrium
                roof_h = int(11 * self.zoom_level)
                roof_rect = pygame.Rect(rect_main.x, rect_main.y, bldg_w, roof_h)
                draw_rounded_rect(surface, theme["bldg_roof"], roof_rect, radius=5)
                pygame.draw.rect(surface, theme["bldg_window"], (bx - 8, roof_rect.centery - 2, 16, 5), border_radius=2)
                pygame.draw.rect(surface, theme["bldg_window"], (bx - 10, rect_main.bottom - 10, 20, 8), border_radius=2)

            elif loc.id == "CAFETERIA":
                # Warm Georgian brick dining hall with awning
                roof_h = int(11 * self.zoom_level)
                roof_rect = pygame.Rect(rect_main.x, rect_main.y, bldg_w, roof_h)
                draw_rounded_rect(surface, theme["bldg_roof_alt"], roof_rect, radius=5)
                for wx in (-14, -4, 5, 15):
                    pygame.draw.rect(surface, theme["bldg_window"], (bx + wx - 2, by + 4, 5, 5), border_radius=1)

            elif loc.id == "DORMITORY":
                # Residence hall with symmetrical dormer windows
                roof_h = int(12 * self.zoom_level)
                roof_rect = pygame.Rect(rect_main.x, rect_main.y, bldg_w, roof_h)
                draw_rounded_rect(surface, theme["bldg_roof_alt"], roof_rect, radius=5)
                for dx in (-16, -6, 6, 16):
                    pygame.draw.polygon(surface, (240, 240, 240), [(bx + dx, roof_rect.top), (bx + dx - 3, roof_rect.centery), (bx + dx + 3, roof_rect.centery)])
                for wx in (-16, -6, 6, 16):
                    pygame.draw.rect(surface, theme["bldg_window"], (bx + wx - 2, by + 4, 4, 5), border_radius=1)

            else:  # SPORTS_COMPLEX
                # Barrel-vaulted arena roof
                roof_h = int(13 * self.zoom_level)
                roof_rect = pygame.Rect(rect_main.x, rect_main.y, bldg_w, roof_h)
                draw_rounded_rect(surface, (160, 175, 195), roof_rect, radius=7)
                pygame.draw.line(surface, (255, 255, 255), (roof_rect.left + 4, roof_rect.centery), (roof_rect.right - 4, roof_rect.centery), 2)
                pygame.draw.rect(surface, theme["bldg_window"], (bx - 12, rect_main.bottom - 8, 24, 6), border_radius=2)

            # High-Contrast Readable Building Name Label Pill (e.g. "Main Gate", "Library")
            if self.show_labels:
                display_label = DISPLAY_NAMES.get(loc.id, loc.name)
                txt_surf = font_label.render(display_label, True, (255, 255, 255))
                pill_w = txt_surf.get_width() + 14
                pill_h = 20

                # Clean label placement below each building footprint
                pill_y = rect_main.bottom + 4

                pill_rect = pygame.Rect(bx - pill_w // 2, pill_y, pill_w, pill_h)

                # Ambient label shadow
                pygame.draw.rect(surface, (0, 0, 0, 40), (pill_rect.x + 1, pill_rect.y + 1, pill_w, pill_h), border_radius=10)
                draw_rounded_rect(surface, theme["bldg_label_bg"], pill_rect, radius=10, border_color=(255, 255, 255), border_width=1)
                surface.blit(txt_surf, (pill_rect.centerx - txt_surf.get_width() // 2, pill_rect.centery - txt_surf.get_height() // 2))

    def _draw_closed_badges(self, surface: pygame.Surface, graph: Any, theme: Dict[str, Any]):
        for walkway in graph.get_closed_walkways():
            loc_u = graph.get_location(walkway.u)
            loc_v = graph.get_location(walkway.v)
            if not loc_u or not loc_v:
                continue

            ux, uy = self.world_to_screen(loc_u.x, loc_u.y)
            vx, vy = self.world_to_screen(loc_v.x, loc_v.y)
            mid_x = (ux + vx) // 2
            mid_y = (uy + vy) // 2

            r = int(11 * self.zoom_level)
            pygame.draw.circle(surface, (255, 255, 255), (mid_x, mid_y), r + 2)
            pygame.draw.circle(surface, theme["danger"], (mid_x, mid_y), r)

            off = int(5 * self.zoom_level)
            pygame.draw.line(surface, (255, 255, 255), (mid_x - off, mid_y - off), (mid_x + off, mid_y + off), 2)
            pygame.draw.line(surface, (255, 255, 255), (mid_x - off, mid_y + off), (mid_x + off, mid_y - off), 2)

    # ==========================================================================
    # 7B. TECHNICAL NODES VIEW (CAD / Graph Topology Visualization)
    # ==========================================================================
    def _draw_nodes_view(
        self,
        surface: pygame.Surface,
        graph: Any,
        active_route: Optional[Dict[str, Any]],
        start_id: str,
        goal_id: str,
        theme: Dict[str, Any]
    ):
        """Renders technical CAD blueprint graph visualization from real graph data."""
        draw_rounded_rect(surface, theme["nodes_bg"], self.base_rect, radius=14, border_color=theme["border"], border_width=1)

        grid_spacing = int(34 * self.zoom_level)
        grid_col = theme["nodes_grid"]
        for gx in range(self.base_rect.x, self.base_rect.right, grid_spacing):
            pygame.draw.line(surface, grid_col, (gx, self.base_rect.top), (gx, self.base_rect.bottom), 1)
        for gy in range(self.base_rect.top, self.base_rect.bottom, grid_spacing):
            pygame.draw.line(surface, grid_col, (self.base_rect.x, gy), (self.base_rect.right, gy), 1)

        # Graph Edges
        font_edge = FontManager.get(9)
        unique_edges = graph.get_all_unique_edges()

        for walkway in unique_edges:
            loc_u = graph.get_location(walkway.u)
            loc_v = graph.get_location(walkway.v)
            if not loc_u or not loc_v:
                continue

            ux, uy = self.world_to_screen(loc_u.x, loc_u.y)
            vx, vy = self.world_to_screen(loc_v.x, loc_v.y)

            if not walkway.is_open:
                self._draw_dashed_line(surface, (ux, uy), (vx, vy), theme["edge_closed"], width=3, dash_len=8, gap_len=5)
                mx, my = (ux + vx) // 2, (uy + vy) // 2
                draw_rounded_rect(surface, theme["danger"], pygame.Rect(mx - 22, my - 8, 44, 16), radius=4)
                txt_c = font_edge.render("CLOSED", True, (255, 255, 255))
                surface.blit(txt_c, (mx - txt_c.get_width() // 2, my - txt_c.get_height() // 2))
            else:
                pygame.draw.line(surface, theme["edge_line"], (ux, uy), (vx, vy), 2)
                mx, my = (ux + vx) // 2, (uy + vy) // 2
                tag_str = f"{walkway.distance_m}m"
                txt_d = font_edge.render(tag_str, True, theme["text_secondary"])
                tw, th = txt_d.get_width() + 8, txt_d.get_height() + 2
                tag_rect = pygame.Rect(mx - tw // 2, my - th // 2, tw, th)
                draw_rounded_rect(surface, theme["bg_card"], tag_rect, radius=4, border_color=theme["border"])
                surface.blit(txt_d, (tag_rect.centerx - txt_d.get_width() // 2, tag_rect.centery - txt_d.get_height() // 2))

        # Single active route line
        if active_route:
            self._draw_single_route(surface, graph, active_route["path"], active_route["color"], active_route["glow"], theme)

        # Graph Nodes with readable names
        font_node = FontManager.get(10, bold=True)
        node_r = int(16 * self.zoom_level)

        for loc in graph.get_all_locations():
            nx, ny = self.world_to_screen(loc.x, loc.y)
            is_start = (loc.id == start_id)
            is_goal = (loc.id == goal_id)

            if is_start:
                pygame.draw.circle(surface, (16, 185, 129, 80), (nx, ny), node_r + 5)
                pygame.draw.circle(surface, theme["success"], (nx, ny), node_r)
                pygame.draw.circle(surface, (255, 255, 255), (nx, ny), node_r - 4)
                pygame.draw.circle(surface, theme["success"], (nx, ny), node_r - 7)
            elif is_goal:
                pygame.draw.circle(surface, (239, 68, 68, 80), (nx, ny), node_r + 5)
                pygame.draw.circle(surface, theme["danger"], (nx, ny), node_r)
                pygame.draw.circle(surface, (255, 255, 255), (nx, ny), node_r - 4)
                pygame.draw.circle(surface, theme["danger"], (nx, ny), node_r - 7)
            else:
                pygame.draw.circle(surface, theme["node_border"], (nx, ny), node_r, 2)
                pygame.draw.circle(surface, theme["node_fill"], (nx, ny), node_r - 2)
                pygame.draw.circle(surface, theme["primary"], (nx, ny), 3)

            # Node Label Pill
            lbl_str = DISPLAY_NAMES.get(loc.id, loc.id)
            txt_lbl = font_node.render(lbl_str, True, (255, 255, 255))
            pw, ph = txt_lbl.get_width() + 12, 18
            p_rect = pygame.Rect(nx - pw // 2, ny + node_r + 4, pw, ph)
            p_col = theme["success"] if is_start else theme["danger"] if is_goal else theme["bldg_label_bg"]
            draw_rounded_rect(surface, p_col, p_rect, radius=9, border_color=(255, 255, 255), border_width=1)
            surface.blit(txt_lbl, (p_rect.centerx - txt_lbl.get_width() // 2, p_rect.centery - txt_lbl.get_height() // 2))

    def _draw_dashed_line(
        self,
        surface: pygame.Surface,
        p1: Tuple[int, int],
        p2: Tuple[int, int],
        color: Tuple[int, int, int],
        width: int = 3,
        dash_len: int = 8,
        gap_len: int = 5
    ):
        dx = p2[0] - p1[0]
        dy = p2[1] - p1[1]
        dist = math.hypot(dx, dy)
        step = dash_len + gap_len
        num_steps = int(dist // step)
        for s in range(num_steps + 1):
            t1 = (s * step) / dist if dist > 0 else 0
            t2 = min(1.0, ((s * step) + dash_len) / dist) if dist > 0 else 1.0
            d1 = (int(p1[0] + dx * t1), int(p1[1] + dy * t1))
            d2 = (int(p1[0] + dx * t2), int(p1[1] + dy * t2))
            pygame.draw.line(surface, color, d1, d2, width)

    # ==========================================================================
    # 7C. POLISHED MARKERS & FLOATING CONTROLS
    # ==========================================================================
    def _draw_markers(self, surface: pygame.Surface, graph: Any, start_id: str, goal_id: str, theme: Dict[str, Any], has_route: bool = True):
        """Renders polished GPS Start (Emerald) and Destination (Ruby) location pins."""
        bldg_h = int(38 * self.zoom_level)

        # Start Marker (Emerald Pin)
        loc_s = graph.get_location(start_id)
        if loc_s:
            sx, sy = self.world_to_screen(loc_s.x, loc_s.y)
            roof_top_y = sy - bldg_h // 2
            pin_y = roof_top_y - 14

            pulse = (math.sin(time.time() * 4.0) + 1.0) * 0.5
            r_radar = int(10 + pulse * 4)
            pygame.draw.circle(surface, (16, 185, 129, 50), (sx, pin_y), max(1, r_radar))
            # Drop shadow
            pygame.draw.circle(surface, (0, 0, 0, 40), (sx + 1, pin_y + 2), 9)
            # Pin body
            pygame.draw.circle(surface, theme["success"], (sx, pin_y), 9)
            pygame.draw.polygon(surface, theme["success"], [(sx - 5, pin_y + 2), (sx + 5, pin_y + 2), (sx, roof_top_y - 1)])
            pygame.draw.circle(surface, (255, 255, 255), (sx, pin_y), 4)
            pygame.draw.circle(surface, theme["success"], (sx, pin_y), 2)

        # Destination Marker (Ruby Pin)
        loc_g = graph.get_location(goal_id)
        if loc_g and goal_id != start_id:
            gx, gy = self.world_to_screen(loc_g.x, loc_g.y)
            roof_top_y = gy - bldg_h // 2
            pin_y = roof_top_y - 14

            pulse = (math.sin(time.time() * 4.0 + 1.5) + 1.0) * 0.5
            r_radar = int(10 + pulse * 4)
            pygame.draw.circle(surface, (239, 68, 68, 50), (gx, pin_y), max(1, r_radar))
            # Drop shadow
            pygame.draw.circle(surface, (0, 0, 0, 40), (gx + 1, pin_y + 2), 9)
            # Pin body
            pygame.draw.circle(surface, theme["danger"], (gx, pin_y), 9)
            pygame.draw.polygon(surface, theme["danger"], [(gx - 5, pin_y + 2), (gx + 5, pin_y + 2), (gx, roof_top_y - 1)])
            pygame.draw.circle(surface, (255, 255, 255), (gx, pin_y), 4)
            pygame.draw.circle(surface, theme["danger"], (gx, pin_y), 2)

    def _draw_compass(self, surface: pygame.Surface, theme: Dict[str, Any]):
        """Renders minimalist modern navigation compass in upper-left of map panel."""
        cx = self.base_rect.x + 32
        cy = self.base_rect.top + 32
        r = 16

        draw_shadowed_card(surface, pygame.Rect(cx - r, cy - r, 2 * r, 2 * r), theme["bg_card"], theme["border"], radius=r)

        pygame.draw.polygon(surface, theme["primary"], [(cx, cy - 11), (cx - 3, cy), (cx + 3, cy)])
        pygame.draw.polygon(surface, theme["danger"], [(cx, cy - 11), (cx - 2, cy - 6), (cx + 2, cy - 6)])
        pygame.draw.polygon(surface, theme["text_muted"], [(cx, cy + 11), (cx - 3, cy), (cx + 3, cy)])

        font = FontManager.get(9, bold=True)
        txt = font.render("N", True, theme["danger"])
        surface.blit(txt, (cx - txt.get_width() // 2, cy - 22))
