from ui import *

class Alt_Static_Window(Static_Window):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        up_arrow = Image_Manager.get_arrow('u', (self.rect.width, 15), padding=(self.rect.width + 10, 10), color=(255, 255, 255), bgcolor=(50, 50, 50, 100))
        down_arrow = pg.transform.rotate(up_arrow, 180)

        self.scroll_bar.up_button = Button.image_button(up_arrow, size=up_arrow.get_size(), border_radius=0, func=self.scroll_bar.scroll, args=[-1])
        self.add_child(self.scroll_bar.up_button, anchor_point='midtop')
        self.scroll_bar.down_button = Button.image_button(down_arrow, size=down_arrow.get_size(), border_radius=0, func=self.scroll_bar.scroll, args=[1])
        self.add_child(self.scroll_bar.down_button, anchor_point='midbottom')
        self.scroll_bar.handel.adjust_offset(-500, 0)
        
        self.scroll_bar.set_handel_collision(False)
        
    def events(self, events):
        self.scroll_bar.events(events)
        
    def draw(self, surf):
        surf.blit(self.current_image, self.rect)
        if not self.hide_label:
            pg.draw.rect(surf, self.label_color, self.label_rect.rect, border_top_left_radius=10, border_top_right_radius=10)
            if self.label:
                self.label.draw(surf)
        if not self.scroll_bar.is_full():
            if self.scroll_bar.can_scroll_up():
                self.scroll_bar.up_button.draw(surf)
            if self.scroll_bar.can_scroll_down():
                self.scroll_bar.down_button.draw(surf)
                