from kivy.graphics import Mesh, Color, Ellipse
from kivy.uix.label import Label
from kivy.uix.scatterlayout import ScatterLayout
from kivy.uix.widget import Widget
from kivymd.uix.screen import MDScreen


class DrawScreen(MDScreen):
    @staticmethod
    def reset(according_to):
        according_to.scale = 1.0
        according_to.rotation = 0.0
        according_to.pos = [0, 0]


def check_pos_distance(pos1: list, pos2: list) -> int:
    pos = map(lambda x: x * -1 if x < 0 else x, [pos2[0] - pos1[0], pos2[1] - pos1[1]])
    return int(sum(pos) / 2)


class TheMainCanvas(Label):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.pointer_size = 5
        self.vertices = []
        self.vertices_point = []
        self.edge_indicators = []
        self.selected_edge_index = None
        self.is_edge_selected = False
        self.indices = None

    def mesh_touch_down(self, touch):
        try:
            if self.collide_point(*touch.pos):
                touch.grab(self)
            self.mesh_draw_canvas()

            # if we are trying to move an edge point, we should change the vertices positions too
            new_touch_pos = [int(x) for x in list(touch.pos)]
            vertices_pos_points = [x[:-2] for x in self.vertices_point]
            for i, vertices_pos_point in enumerate(vertices_pos_points):
                if check_pos_distance(new_touch_pos, vertices_pos_point) < self.pointer_size:
                    self.is_edge_selected = True
                    self.selected_edge_index = i
        except TypeError:
            pass

    def mesh_touch_move(self, touch):
        try:
            if self.is_edge_selected:
                self.vertices[self.selected_edge_index * 4], self.vertices[self.selected_edge_index * 4 + 1] = \
                    self.vertices_point[self.selected_edge_index][0], self.vertices_point[self.selected_edge_index][1] = \
                    [int(x) for x in list(touch.pos)]

            self.mesh_draw_canvas()
        except TypeError:
            pass

    def mesh_touch_up(self, touch):
        try:
            self.is_edge_selected = not self.is_edge_selected
            if touch.grab_current is self:
                if touch.ppos[0] - touch.pos[0] == 0 and touch.ppos[1] - touch.pos[1] == 0:
                    new_vert = [int(x) for x in touch.pos] + [0, 0]
                    touch.ungrab(self)
                    self.vertices += new_vert
                    self.vertices_point.append(new_vert)

                if len(self.vertices) > 2:
                    self.indices = [x for x in range(0, len(self.vertices_point))]
                    self.mesh_draw_canvas()
        except TypeError:
            pass

    def mesh_draw_canvas(self):
        try:
            pos = [x[:-2] for x in self.vertices_point]
            for ind in self.indices:
                with self.canvas.after:
                    self.canvas.after.clear()
                    Color(rgba=(1, .5, 1, .4))
                    Mesh(vertices=self.vertices, indices=self.indices, mode='triangle_fan')
                    Color(rgb=(1, 1, 1))
                    self.edge_indicators.append(
                        Ellipse(size=(self.pointer_size, self.pointer_size),
                                pos=tuple([int(x) - self.pointer_size for x in pos[ind]])))
            for i, data in enumerate(pos):
                with self.canvas.after:
                    Ellipse(size=(self.pointer_size, self.pointer_size),
                            pos=tuple([int(x) - self.pointer_size for x in pos[i]]))

        except TypeError:
            pass

    def on_touch_down(self, touch):
        self.mesh_touch_down(touch)

    def on_touch_move(self, touch):
        self.mesh_touch_move(touch)

    def on_touch_up(self, touch):
        self.mesh_touch_up(touch)


class MyScatterLayout(ScatterLayout):
    pass


class BottomSheetWidget(Widget):
    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            touch.grab(self)

    def on_touch_move(self, touch):
        if touch.grab_current is self:
            self.parent.parent.parent.canvas.ask_update()
            self.parent.parent.parent.height = 50.1 if self.parent.parent.parent.height <= 50 else self.parent.parent.parent.height + touch.dy
            if self.parent.parent.parent.height >= 800:
                self.parent.parent.parent.height = 800

    def on_touch_up(self, touch):
        touch.ungrab(self)
