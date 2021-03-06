import pygame as pg
from pygame.math import Vector2 as vec

from ..image import get_surface

class Mover:
    def __init__(self):
        self.target_rect = None
        self.last_pos = None

        self.pos = vec(self.rect.centerx, self.rect.centery)
        self.vel = vec(0, 0)
        self.acc = vec(0, 0)
        
        self.scale = vec(self.rect.width, self.rect.height)
        self.scale_vel = vec(0, 0)
        self.scale_acc = vec(0, 0)
        
        self.current_rotation = 0
        self.rotation_vel = 0
        
        self.startup_timer = 0
        self.end_timer = 0

        self.moving = False
        self.scaling = False
        self.animation_index = 0
        
        self.movement_sequence = []
        self.movement_cache = {'v': 5, 'startup_timer': 0, 'end_timer': 0, 'scale': False, 'rotation_vel': 0}
        
    def finished_move(self):
        return self.end_timer == 0 and not (self.moving or self.scaling)
        
    def set_target_rect(self, target_rect, p=None, v=5, startup_timer=0, end_timer=0, scale=False, rotation_vel=0):
        if target_rect == self.rect:
            return
            
        self.target_rect = target_rect
        
        if p is not None:
            self.rect.center = p
            
        p0 = vec(self.rect.centerx, self.rect.centery)
        p1 = vec(target_rect.centerx, target_rect.centery)
        length = p0.distance_to(p1)
        
        if length == 0:
            vel = vec(0, 0)
        else:
            vel = (p1 - p0).normalize() * v

        self.vel = vel
        self.pos = p0
        self.moving = True
        
        frames = length / v
        
        if scale:
            s1 = vec(target_rect.width, target_rect.height)
            s0 = vec(self.rect.width, self.rect.height)
            
            scale_vel = (s1 - s0) / frames
        
            self.scale_vel = scale_vel
            self.scaling = True
            
        self.rotation_vel = rotation_vel

        self.startup_timer = startup_timer
        self.end_timer = end_timer
        
        self.movement_cache['v'] = v
        self.movement_cache['startup_timer'] = startup_timer
        self.movement_cache['end_timer'] = end_timer
        self.movement_cache['scale'] = scale
        self.movement_cache['rotation_vel'] = rotation_vel
        
        self.last_pos = self.target_rect.center
        
    def cancel_move(self):
        if self.target_rect:
            self.stop_scale()
            self.stop_move()
            self.stop_rotate()
            self.startup_timer = 0
            self.end_timer = 0
            self.target_rect = None
        
    def set_animation(self, movement_sequence, start=False):
        self.movement_sequence = movement_sequence 
        if start:
            self.start_next_sequence()
            
    def start_animation(self):
        self.animation_index = 0
        self.start_next_sequence()
        
    def start_next_sequence(self):
        info = self.movement_sequence[self.animation_index].copy()
        self.animation_index += 1
        target_rect = info.pop('target_rect')
        self.set_target_rect(target_rect, **info)

    def move(self):
        if not self.finished_move():
        
            p = self.target_rect.center
            if self.last_pos != p:
                self.set_target_rect(self.target_rect, **self.movement_cache)
            self.last_pos = p
            
        if self.startup_timer > 0:
            self.startup_timer -= 1

        elif self.moving or self.scaling:
            
            if self.moving:
                self.pos += self.vel  
                self.rect.center = (self.pos.x, self.pos.y)
                if self.done_moving():
                    self.stop_move()
 
            if self.scaling:
                self.scale += self.scale_vel
                self.rect.size = self.get_scale()
                self.rect.center = (self.pos.x, self.pos.y)
                if self.done_scaling():
                    self.stop_scale()
                    
            if self.rotation_vel:
                self.current_rotation += self.rotation_vel
                
        else:
            
            if self.end_timer > 0:
                self.end_timer -= 1
                
            elif self.target_rect:
                self.target_rect = None
                
        if self.finished_move() and 0 < self.animation_index < len(self.movement_sequence):
            self.start_next_sequence()
            
    def gen_path(self, start_point, itterations, start_scale=None, dx=lambda x, y: x, dy=lambda x, y: y, dw=lambda w, h: w, dh=lambda w, h: h):
        if start_scale is None:
            start_scale = self.rect.size

        x, y = start_point
        w, h = start_scale
        
        r = pg.Rect(x, y, w, h)
                
        frames = [{'target_rect': r}]

        for i in range(itterations):
            x = dx(x, y)
            y = dy(x, y)
            w = dw(w, h)
            h = dh(w, h)
            
            r = pg.Rect(x, y, w, h)
            frames.append({'target_rect': r, 'scale': True})
            
        self.set_animation(frames)
            
    def done_moving(self):
        x_done = False
        y_done = False
        
        if self.vel.x > 0:
            x_done = self.rect.centerx >= self.target_rect.centerx
        elif self.vel.x < 0:
            x_done = self.rect.centerx <= self.target_rect.centerx
        else:
            x_done = True
            
        if self.vel.y > 0:
            y_done = self.rect.centery >= self.target_rect.centery
        elif self.vel.y < 0:
            y_done = self.rect.centery <= self.target_rect.centery
        else:
            y_done = True
            
        return x_done and y_done
            
    def done_scaling(self):
        w_done = False
        h_done = False
        
        if self.scale_vel.x > 0:
            if self.rect.width >= self.target_rect.width:
                w_done = True
        elif self.scale_vel.x < 0:
            if self.rect.width <= self.target_rect.width:
                w_done = True
        else:
            w_done = True
            
        if self.scale_vel.y > 0:
            if self.rect.height >= self.target_rect.height:
                h_done = True
        elif self.scale_vel.y < 0:
            if self.rect.height <= self.target_rect.height:
                h_done = True
        else:
            h_done = True
            
        return w_done and h_done
     
    def stop_move(self):
        self.rect.center = self.target_rect.center
        self.vel *= 0
        self.moving = False
        
    def stop_scale(self):
        c = self.rect.center
        self.rect.size = self.target_rect.size
        if not self.moving:
            self.rect.center = self.target_rect.center
        else:
            self.rect.center = c
        
        self.scale = vec(self.rect.width, self.rect.height)
        self.scale_vel *= 0
        self.scaling = False

    def stop_rotate(self):
        self.current_rotation = 0
        self.rotation_vel = 0

    def reset_timer(self):
        self.end_timer = self.movement_cache['end_timer']
        
    def get_scale(self):
        w = max({int(self.scale.x), 0})
        h = max({int(self.scale.y), 0})
        return (w, h)
       
    def get_applied_scale(self):
        return pg.transfrom.scale(self.image, self.get_scale())
        
    def get_applied_rotation(self):
        return pg.transform.rotate(self.image, self.rotation)

