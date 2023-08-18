from PIL import ImageGrab
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Mesh, Color, Ellipse, RoundedRectangle
from kivy.logger import Logger
from kivy.properties import NumericProperty, OptionProperty
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.colorpicker import ColorPicker
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.modalview import ModalView
from kivy.uix.scatterlayout import ScatterLayout
from kivy.uix.widget import Widget
from kivymd.uix.screen import MDScreen

bottom_sheet_fade = 'faded'


class DrawScreen(MDScreen):
    @staticmethod
    def reset(according_to):
        according_to.scale = 1.0
        according_to.rotation = 0.0
        according_to.pos = [0, 0]

    @staticmethod
    def on_bottom_sheet_size(height):
        global bottom_sheet_fade
        bottom_sheet_fade = 'faded' if int(height) < 300 else 'not_faded'


class MyScatterLayout(ScatterLayout):
    pass


class BaseLayer(Widget):

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


class BottomSheetBase(FloatLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.swipe_direction = 'up'
        self.child_objects_for_touch_detection = None

    def on_touch_down(self, touch):
        self.child_objects_for_touch_detection = self.children[0].children[0].children[0].children
        if self.collide_point(*touch.pos) and not any(
                [child.collide_point(*touch.pos) for child in self.child_objects_for_touch_detection]):
            touch.grab(self)
            self.parent.children[1].disabled = True
            return True
        else:
            return super().on_touch_down(touch)

    def on_touch_move(self, touch):
        if touch.ppos[1] < touch.pos[1]:
            self.swipe_direction = 'up'
        else:  # swiping downwards
            self.swipe_direction = 'down'

        if touch.grab_current is self:
            self.canvas.ask_update()
            self.height = 30.1 if self.height <= 30 else self.height + touch.dy
            if self.height >= 800:
                self.height = 800
            return True

    def on_touch_up(self, touch):
        if touch.grab_current is self:
            # for enabling disabled drawing canvas
            if self.swipe_direction == 'down':
                Clock.schedule_once(self.enable_canvas, .4)

            if self.swipe_direction == 'up' and 30 < int(self.height) <= 400:
                Animation(height=400, duration=.3).start(self)
            elif self.swipe_direction == 'up' and 400 < int(self.height) <= 800:
                Animation(height=800, duration=.3).start(self)
            elif self.swipe_direction == 'down' and 30 < int(self.height) <= 400:
                Animation(height=30.1, duration=.3).start(self)
            elif self.swipe_direction == 'down' and 400 < int(self.height) <= 800:
                Animation(height=400, duration=.3).start(self)
            touch.ungrab(self)
            return True

    def enable_canvas(self, who):
        if int(self.height) == 30:
            self.parent.children[1].disabled = False


class BottomSheetWidget(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def color_fader(self):
        Animation.stop_all(self)
        Animation(width=50 if bottom_sheet_fade == 'faded' else 70, duration=.1).start(self)

        with self.canvas.before:
            self.canvas.before.clear()
            Color(rgba=(1, 1, 1, .3) if bottom_sheet_fade == 'faded' else (1, 1, 1, 1))
            RoundedRectangle(size=self.size, pos=self.pos, radius=[4])

        with self.parent.parent.parent.canvas.before:
            self.parent.parent.parent.canvas.before.clear()
            Color(rgba=(.1, .1, .1, .5) if bottom_sheet_fade == 'faded' else (1, 1, 1, .4))
            RoundedRectangle(size=self.parent.parent.parent.size, pos=self.parent.parent.parent.pos,
                             radius=[20, 20, 0, 0])


class BottomSheetButton(Label, ButtonBehavior):
    canvas_lock_text = OptionProperty('lock-canvas', options=['lock-canvas', 'unlock-canvas'])

    def bg_fader(self):
        with self.canvas.before:
            self.canvas.before.clear()
            Color(rgba=(0, 0, 0, .3) if bottom_sheet_fade == 'faded' else (0, 0, 0, 1))
            RoundedRectangle(size=self.size, pos=self.pos)
        if bottom_sheet_fade == 'faded':
            self.color = [1, 1, 1, .3]
        else:
            self.color = [1, 1, 1, 1]

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            touch.grab(self)
            return True

    def on_touch_up(self, touch):
        if self.collide_point(*touch.pos):
            if touch.grab_current is self:
                match self.text:
                    case 'save':
                        drawing_canvas = [x for x in self.walk_reverse(loopback=False)][-2]
                        drawing_canvas.ids['layer_holder'].export_as_image().save('hlo.png')
                    case 'reset-size':
                        drawing_canvas = [x for x in self.walk_reverse(loopback=False)][-2]
                        drawing_canvas.ids['sctr'].scale = 1.0
                        drawing_canvas.ids['sctr'].rotation = 0.0
                        drawing_canvas.ids['sctr'].pos = [0, 0]
                    case 'lock-canvas' | 'unlock-canvas':
                        drawing_canvas = [x for x in self.walk_reverse(loopback=False)][-2]
                        drawing_canvas.ids['sctr'].do_scale = False if drawing_canvas.ids['sctr'].do_scale else True
                        drawing_canvas.ids['sctr'].do_translation = False if drawing_canvas.ids[
                            'sctr'].do_translation else True
                        drawing_canvas.ids['sctr'].do_rotation = False if drawing_canvas.ids[
                            'sctr'].do_rotation else True
                        self.canvas_lock_text = 'lock-canvas' if drawing_canvas.ids[
                            'sctr'].do_rotation else 'unlock-canvas'

                    case _:
                        self.show_popup(self.text)
                return True

    @staticmethod
    def show_popup(for_what):
        color_lst = ['pen_color', 'background_color']
        tools_lst = ['gradient', 'eye dropper', 'custom brush creator']
        brush_lst = ['paint brush', 'pen', 'pencil', 'eraser']
        insert_lst = ['layer', 'shape', 'layer mask', 'text', 'image']
        effects_list = ['blur', 'vintage']
        list_of_lists = ['color_lst', 'tools_lst', 'brush_lst', 'insert_lst', 'effects_list']
        PopUp_show(eval([str(x) for x in list_of_lists if for_what in x][0]))


class PopUp_show(ModalView):
    pop_size = NumericProperty()

    def __init__(self, lst, **kwargs):
        super().__init__(**kwargs)
        for data in lst:
            self.ids['list_popup_scroll'].children[0].add_widget(MyPopUpListItem(text='[b]' + data + '[/b]'))
        self.opacity = 0
        self.open()

    def on_open(self):
        self.size_hint_y = None
        if self.ids['list_popup_holder'].height <= self.height:
            self.pop_size = self.ids['list_popup_holder'].height
        else:
            self.pop_size = self.height

    def on_pop_size(self, *args):
        self.height = self.pop_size
        anim = Animation(opacity=1, duration=0.1)
        anim.start(self)


class MyPopUpListItem(Label):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            touch.grab(self)

    def on_touch_up(self, touch):
        if self.collide_point(*touch.pos) and touch.grab_current is self:
            touch.ungrab(self)
            Logger.info(f'selected option: ____{self.text}____')
            match self.text[3:-4]:
                # color:
                case 'pen_color' | 'background_color':
                    Clr()
                # insert:


class Clr(ModalView):
    def __init__(self, **kwargs):
        self.size_hint = (.9, .5)
        super().__init__(**kwargs)
        self.add_widget(ColorPicker())
        self.open()


def check_pos_distance(pos1: list, pos2: list) -> int:
    pos = map(lambda x: x * -1 if x < 0 else x, [pos2[0] - pos1[0], pos2[1] - pos1[1]])
    return int(sum(pos) / 2)


def get_color_at_touch(self):
    x, y = Window.mouse_pos  # Get mouse coordinates
    screenshot = ImageGrab.grab(bbox=(x, y, x + 1, y + 1))  # Capture a 1x1 pixel screenshot
    color = screenshot.getpixel((0, 0))  # Get the color of the pixel
    return f'#{color[0]:02X}{color[1]:02X}{color[2]:02X}'  # Convert to hex format
