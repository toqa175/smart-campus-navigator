"""
Smart Campus Navigator - Main Application
Fundamentals of AI (CF321) - Project 1

Main desktop application powered by Pygame and custom A* search.
Commercial-grade university navigation system:
- Top Header: Sleek university crest, live AI status indicator, and Apple-style segmented Light/Dark toggle.
- Left Column: Route Planner, View Mode segmented switch, Walkway Controls, and Route Legend.
- Center Column: Maximized dynamic Campus Map with 2.5D architectural landmarks, Compass, Zoom, and View Switcher.
- Right Column: Route Analysis with featured Optimal Route hero card (distance, walking time, stops, breadcrumb timeline)
  and Alternative Route cards with distance diff badges.
"""

import sys
import os
import math
import time
import pygame
from typing import Dict, List, Optional, Tuple, Any

from campus_map import CampusGraph
from astar import SearchResult
from alternative_routes import RouteManager, RouteComparison
from visualization import (
    THEMES,
    FontManager,
    DISPLAY_NAMES,
    draw_rounded_rect,
    draw_shadowed_card,
    Button,
    Dropdown,
    CampusMapRenderer,
)


class SmartCampusNavigatorApp:
    """Main Application Controller with 3-column dashboard matching commercial navigation platform standards."""

    def __init__(self, target_w: Optional[int] = None, target_h: Optional[int] = None):
        os.environ['SDL_VIDEO_CENTERED'] = '1'
        pygame.init()
        pygame.display.set_caption("Smart Campus Navigator — University Campus")

        info = pygame.display.Info()
        screen_w = info.current_w if (info.current_w and info.current_w > 0) else 1366
        screen_h = info.current_h if (info.current_h and info.current_h > 0) else 768

        # Target window bounds
        if target_w and target_h:
            self.WINDOW_WIDTH = target_w
            self.WINDOW_HEIGHT = target_h
        else:
            self.WINDOW_WIDTH = max(1120, min(1440, screen_w - 40))
            self.WINDOW_HEIGHT = max(680, min(860, screen_h - 60))

        self.screen = pygame.display.set_mode((self.WINDOW_WIDTH, self.WINDOW_HEIGHT), pygame.RESIZABLE)
        self.clock = pygame.time.Clock()
        self.running = True

        # Graph and Route Manager
        self.graph = CampusGraph()
        self.manager = RouteManager(self.graph)

        # Application State
        self.current_theme_name = "light"
        self.start_location_id = "MAIN_GATE"
        self.dest_location_id = "LIBRARY"
        self.cost_metric = "distance"

        # Route Results
        self.route_comparison: Optional[RouteComparison] = None
        self.best_route: Optional[SearchResult] = None
        self.alternative_routes: List[SearchResult] = []
        self.selected_route_idx: Optional[int] = 0  # 0: opt, 1: alt1, 2: alt2, 3: alt3
        self.status_message = "Ready to plan route."
        self.route_card_rects: List[pygame.Rect] = []

        # Road Controls State
        self.selected_walkway_key: str = "MAIN_GATE-ADMINISTRATION"
        self.show_history_modal = False

        # Scrolling in right panel / cards if needed
        self.right_scroll_y = 0

        # Build UI layout and controls
        self.map_renderer: Optional[CampusMapRenderer] = None
        self._compute_layout()
        self._init_ui_controls()

        # Compute initial route
        self.calculate_route()

    def _compute_layout(self):
        """Calculates geometry for 3-column layout matching reference design."""
        W = self.WINDOW_WIDTH
        H = self.WINDOW_HEIGHT

        self.header_h = 56
        self.margin_x = 12
        self.gap = 10
        self.margin_bottom = 12

        # Available content dimensions
        avail_h = H - self.header_h - self.margin_bottom
        self.content_y = self.header_h + 8
        self.col_h = max(580, avail_h - 8)

        # 3 Column Widths - Optimized to maximize center map space while ensuring rich card presentation
        self.left_w = 224
        self.right_w = 286
        self.map_w = W - (2 * self.margin_x) - (2 * self.gap) - self.left_w - self.right_w

        # Panel Rectangles on screen
        self.left_col_rect = pygame.Rect(self.margin_x, self.content_y, self.left_w, self.col_h)
        self.map_rect = pygame.Rect(self.left_col_rect.right + self.gap, self.content_y, self.map_w, self.col_h)
        self.right_col_rect = pygame.Rect(self.map_rect.right + self.gap, self.content_y, self.right_w, self.col_h)

        if self.map_renderer is None:
            self.map_renderer = CampusMapRenderer(self.map_rect)
        else:
            self.map_renderer.update_rect(self.map_rect)

        # Header interactive rects (Apple-style segmented toggle)
        self.theme_toggle_rect = pygame.Rect(W - 146, 12, 134, 32)

        # Update widget rects
        self._update_widget_rects()

    def _init_ui_controls(self):
        """Constructs all interactive widgets."""
        all_locs = self.graph.get_all_locations()
        # Use human-readable names for UI display while preserving internal IDs
        self.loc_options = [(loc.id, DISPLAY_NAMES.get(loc.id, loc.name)) for loc in all_locs]

        # Left Panel - Dropdowns
        self.start_dropdown = Dropdown(
            rect=pygame.Rect(0, 0, 10, 10),
            options=self.loc_options,
            selected_id=self.start_location_id,
            on_change=self._on_start_changed,
            icon_type="start_pin"
        )

        self.dest_dropdown = Dropdown(
            rect=pygame.Rect(0, 0, 10, 10),
            options=self.loc_options,
            selected_id=self.dest_location_id,
            on_change=self._on_dest_changed,
            icon_type="dest_pin"
        )

        # Find Routes button
        self.btn_find = Button(
            rect=pygame.Rect(0, 0, 10, 10),
            text="Find Routes",
            callback=self.calculate_route,
            style="primary",
            icon="search",
            font_size=13,
            border_radius=8
        )

        # Map View / Nodes View segmented buttons in left panel
        self.btn_map_view = Button(
            rect=pygame.Rect(0, 0, 10, 10),
            text="Map View",
            callback=lambda: self._set_map_view_mode("map"),
            style="primary" if self.map_renderer.view_mode == "map" else "outline",
            icon="map",
            font_size=12,
            border_radius=8
        )
        self.btn_nodes_view = Button(
            rect=pygame.Rect(0, 0, 10, 10),
            text="Nodes View",
            callback=lambda: self._set_map_view_mode("nodes"),
            style="primary" if self.map_renderer.view_mode == "nodes" else "outline",
            icon="nodes",
            font_size=12,
            border_radius=8
        )

        # Walkway Controls
        self._refresh_walkway_options()
        self.road_dropdown = Dropdown(
            rect=pygame.Rect(0, 0, 10, 10),
            options=self.walkway_options,
            selected_id=self.selected_walkway_key,
            on_change=self._on_road_selected,
            icon_type="road"
        )
        self.btn_close_road = Button(
            rect=pygame.Rect(0, 0, 10, 10),
            text="Close Road",
            callback=self._close_selected_road,
            style="danger_light",
            icon="close_road",
            font_size=11,
            border_radius=8
        )
        self.btn_reopen_road = Button(
            rect=pygame.Rect(0, 0, 10, 10),
            text="Reopen Road",
            callback=self._reopen_selected_road,
            style="success_light",
            icon="reopen_road",
            font_size=11,
            border_radius=8
        )
        self.btn_road_history = Button(
            rect=pygame.Rect(0, 0, 10, 10),
            text="Road History",
            callback=self._open_history_modal,
            style="pill",
            icon="history",
            font_size=12,
            border_radius=8
        )

        # Route select buttons for cards (up to 4 routes: optimal + 3 alternatives)
        self.route_select_buttons: List[Button] = []
        for i in range(4):
            btn = Button(
                rect=pygame.Rect(0, 0, 10, 10),
                text="Select",
                callback=lambda idx=i: self._select_route(idx),
                style="outline",
                font_size=10,
                border_radius=6
            )
            self.route_select_buttons.append(btn)

        # Dropdowns list for click handling and z-order drawing
        self.all_dropdowns = [
            self.start_dropdown,
            self.dest_dropdown,
            self.road_dropdown,
        ]

        self._update_widget_rects()

    def _update_widget_rects(self):
        """Aligns all widget rects to current layout dimensions."""
        if not hasattr(self, "btn_find"):
            return

        lx = self.left_col_rect.x + 10
        lw = self.left_col_rect.w - 20
        ly = self.left_col_rect.y

        # Card 1: Route Planner (y: ly, h: 204)
        self.start_dropdown.rect = pygame.Rect(lx, ly + 52, lw, 32)
        self.dest_dropdown.rect = pygame.Rect(lx, ly + 110, lw, 32)
        self.btn_find.rect = pygame.Rect(lx, ly + 154, lw, 36)

        # Card 2: View Mode (y: ly + 214, h: 80)
        c2_y = ly + 214
        half_w = (lw - 6) // 2
        self.btn_map_view.rect = pygame.Rect(lx, c2_y + 34, half_w, 32)
        self.btn_nodes_view.rect = pygame.Rect(lx + half_w + 6, c2_y + 34, half_w, 32)

        # Card 3: Road Controls (y: ly + 304, h: 152)
        c3_y = ly + 304
        self.road_dropdown.rect = pygame.Rect(lx, c3_y + 34, lw, 32)
        self.btn_close_road.rect = pygame.Rect(lx, c3_y + 74, half_w, 30)
        self.btn_reopen_road.rect = pygame.Rect(lx + half_w + 6, c3_y + 74, half_w, 30)
        self.btn_road_history.rect = pygame.Rect(lx, c3_y + 110, lw, 28)

    def on_resize(self, new_w: int, new_h: int):
        self.WINDOW_WIDTH = max(1000, new_w)
        self.WINDOW_HEIGHT = max(600, new_h)
        self.screen = pygame.display.set_mode((self.WINDOW_WIDTH, self.WINDOW_HEIGHT), pygame.RESIZABLE)
        self._compute_layout()

    def _refresh_walkway_options(self):
        options = []
        for w in self.graph.get_all_unique_edges():
            key = f"{w.u}-{w.v}"
            status = " [CLOSED]" if not w.is_open else ""
            u_name = DISPLAY_NAMES.get(w.u, w.u)
            v_name = DISPLAY_NAMES.get(w.v, w.v)
            label = f"{u_name} ↔ {v_name}{status}"
            options.append((key, label))
        self.walkway_options = options
        if hasattr(self, "road_dropdown"):
            self.road_dropdown.options = options

    def _on_start_changed(self, new_id: str):
        self.start_location_id = new_id

    def _on_dest_changed(self, new_id: str):
        self.dest_location_id = new_id

    def _on_road_selected(self, new_key: str):
        self.selected_walkway_key = new_key

    def _set_map_view_mode(self, mode: str):
        self.map_renderer.set_view_mode(mode)
        self.btn_map_view.style = "primary" if mode == "map" else "outline"
        self.btn_nodes_view.style = "primary" if mode == "nodes" else "outline"

    def _select_route(self, route_idx: int):
        self.selected_route_idx = route_idx
        route_name = "Optimal Route" if route_idx == 0 else f"Alternative Route {route_idx}"
        self.status_message = f"Displaying {route_name} on map."

    def _close_selected_road(self):
        if not self.selected_walkway_key:
            return
        parts = self.selected_walkway_key.split("-")
        if len(parts) == 2:
            self.manager.close_road(parts[0], parts[1])
            self._refresh_walkway_options()
            self.calculate_route()

    def _reopen_selected_road(self):
        if not self.selected_walkway_key:
            return
        parts = self.selected_walkway_key.split("-")
        if len(parts) == 2:
            self.manager.reopen_road(parts[0], parts[1])
            self._refresh_walkway_options()
            self.calculate_route()

    def _open_history_modal(self):
        self.show_history_modal = True

    def toggle_theme(self):
        self.current_theme_name = "dark" if self.current_theme_name == "light" else "light"

    def calculate_route(self):
        """Calculates optimal A* route and up to 3 distinct valid alternative routes."""
        comparison = self.manager.find_best_and_alternatives(
            self.start_location_id,
            self.dest_location_id,
            cost_metric=self.cost_metric,
            max_alternatives=3
        )
        self.route_comparison = comparison
        self.best_route = comparison.best_route
        self.alternative_routes = comparison.alternative_routes

        if not self.best_route.found:
            self.selected_route_idx = None
            if self.start_location_id == self.dest_location_id:
                self.status_message = "Start and destination are identical."
            else:
                self.status_message = "No valid path found! Walkways are blocked."
        else:
            self.selected_route_idx = 0  # CRITICAL: Always reset to Optimal Route on calculation
            alt_count = len(self.alternative_routes)
            self.status_message = f"Found optimal route and {alt_count} alternative route(s)."

    # ==========================================================================
    # EVENT LOOP
    # ==========================================================================
    def run(self):
        while self.running:
            theme = THEMES[self.current_theme_name]

            # Sync segmented buttons style with map renderer view_mode
            current_mode = self.map_renderer.view_mode
            self.btn_map_view.style = "primary" if current_mode == "map" else "outline"
            self.btn_nodes_view.style = "primary" if current_mode == "nodes" else "outline"

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

                elif event.type == pygame.VIDEORESIZE:
                    self.on_resize(event.w, event.h)

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        if self.show_history_modal:
                            self.show_history_modal = False
                        else:
                            for d in self.all_dropdowns:
                                d.is_open = False
                    elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        self.calculate_route()
                    elif event.key == pygame.K_t:
                        self.toggle_theme()
                    elif event.key in (pygame.K_PLUS, pygame.K_EQUALS):
                        self.map_renderer.zoom_in()
                    elif event.key == pygame.K_MINUS:
                        self.map_renderer.zoom_out()

                elif event.type == pygame.MOUSEWHEEL:
                    open_dropdown = next((d for d in self.all_dropdowns if d.is_open), None)
                    if open_dropdown:
                        open_dropdown.handle_event(event, self.WINDOW_HEIGHT)
                    else:
                        # Scroll right panel results if mouse is over right column
                        if self.right_col_rect.collidepoint(pygame.mouse.get_pos()):
                            self.right_scroll_y = max(0, min(360, self.right_scroll_y - event.y * 24))

                elif event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.MOUSEMOTION):
                    pos = event.pos

                    # Modal handling
                    if self.show_history_modal:
                        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                            self._handle_history_modal_click(pos)
                        continue

                    # Header click (Theme toggle)
                    if pos[1] < self.header_h:
                        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                            if self.theme_toggle_rect.collidepoint(pos):
                                self.toggle_theme()
                                for d in self.all_dropdowns:
                                    d.is_open = False
                        continue

                    # Check open dropdown first (highest priority)
                    handled = False
                    for d in reversed(self.all_dropdowns):
                        if d.is_open:
                            if d.handle_event(event, self.WINDOW_HEIGHT):
                                handled = True
                                break

                    if not handled:
                        # Check dropdown openers
                        for d in self.all_dropdowns:
                            if d.handle_event(event, self.WINDOW_HEIGHT):
                                handled = True
                                break

                    if not handled:
                        # Left panel controls
                        self.btn_find.handle_event(event)
                        self.btn_map_view.handle_event(event)
                        self.btn_nodes_view.handle_event(event)
                        self.btn_close_road.handle_event(event)
                        self.btn_reopen_road.handle_event(event)
                        self.btn_road_history.handle_event(event)

                        # Center map controls
                        self.map_renderer.handle_event(event)

                        # Right panel route cards click handling
                        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                            if self.right_col_rect.collidepoint(pos):
                                for c_idx, c_rect in enumerate(self.route_card_rects):
                                    if c_rect.collidepoint(pos):
                                        self._select_route(c_idx)
                                        handled = True
                                        break

                        if not handled:
                            for r_btn in self.route_select_buttons:
                                r_btn.handle_event(event)

            self.draw(theme)
            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()
        sys.exit(0)

    # ==========================================================================
    # DRAWING & RENDERING
    # ==========================================================================
    def draw(self, theme: Dict[str, Any]):
        self.screen.fill(theme["bg_app"])

        # 1. Draw Top Header Bar
        self._draw_header(theme)

        # 2. Draw Left Column (Route Planner, View Mode toggle, Road Controls, Legend)
        self._draw_left_column(theme)

        # 3. Draw Center Map Visualization (Map View or Nodes View)
        best_p = self.best_route.path if (self.best_route and self.best_route.found) else []
        alt_paths_list = [r.path for r in self.alternative_routes if r.found]

        self.map_renderer.draw_map(
            self.screen,
            self.graph,
            best_p,
            alt_paths_list,
            self.start_location_id,
            self.dest_location_id,
            theme,
            selected_route_idx=self.selected_route_idx
        )

        # 4. Draw Right Column (Route Results with featured Optimal card and Alternatives)
        self._draw_right_column(theme)

        # 5. Render Open Floating Dropdown Menus on Top
        for d in self.all_dropdowns:
            d.draw_menu(self.screen, theme, self.WINDOW_HEIGHT)

        # 6. Render Road History Modal if active
        if self.show_history_modal:
            self._draw_history_modal(theme)

    def _draw_header(self, theme: Dict[str, Any]):
        """Renders modern navigation header with university emblem, AI status pill, and Apple-style toggle."""
        W = self.WINDOW_WIDTH
        header_rect = pygame.Rect(0, 0, W, self.header_h)
        pygame.draw.rect(self.screen, theme["bg_header"], header_rect)
        pygame.draw.line(self.screen, theme["border"], (0, self.header_h), (W, self.header_h), 1)

        # University Crest / Shield Emblem
        cx, cy = 28, 28
        shield_pts = [
            (cx - 13, cy - 14),
            (cx + 13, cy - 14),
            (cx + 13, cy + 2),
            (cx, cy + 15),
            (cx - 13, cy + 2)
        ]
        shadow_pts = [(p[0] + 1, p[1] + 1) for p in shield_pts]
        pygame.draw.polygon(self.screen, (0, 0, 0, 40) if theme["name"] == "Light Mode" else (0, 0, 0, 100), shadow_pts)
        pygame.draw.polygon(self.screen, theme["primary"], shield_pts)
        pygame.draw.polygon(self.screen, (255, 255, 255), shield_pts, 1)

        # Star / Compass Emblem inside shield
        pygame.draw.line(self.screen, (255, 255, 255), (cx, cy - 8), (cx, cy + 6), 2)
        pygame.draw.line(self.screen, (255, 255, 255), (cx - 7, cy - 1), (cx + 7, cy - 1), 2)
        pygame.draw.circle(self.screen, theme["warning"], (cx, cy - 1), 2)

        # Header Title
        font_title = FontManager.get(17, bold=True)
        t_surf = font_title.render("Smart Campus Navigator", True, theme["text_primary"])
        self.screen.blit(t_surf, (50, 10))

        # Live AI Status Indicator Badge
        status_x = 50 + t_surf.get_width() + 14
        status_rect = pygame.Rect(status_x, 12, 126, 22)
        bg_status = (236, 253, 245) if theme["name"] == "Light Mode" else (6, 78, 59)
        border_status = (167, 243, 208) if theme["name"] == "Light Mode" else (16, 185, 129)
        draw_rounded_rect(self.screen, bg_status, status_rect, radius=11, border_color=border_status, border_width=1)

        pulse = (math.sin(time.time() * 4.0) + 1.0) * 0.5
        dot_r = int(3 + pulse * 1.5)
        pygame.draw.circle(self.screen, (16, 185, 129), (status_rect.x + 10, status_rect.centery), max(2, dot_r))
        font_badge = FontManager.get(10, bold=True)
        txt_status = font_badge.render("AI Engine Active", True, (5, 150, 105) if theme["name"] == "Light Mode" else (52, 211, 153))
        self.screen.blit(txt_status, (status_rect.x + 18, status_rect.centery - txt_status.get_height() // 2))

        # Subtitle
        font_sub = FontManager.get(11)
        sub_text = "Intelligent University Wayfinding & Route Optimization"
        s_surf = font_sub.render(sub_text, True, theme["text_secondary"])
        self.screen.blit(s_surf, (50, 32))

        # Segmented Light / Dark Toggle Switch Pill
        t_rect = self.theme_toggle_rect
        draw_rounded_rect(self.screen, theme["bg_card"], t_rect, radius=16, border_color=theme["border"], border_width=1)

        if self.current_theme_name == "light":
            sun_pill = pygame.Rect(t_rect.x + 2, t_rect.y + 2, 64, t_rect.h - 4)
            draw_rounded_rect(self.screen, theme["primary_light"], sun_pill, radius=14, border_color=theme["border_focus"], border_width=1)
            pygame.draw.circle(self.screen, theme["warning"], (sun_pill.x + 13, sun_pill.centery), 4)
            font_pill = FontManager.get(11, bold=True)
            self.screen.blit(font_pill.render("Light", True, theme["primary"]), (sun_pill.x + 23, sun_pill.centery - 7))

            pygame.draw.circle(self.screen, theme["text_muted"], (t_rect.right - 18, t_rect.centery), 4)
            font_dim = FontManager.get(10)
            self.screen.blit(font_dim.render("Dark", True, theme["text_secondary"]), (t_rect.right - 48, t_rect.centery - 6))
        else:
            moon_pill = pygame.Rect(t_rect.right - 66, t_rect.y + 2, 64, t_rect.h - 4)
            draw_rounded_rect(self.screen, theme["primary_light"], moon_pill, radius=14, border_color=theme["border_focus"], border_width=1)
            pygame.draw.circle(self.screen, theme["primary"], (moon_pill.x + 13, moon_pill.centery), 4)
            font_pill = FontManager.get(11, bold=True)
            self.screen.blit(font_pill.render("Dark", True, theme["text_primary"]), (moon_pill.x + 23, moon_pill.centery - 7))

            font_dim = FontManager.get(10)
            self.screen.blit(font_dim.render("Light", True, theme["text_secondary"]), (t_rect.x + 14, t_rect.centery - 6))

    def _draw_left_column(self, theme: Dict[str, Any]):
        """Renders Left Column cards: Route Planner, View Mode toggle, Road Controls, Legend."""
        lx = self.left_col_rect.x
        lw = self.left_col_rect.w
        ly = self.left_col_rect.y

        # ----------------------------------------------------------------------
        # Card 1: Route Planner
        # ----------------------------------------------------------------------
        c1_rect = pygame.Rect(lx, ly, lw, 204)
        draw_shadowed_card(self.screen, c1_rect, theme["bg_card"], theme["border"], radius=14)

        font_card_h = FontManager.get(13, bold=True)
        pygame.draw.circle(self.screen, theme["primary"], (c1_rect.x + 20, c1_rect.y + 20), 8)
        pygame.draw.circle(self.screen, (255, 255, 255), (c1_rect.x + 20, c1_rect.y + 20), 3)
        self.screen.blit(font_card_h.render("Route Planner", True, theme["text_primary"]), (c1_rect.x + 34, c1_rect.y + 12))

        font_lbl = FontManager.get(10, bold=True)
        pygame.draw.circle(self.screen, theme["success"], (c1_rect.x + 18, c1_rect.y + 42), 3)
        self.screen.blit(font_lbl.render("START LOCATION", True, theme["text_secondary"]), (c1_rect.x + 26, c1_rect.y + 36))
        self.start_dropdown.draw(self.screen, theme)

        pygame.draw.circle(self.screen, theme["danger"], (c1_rect.x + 18, c1_rect.y + 100), 3)
        self.screen.blit(font_lbl.render("DESTINATION", True, theme["text_secondary"]), (c1_rect.x + 26, c1_rect.y + 94))
        self.dest_dropdown.draw(self.screen, theme)

        self.btn_find.draw(self.screen, theme)

        # ----------------------------------------------------------------------
        # Card 2: View Mode (Map View / Nodes View Toggle)
        # ----------------------------------------------------------------------
        c2_rect = pygame.Rect(lx, ly + 214, lw, 80)
        draw_shadowed_card(self.screen, c2_rect, theme["bg_card"], theme["border"], radius=14)

        pygame.draw.rect(self.screen, theme["primary"], (c2_rect.x + 14, c2_rect.y + 14, 12, 12), border_radius=3)
        pygame.draw.rect(self.screen, (255, 255, 255), (c2_rect.x + 16, c2_rect.y + 16, 8, 8), border_radius=1)
        self.screen.blit(font_card_h.render("View Mode", True, theme["text_primary"]), (c2_rect.x + 34, c2_rect.y + 11))

        self.btn_map_view.draw(self.screen, theme)
        self.btn_nodes_view.draw(self.screen, theme)

        # ----------------------------------------------------------------------
        # Card 3: Road Controls
        # ----------------------------------------------------------------------
        c3_rect = pygame.Rect(lx, ly + 304, lw, 152)
        draw_shadowed_card(self.screen, c3_rect, theme["bg_card"], theme["border"], radius=14)

        pygame.draw.circle(self.screen, theme["danger"], (c3_rect.x + 20, c3_rect.y + 20), 8)
        pygame.draw.line(self.screen, (255, 255, 255), (c3_rect.x + 16, c3_rect.y + 20), (c3_rect.x + 24, c3_rect.y + 20), 2)
        self.screen.blit(font_card_h.render("Road Controls", True, theme["text_primary"]), (c3_rect.x + 34, c3_rect.y + 11))

        self.road_dropdown.draw(self.screen, theme)
        self.btn_close_road.draw(self.screen, theme)
        self.btn_reopen_road.draw(self.screen, theme)
        self.btn_road_history.draw(self.screen, theme)

        # ----------------------------------------------------------------------
        # Card 4: Route Legend
        # ----------------------------------------------------------------------
        c4_y = ly + 466
        c4_h = max(136, self.col_h - 466)
        c4_rect = pygame.Rect(lx, c4_y, lw, c4_h)
        draw_shadowed_card(self.screen, c4_rect, theme["bg_card"], theme["border"], radius=14)

        pygame.draw.circle(self.screen, theme["text_secondary"], (c4_rect.x + 20, c4_rect.y + 18), 7, 1)
        pygame.draw.circle(self.screen, theme["text_secondary"], (c4_rect.x + 20, c4_rect.y + 15), 1)
        pygame.draw.line(self.screen, theme["text_secondary"], (c4_rect.x + 20, c4_rect.y + 17), (c4_rect.x + 20, c4_rect.y + 21), 2)
        self.screen.blit(font_card_h.render("Route Legend", True, theme["text_primary"]), (c4_rect.x + 34, c4_rect.y + 11))

        legend_items = [
            ("Optimal Route", theme["route_primary"], "line"),
            ("Alternative Route 1", theme["route_alt1"], "line"),
            ("Alternative Route 2", theme["route_alt2"], "line"),
            ("Alternative Route 3", theme["route_alt3"], "line"),
            ("Start Location", theme["success"], "pin"),
            ("Destination", theme["danger"], "pin"),
        ]

        font_leg = FontManager.get(10)
        row_y = c4_rect.y + 34
        for name, col, kind in legend_items:
            if kind == "line":
                pygame.draw.line(self.screen, col, (c4_rect.x + 14, row_y + 5), (c4_rect.x + 34, row_y + 5), 4)
            else:
                px, py = c4_rect.x + 24, row_y + 5
                pygame.draw.circle(self.screen, col, (px, py), 5)
                pygame.draw.polygon(self.screen, col, [(px - 3, py + 2), (px + 3, py + 2), (px, py + 5)])
                pygame.draw.circle(self.screen, (255, 255, 255), (px, py), 2)

            self.screen.blit(font_leg.render(name, True, theme["text_primary"]), (c4_rect.x + 42, row_y))
            row_y += 22

    def _draw_right_column(self, theme: Dict[str, Any]):
        """Renders Right Column: Route Results featuring prominent Optimal Hero card and clean Alternatives."""
        rx = self.right_col_rect.x
        rw = self.right_col_rect.w
        ry = self.right_col_rect.y

        main_card = pygame.Rect(rx, ry, rw, self.col_h)
        draw_shadowed_card(self.screen, main_card, theme["bg_card"], theme["border"], radius=14)

        # Header Badge & Title
        pygame.draw.circle(self.screen, theme["primary"], (rx + 20, ry + 20), 8)
        pygame.draw.circle(self.screen, (255, 255, 255), (rx + 20, ry + 20), 3)

        font_rh = FontManager.get(14, bold=True)
        self.screen.blit(font_rh.render("Route Results", True, theme["text_primary"]), (rx + 34, ry + 12))

        # Count badge pill
        all_routes: List[SearchResult] = []
        if self.best_route and self.best_route.found:
            all_routes.append(self.best_route)
        all_routes.extend([r for r in self.alternative_routes if r.found])

        count_badge_text = f"{len(all_routes)} Found"
        font_cnt = FontManager.get(9, bold=True)
        txt_cnt = font_cnt.render(count_badge_text, True, theme["primary"])
        cnt_rect = pygame.Rect(rx + rw - txt_cnt.get_width() - 24, ry + 12, txt_cnt.get_width() + 14, 20)
        draw_rounded_rect(self.screen, theme["primary_light"], cnt_rect, radius=10, border_color=theme["border_focus"], border_width=1)
        self.screen.blit(txt_cnt, (cnt_rect.centerx - txt_cnt.get_width() // 2, cnt_rect.centery - txt_cnt.get_height() // 2))

        font_sub = FontManager.get(10)
        self.screen.blit(font_sub.render("Click any route to display on map", True, theme["text_secondary"]), (rx + 14, ry + 34))

        self.route_card_rects = []

        if not all_routes:
            empty_rect = pygame.Rect(rx + 12, ry + 64, rw - 24, 180)
            draw_rounded_rect(self.screen, theme["bg_card_alt"], empty_rect, radius=10, border_color=theme["border"])
            pygame.draw.circle(self.screen, theme["danger"], (empty_rect.centerx, empty_rect.y + 40), 18)
            pygame.draw.line(self.screen, (255, 255, 255), (empty_rect.centerx - 7, empty_rect.y + 33), (empty_rect.centerx + 7, empty_rect.y + 47), 3)
            pygame.draw.line(self.screen, (255, 255, 255), (empty_rect.centerx - 7, empty_rect.y + 47), (empty_rect.centerx + 7, empty_rect.y + 33), 3)

            font_warn = FontManager.get(13, bold=True)
            txt_w = font_warn.render("No Routes Available", True, theme["danger"])
            self.screen.blit(txt_w, (empty_rect.centerx - txt_w.get_width() // 2, empty_rect.y + 74))

            font_msg = FontManager.get(10)
            txt_m = font_msg.render("Connecting walkways may be closed.", True, theme["text_secondary"])
            self.screen.blit(txt_m, (empty_rect.centerx - txt_m.get_width() // 2, empty_rect.y + 98))
            txt_m2 = font_msg.render("Reopen roads in the Road Controls panel.", True, theme["text_muted"])
            self.screen.blit(txt_m2, (empty_rect.centerx - txt_m2.get_width() // 2, empty_rect.y + 116))
            return

        font_badge = FontManager.get(10, bold=True)
        font_rtitle = FontManager.get(11, bold=True)
        font_stat_bold = FontManager.get(10, bold=True)
        font_stat = FontManager.get(10)
        font_step = FontManager.get(10)

        route_themes = [
            {"num": "1", "name": "Optimal Route", "color": theme["route_primary"], "bg": theme["primary_light"]},
            {"num": "2", "name": "Alternative Route 1", "color": theme["route_alt1"], "bg": theme["orange_light"]},
            {"num": "3", "name": "Alternative Route 2", "color": theme["route_alt2"], "bg": theme["purple_light"]},
            {"num": "4", "name": "Alternative Route 3", "color": theme["route_alt3"], "bg": (236, 253, 245) if theme["name"] == "Light Mode" else (20, 60, 45)},
        ]

        old_clip = self.screen.get_clip()
        content_clip = pygame.Rect(rx + 6, ry + 52, rw - 12, self.col_h - 58)
        self.screen.set_clip(content_clip)

        opt_dist = all_routes[0].total_distance_m if all_routes else 0
        card_start_y = ry + 54 - self.right_scroll_y
        card_y = card_start_y

        for idx, route in enumerate(all_routes[:4]):
            r_cfg = route_themes[idx]
            is_selected = (self.selected_route_idx == idx)
            is_optimal = (idx == 0)
            card_h = 126 if is_optimal else 114

            r_card = pygame.Rect(rx + 10, card_y, rw - 20, card_h)
            self.route_card_rects.append(r_card)

            border_col = r_cfg["color"] if is_selected else theme["border"]
            card_bg = r_cfg["bg"] if is_selected else theme["bg_card_alt"]
            border_w = 2 if is_selected else 1
            draw_rounded_rect(self.screen, card_bg, r_card, radius=10, border_color=border_col, border_width=border_w)

            # Left accent bar for Optimal Hero Card
            if is_optimal:
                accent_bar = pygame.Rect(r_card.x, r_card.y + 4, 3, r_card.h - 8)
                draw_rounded_rect(self.screen, theme["primary"], accent_bar, radius=2)

            # Route Number Badge
            badge_r = 9
            pygame.draw.circle(self.screen, r_cfg["color"], (r_card.x + 16, r_card.y + 16), badge_r)
            txt_b = font_badge.render(r_cfg["num"], True, (255, 255, 255))
            self.screen.blit(txt_b, (r_card.x + 16 - txt_b.get_width() // 2, r_card.y + 16 - txt_b.get_height() // 2))

            # Route Title
            self.screen.blit(font_rtitle.render(r_cfg["name"], True, r_cfg["color"]), (r_card.x + 32, r_card.y + 10))

            # Difference tag for alternative routes (+140 m)
            if idx > 0 and route.total_distance_m > opt_dist:
                diff_m = route.total_distance_m - opt_dist
                txt_diff = font_badge.render(f"+{diff_m}m", True, r_cfg["color"])
                dw = txt_diff.get_width() + 10
                diff_rect = pygame.Rect(r_card.x + 148, r_card.y + 9, dw, 18)
                draw_rounded_rect(self.screen, theme["bg_card"], diff_rect, radius=4, border_color=r_cfg["color"], border_width=1)
                self.screen.blit(txt_diff, (diff_rect.centerx - txt_diff.get_width() // 2, diff_rect.centery - txt_diff.get_height() // 2))

            # Active indicator pill or Select button
            if is_selected:
                pill_rect = pygame.Rect(r_card.right - 66, r_card.y + 8, 58, 20)
                draw_rounded_rect(self.screen, r_cfg["color"], pill_rect, radius=10)
                txt_act = font_badge.render("● Active", True, (255, 255, 255))
                self.screen.blit(txt_act, (pill_rect.centerx - txt_act.get_width() // 2, pill_rect.centery - txt_act.get_height() // 2))
            else:
                sel_btn = self.route_select_buttons[idx]
                sel_btn.rect = pygame.Rect(r_card.right - 58, r_card.y + 8, 50, 20)
                sel_btn.text = "Select"
                sel_btn.style = "outline"
                sel_btn.draw(self.screen, theme)

            # Prominent Metrics Presentation (Distance, Walk Time, Stops)
            est_walk_min = round(route.total_distance_m / 80.0, 1)
            if is_optimal:
                # Featured metrics chips row for optimal hero card
                chip_y = r_card.y + 32
                chip_h = 22
                chip1_w = 64
                chip2_w = 72
                chip3_w = 58

                c1 = pygame.Rect(r_card.x + 12, chip_y, chip1_w, chip_h)
                c2 = pygame.Rect(c1.right + 6, chip_y, chip2_w, chip_h)
                c3 = pygame.Rect(c2.right + 6, chip_y, chip3_w, chip_h)

                chip_bg = theme["bg_card"]
                draw_rounded_rect(self.screen, chip_bg, c1, radius=4, border_color=theme["border"], border_width=1)
                draw_rounded_rect(self.screen, chip_bg, c2, radius=4, border_color=theme["border"], border_width=1)
                draw_rounded_rect(self.screen, chip_bg, c3, radius=4, border_color=theme["border"], border_width=1)

                t1 = font_stat_bold.render(f"{route.total_distance_m} m", True, theme["text_primary"])
                t2 = font_stat_bold.render(f"~{est_walk_min} min", True, theme["text_primary"])
                t3 = font_stat_bold.render(f"{len(route.path)} stops", True, theme["text_primary"])

                self.screen.blit(t1, (c1.centerx - t1.get_width() // 2, c1.centery - t1.get_height() // 2))
                self.screen.blit(t2, (c2.centerx - t2.get_width() // 2, c2.centery - t2.get_height() // 2))
                self.screen.blit(t3, (c3.centerx - t3.get_width() // 2, c3.centery - t3.get_height() // 2))

                step_y = r_card.y + 58
            else:
                stat_str = f"{route.total_distance_m} m   •   ~{est_walk_min} min   •   {len(route.path)} stops"
                self.screen.blit(font_stat.render(stat_str, True, theme["text_secondary"]), (r_card.x + 14, r_card.y + 32))
                step_y = r_card.y + 50

            # Visual Breadcrumb / Steps Timeline with human-readable names
            for s_idx, node_id in enumerate(route.path):
                if s_idx >= 3 and len(route.path) > 3:
                    if s_idx == 3:
                        last_name = DISPLAY_NAMES.get(route.path[-1], route.path[-1])
                        lbl_ell = font_stat.render(f"+ {len(route.path) - 2} more... → {last_name}", True, theme["text_muted"])
                        self.screen.blit(lbl_ell, (r_card.x + 22, step_y))
                    break

                dot_col = theme["success"] if s_idx == 0 else theme["danger"] if s_idx == len(route.path) - 1 else r_cfg["color"] if is_selected else theme["border_focus"]
                pygame.draw.circle(self.screen, dot_col, (r_card.x + 18, step_y + 6), 3)

                if s_idx < min(2, len(route.path) - 1):
                    pygame.draw.line(self.screen, theme["border"], (r_card.x + 18, step_y + 9), (r_card.x + 18, step_y + 16), 1)

                readable_node = DISPLAY_NAMES.get(node_id, node_id)
                step_label = f"{s_idx + 1}.  {readable_node}"
                txt_step = font_step.render(step_label, True, theme["text_primary"])
                self.screen.blit(txt_step, (r_card.x + 26, step_y))
                step_y += 16

            card_y += card_h + 10

        self.screen.set_clip(old_clip)

    def _draw_history_modal(self, theme: Dict[str, Any]):
        """Renders Road History modal dialog."""
        overlay = pygame.Surface((self.WINDOW_WIDTH, self.WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 120))
        self.screen.blit(overlay, (0, 0))

        modal_w = 480
        modal_h = min(500, self.WINDOW_HEIGHT - 80)
        mx = (self.WINDOW_WIDTH - modal_w) // 2
        my = (self.WINDOW_HEIGHT - modal_h) // 2
        modal_rect = pygame.Rect(mx, my, modal_w, modal_h)

        draw_shadowed_card(self.screen, modal_rect, theme["bg_card"], theme["border"], radius=16)

        pygame.draw.circle(self.screen, theme["primary"], (mx + 26, my + 26), 11)
        pygame.draw.circle(self.screen, (255, 255, 255), (mx + 26, my + 26), 4)
        font_mh = FontManager.get(15, bold=True)
        self.screen.blit(font_mh.render("Road Query History", True, theme["text_primary"]), (mx + 46, my + 16))

        # Close X
        close_x = modal_rect.right - 28
        close_y = my + 20
        pygame.draw.line(self.screen, theme["text_secondary"], (close_x - 5, close_y - 5), (close_x + 5, close_y + 5), 2)
        pygame.draw.line(self.screen, theme["text_secondary"], (close_x + 5, close_y - 5), (close_x - 5, close_y + 5), 2)

        history = self.manager.get_recent_history()
        font_hn = FontManager.get(12, bold=True)
        font_hd = FontManager.get(10)
        font_tag = FontManager.get(9, bold=True)

        hy = my + 56
        if not history:
            font_empty = FontManager.get(11)
            txt_e = font_empty.render("No queries recorded yet.", True, theme["text_muted"])
            self.screen.blit(txt_e, (mx + 24, hy + 20))
        else:
            for entry in history[:7]:
                item_rect = pygame.Rect(mx + 16, hy, modal_w - 32, 46)
                draw_rounded_rect(self.screen, theme["bg_card_alt"], item_rect, radius=8, border_color=theme["border"])

                start_disp = DISPLAY_NAMES.get(entry.start_name, entry.start_name)
                goal_disp = DISPLAY_NAMES.get(entry.goal_name, entry.goal_name)
                route_str = f"{start_disp} → {goal_disp}"
                self.screen.blit(font_hn.render(route_str, True, theme["text_primary"]), (item_rect.x + 12, item_rect.y + 6))

                walk_min = round(entry.distance_m / 80.0, 1)
                details = f"{entry.distance_m} m   •   ~{walk_min} min   •   {entry.timestamp}"
                self.screen.blit(font_hd.render(details, True, theme["text_secondary"]), (item_rect.x + 12, item_rect.y + 26))

                status_col = theme["success"] if entry.found else theme["danger"]
                status_bg = (236, 253, 245) if entry.found else (254, 242, 242)
                tag_txt = "OPTIMAL" if entry.found else "BLOCKED"
                t_surf = font_tag.render(tag_txt, True, status_col)
                t_rect = pygame.Rect(item_rect.right - t_surf.get_width() - 18, item_rect.centery - 10, t_surf.get_width() + 12, 20)
                draw_rounded_rect(self.screen, status_bg, t_rect, radius=4, border_color=status_col, border_width=1)
                self.screen.blit(t_surf, (t_rect.centerx - t_surf.get_width() // 2, t_rect.centery - t_surf.get_height() // 2))

                hy += 52

        # Close button at bottom
        btn_close = pygame.Rect(mx + 16, modal_rect.bottom - 46, modal_w - 32, 34)
        draw_rounded_rect(self.screen, theme["primary"], btn_close, radius=8)
        txt_c = FontManager.get(13, bold=True).render("Close History", True, (255, 255, 255))
        self.screen.blit(txt_c, (btn_close.centerx - txt_c.get_width() // 2, btn_close.centery - txt_c.get_height() // 2))

    def _handle_history_modal_click(self, pos: Tuple[int, int]):
        modal_w = 480
        modal_h = min(500, self.WINDOW_HEIGHT - 80)
        mx = (self.WINDOW_WIDTH - modal_w) // 2
        my = (self.WINDOW_HEIGHT - modal_h) // 2
        modal_rect = pygame.Rect(mx, my, modal_w, modal_h)

        if not modal_rect.collidepoint(pos):
            self.show_history_modal = False
            return

        close_rect = pygame.Rect(modal_rect.right - 36, my + 12, 28, 28)
        btn_close = pygame.Rect(mx + 16, modal_rect.bottom - 46, modal_w - 32, 34)
        if close_rect.collidepoint(pos) or btn_close.collidepoint(pos):
            self.show_history_modal = False


def main():
    app = SmartCampusNavigatorApp()
    app.run()


if __name__ == "__main__":
    main()