class Base_Object:    
    @classmethod
    def get_moving(cls):
        class New_Mover(Mover, cls):
            def __init__(self, *args, **kwargs):
                cls.__init__(self, *args, **kwargs)
                Mover.__init__(self)

            def update(self):
                self.move()
                super().update()
                
        New_Mover.__name__ = f'Moving_{cls.__name__}'
        
        return New_Mover
        
    def __init__(self, func=None, args=[], kwargs={}, tag=None, ohandle=False, enable_func=False, **okwargs):
        if tag is None:
            tag = str(id(self))
        self.tag = tag
        self.ohandle = ohandle
        self.visible = True
        self.enabled = True
        self.window_draw = False
        self.hit = False
        self.flag = False
        
        self._menu = None

        self.enable_func = enable_func
        self._func = func
        self._args = args
        self._kwargs = kwargs
        self._return_val = None

        self.leftover = okwargs
            
    def __hash__(self):
        return id(self)
        
    @property
    def menu(self):
        return self._menu
        
    def get_leftover(self):
        lo = self.leftover.copy()
        self.leftover.clear()
        return lo
        
    def set_leftover(self):
        for name, value in self.get_leftover().items():
            setattr(self, name, value)
        
    def set_tag(self, tag):
        self.tag = tag
        
    def get_tag(self):
        return self.tag
        
    def set_visible(self, visible):
        self.visible = visible
        
    def set_enabled(self, enabled):
        self.enabled = enabled
        
    def turn_off(self):
        self.visible = False
        self.enabled = False
        
    def turn_on(self):
        self.visible = True
        self.enabled = True
        
    def set_window_draw(self, window_draw):
        self.window_draw = window_draw
        
    def hit_mouse(self):
        if hasattr(self, 'rect'):
            return self.rect.collidepoint(pg.mouse.get_pos())
        
    def set_func(self, func, args=None, kwargs=None):    
        self._func = func
        if args is not None:
            self._args = args
        if kwargs is not None:
            self._kwargs = kwargs
        
    def set_args(self, args=None, kwargs=None):
        if args is not None:
            self._args = args
        if kwargs is not None:
            self._kwargs = kwargs
            
    def clear_args(self):
        self.set_args(args=[], kwargs={})
        
    def set_return(self, r):
        self._return_val = r
        
    def peek_return(self):
        return self._return_val

    def get_return(self):
        r = self._return_val
        self._return_val = None
        return r
        
    def run_func(self):
        if self._func:
            r = self._func(*self._args, **self._kwargs)
            if r is not None:
                self._return_val = r
        
    def set_cursor(self):
        pass
        
    def clear(self):
        pass
        
    def events(self, events):
        pass
        
    def update(self):
        if self.enable_func:
            self.run_func()
        
    def draw(self, surf):
        pass
        
    def draw_many(self, surf, locations, anchor_point='center'):
        s = getattr(self.rect, anchor_point)
        for pos in locations:
            setattr(self.rect, anchor_point, s)
            self.update_position()
            self.draw(surf)
        setattr(self.rect, anchor_point, s)
        self.update_position()

