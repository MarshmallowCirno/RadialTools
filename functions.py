import blf

def draw_text_line(text_line, newline_x, newline_y, align="LEFT", font=0, font_size=12):
    offset_x = newline_x
    for text, color in text_line:
        draw_text(text, offset_x, newline_y, align, font, font_size, color)
        offset_x += get_text_dimensions(text, font)[0]
    newline_y -= get_text_dimensions("M", font)[1]*2
    return newline_y


def draw_text(text, pos_x, pos_y, align="LEFT", font=0, font_size=12, color=(1, 1, 1, 1)):
    blf.size(font, font_size, 0)
    blf.color(font, *color)
    blf.enable(font, blf.SHADOW)
    blf.shadow_offset(font, 1, -1)
    blf.shadow(font, 3, *(0, 0, 0, 1))

    if align == "RIGHT":
        width, height = blf.dimensions(font, text)
        blf.position(font, pos_x - width, pos_y, 0)
    else:
        blf.position(font, pos_x, pos_y, 0)

    blf.draw(font, text)
    
    
def get_text_dimensions(text, font=0):
    return blf.dimensions(font, text)


def get_safe_draw_x(context, ui_width):
    '''Maximum x position of ui left side that doesn't cause overlap width sidebar'''
    region_overlap = context.preferences.system.use_region_overlap
    if context.space_data.show_region_ui and region_overlap:
        for region in context.area.regions:
            if region.type == 'UI':
                offset_width = region.width # area of 3d view covered by sidebar
                break
    else:
        offset_width = 0
              
    safe_x = context.region.width - offset_width - ui_width
    return safe_x
    