class Position(Base_Object):        
    @classmethod
    def rect(cls, r, **kwargs):
        return cls(rect=r, **kwargs)
        
    def __init__(
        self,
        rect=None,
        parent=None,
        offset=None,
        anchor_point='topleft',
        children=None,
        contain=False,
        bind_width=False,
        bind_height=False, 
        **kwargs
    ):
    
        super().__init__(**kwargs)
        if rect is not None:
            self.rect = rect
        self.parent = parent
        if offset is None:
            offset = [0, 0]
        self.offset = offset
        self.anchor_point = anchor_point

        if children is None:
            children = []
        self.children = children
        
        self.contain = contain
        self.bind_width = bind_width
        self.bind_height = bind_height
        
    @property
    def total_rect(self):
        self.update_position(all=True)
        x = min({c.rect.x for c in self.children})
        y = min({c.rect.y for c in self.children})
        w = max({c.rect.right for c in self.children}) - x
        h = max({c.rect.bottom for c in self.children}) - y
        return pg.Rect(x, y, w, h)
        
    @property
    def first_born(self):
        if self.children:
            return self.children[0]
            
    @property
    def last_born(self):
        if self.children:
            return self.children[-1]
            
    @property
    def menu(self):
        if self._menu is None and self.parent:
            return self.parent.menu

    def set_children(self, children):
        self.children = children
        
    def add_children(self, children):
        self.children += children
        
    def add_child(self, child, set_parent=False, **kwargs):
        if child not in self.children:
            self.children.append(child)
        if set_parent or kwargs:
            child.set_parent(self, **kwargs)
        
    def remove_child(self, child):
        i = 0
        for c in self.children:
            if c is child:
                self.children.pop(i)
            else:
                i += 1
 
    def clear_children(self):
        self.set_children([])

    def get_children(self):
        return self.children
        
    def get_sub_children(self, children=None):
        if children is None:
            children = []
        for c in self.children:
            children.append(c)
            c.get_sub_children(children=children)
        return children

    def set_parent(self, parent, offset=None, anchor_point='topleft', contain=False, bind_width=False, bind_height=False, current_offset=False):
        self.parent = parent
        self.anchor_point = anchor_point
        if offset is None:
            if current_offset:
                offset = self.get_current_offset()
            else:
                offset = [0, 0]
        self.offset = offset
        self.contain = contain
        self.bind_width = bind_width
        self.bind_height = bind_height
        self.update_position()
        
    def position_copy_from(self, o):
        self.rect = o.rect.copy()
        self.set_parent(o.parent, offset=o.offset.copy(), anchor_point=o.anchor_point, contain=o.contain, bind_width=o.bind_width, bind_height=o.bind_height)

    def set_anchor(self, anchor_point, offset=None):
        self.anchor_point = anchor_point
        if offset is None:
            offset = [0, 0]
        self.offset = offset

    def get_relative_position(self):
        self.update_position()
        return [self.rect.x - self.parent.rect.x, self.rect.y - self.parent.rect.y]
        
    def set_to_relative(self):
        self.rect.topleft = self.get_relative_position()
        
    def freeze(self):
        self.offset = self.get_relative_position()
        self.anchor_point = 'topleft'
        
    def get_offset(self):
        return self.offset.copy()
                
    def adjust_offset(self, dx, dy):
        self.offset[0] += dx
        self.offset[1] += dy
        if self.contain:
            self.set_contain()
            
    def set_current_offset(self):
        sx, sy = getattr(self.rect, self.anchor_point)
        px, py = getattr(self.parent.rect, self.anchor_point)
        self.offset[0] = sx - px
        self.offset[1] = sy - py
        if self.contain:
            self.set_contain()
            
    def get_current_offset(self):
        sx, sy = getattr(self.rect, self.anchor_point)
        px, py = getattr(self.parent.rect, self.anchor_point)
        return [sx - px, sy - py]
        
    def get_offset_from(self, r, anchor_point='topleft'):
        sx, sy = getattr(self.rect, anchor_point)
        rx, ry = getattr(r, anchor_point)
        return [sx - rx, sy - ry]
        
    def match_anchor(self, r, anchor_point):
        setattr(self.rect, anchor_point, getattr(r, anchor_point))

    def set_offset(self, dx, dy):
        self.offset = [dx, dy]
        
    def set_contain(self):
        setattr(self.rect, self.anchor_point, getattr(self.parent.rect, self.anchor_point))
        self.rect.x += self.offset[0]
        self.rect.y += self.offset[1]
        ax, ay = self.adjust_limits()
        self.offset[0] += ax
        self.offset[1] += ay

    def adjust_limits(self):
        x0, y0 = self.rect.topleft
        if self.rect.top < self.parent.rect.top:
            self.rect.top = self.parent.rect.top
        elif self.rect.bottom > self.parent.rect.bottom:
            self.rect.bottom = self.parent.rect.bottom
        if self.rect.left < self.parent.rect.left:
            self.rect.left = self.parent.rect.left
        elif self.rect.right > self.parent.rect.right:
            self.rect.right = self.parent.rect.right
        return (self.rect.x - x0, self.rect.y - y0)

    def update_position(self, all=False):
        if self.parent is not None:
            if self.bind_width:
                self.rect.width = self.parent.rect.width
            if self.bind_height:
                self.rect.height = self.parent.rect.height
            setattr(self.rect, self.anchor_point, getattr(self.parent.rect, self.anchor_point))
            self.rect.x += self.offset[0]
            self.rect.y += self.offset[1]
            if self.contain:
                self.adjust_limits()
        if all:
            self.update_children()
                
    def update_children(self):
        for c in self.get_children():
            c.update_position()
            c.update_children()
            
    def draw_on(self, surf, rect):
        dx, dy = rect.topleft
        self.rect.move_ip(-dx, -dy)
        self.update_children()
        self.draw(surf)
        self.rect.move_ip(dx, dy)
        self.update_children()
        
    def update(self):
        self.update_position()
        super().update()

class Style(Position):
    def __init__(self,
        size=(0, 0),
        padding=[0, 0, 0, 0],
        special_pad=0,
        color=(0, 0, 0), 
        outline_width=0,
        outline_color=None,
        outline_dir=False,
        color_key=None,
        border_radius=5,
        border_top_left_radius=-1,
        border_top_right_radius=-1,
        border_bottom_left_radius=-1,
        border_bottom_right_radius=-1,
        draw_rect=False,
        draw_image=True,
        image=None,
        from_surface=False,
        **kwargs
    ):
        
        super().__init__(**kwargs)

        if len(padding) == 2:
            padding = [padding[0], padding[0], padding[1], padding[1]]
        self.padding = padding
        self.special_pad = special_pad
        self.rect = pg.Rect(0, 0, size[0], size[1])
        self._osize = size
        
        try:
            self.color = color
        except AttributeError:
            pass
        self.outline_width = outline_width
        self.outline_color = outline_color
        self.outline_dir = outline_dir
        self.border_kwargs = {
            'border_radius': border_radius,
            'border_top_left_radius': border_top_left_radius,
            'border_top_right_radius': border_top_right_radius,
            'border_bottom_left_radius': border_bottom_left_radius,
            'border_bottom_right_radius': border_bottom_right_radius
        }
        self._draw_rect = draw_rect
        self._draw_image = draw_image
        
        self.image = image
        if image and not any(size):
            self.size = image.get_size()
        elif from_surface:
            self.image = get_surface(
                self.size,
                color=self.color,
                width=self.outline_width,
                olcolor=self.outline_color,
                key=color_key,
                **self.border_kwargs
            )
        
    @property
    def left_pad(self):
        return self.padding[0]
    @property
    def right_pad(self):
        return self.padding[1]
    @property
    def top_pad(self):
        return self.padding[2]
    @property
    def bottom_pad(self):
        return self.padding[3]
    @property
    def x_pad(self):
        return self.left_pad + self.right_pad
    @property
    def y_pad(self):
        return self.top_pad + self.bottom_pad

    @property
    def size(self):
        return self.rect.size
        
    @size.setter
    def size(self, size):
        self.rect.size = size
        
    @property
    def alpha(self):
        if len(self.color) == 4:
            return self.color[3]
        return 0

    @property
    def padded_rect(self):
        r = self.rect.inflate(-self.x_pad, -self.y_pad)
        r.x = self.rect.x + self.left_pad
        r.y = self.rect.y + self.top_pad
        return r
        
    @property
    def reverse_padded_rect(self):
        r = self.rect.inflate(self.x_pad, self.y_pad)
        r.x = self.rect.x - self.left_pad
        r.y = self.rect.y - self.top_pad
        return r
        
    @property
    def border_radius(self):
        return self.border_kwargs['border_radius']
        
    @border_radius.setter
    def border_radius(self, br):
        self.border_kwargs['border_radius'] = br
        
    def reset_size(self):
        self.size = (self._ozise[0], self._osize[1])
        
    def set_image(self, image):
        self.image = image
        self.size = image.get_size()

    def fit_to_object(self, o, padding=None, abs_fit=False):
        if padding is not None:
            self.padding = padding
            
        w = o.rect.width + self.x_pad
        h = o.rect.height + self.y_pad
        if abs_fit:
            self.size = (w, h)
        else:
            self.size = (
                max({self.rect.width, w}),
                max({self.rect.height, h})
            )
        
        return (self.rect.x + self.left_pad, self.rect.y + self.top_pad)
        
    def join_object(self, o, *args, anchor_point='center', clear=True, **kwargs):
        self.fit_to_object(o, *args, **kwargs)
        if clear:
            self.clear_children()
        o.match_anchor(self.rect, anchor_point)
        offset = o.get_offset_from(self.reverse_padded_rect, anchor_point=anchor_point)
        self.add_child(o, offset=offset, anchor_point=anchor_point)

    def get_rect(self):
        w, h = self.size
        return pg.Rect(0, 0, w, h)
        
    def draw_rect(self, surf):
        pg.draw.rect(surf, self.color, self.rect, **self.border_kwargs)
        if self.outline_width and self.outline_color:
            if self.outline_dir:
                r = self.rect.inflate(self.outline_width * 2, self.outline_width * 2)
            else:
                r = self.rect
            pg.draw.rect(surf, self.outline_color, r, width=self.outline_width, **self.border_kwargs)

    def draw(self, surf):
        if self._draw_rect and self.color:
            self.draw_rect(surf)
        if self._draw_image and self.image:
            surf.blit(self.image, self.rect)

class Compound_Object(Style):
    def collide(self, p):
        return any({o.rect.collidepoint(p) for o in self.get_sub_children()})
        
    def set_cursor(self):
        for o in self.children:
            if o.visible and o.enabled:
                if o.set_cursor():
                    return True
        
    def events(self, events):
        for o in self.children:
            if o.visible and o.enabled:
                o.events(events)
            
    def update(self):
        super().update()
        for o in self.children:
            if o.visible:
                o.update()
            
    def draw(self, surf, reverse=False):
        if self.visible:
            super().draw(surf)
        children = self.children
        if reverse:
            children = children[::-1]
        for o in children:
            if o.visible:
                o.draw(surf)

