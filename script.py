import mdl
from display import *
from matrix import *
from draw import *
from gmath import *

"""======== first_pass( commands ) ==========

  Checks the commands array for any animation commands
  (frames, basename, vary)

  Should set num_frames and basename if the frames
  or basename commands are present

  If vary is found, but frames is not, the entire
  program should exit.

  If frames is found, but basename is not, set name
  to some default value, and print out a message
  with the name being used.
  ==================== """
def first_pass( commands ):

    name = ''
    num_frames = 1    
    n = False
    vary = False
    frames = False
    
    for command in commands:
        c = command['op']
        args = command['args']
        
        if c == 'vary':
            vary = True
        
        elif c == 'basename':
            n = True
            name = args[0]
        
        elif c == 'frames':
            frames = True
            num_frames = int(args[0])
    
    if vary and not frames:
        print('entire program should exist lol')
        exit()
    
    if frames and not n:
        print('name set to default img')
        name = 'img'

    return (name, int(num_frames))

"""======== second_pass( commands ) ==========

  In order to set the knobs for animation, we need to keep
  a seaprate value for each knob for each frame. We can do
  this by using an array of dictionaries. Each array index
  will correspond to a frame (eg. knobs[0] would be the first
  frame, knobs[2] would be the 3rd frame and so on).

  Each index should contain a dictionary of knob values, each
  key will be a knob name, and each value will be the knob's
  value for that frame.

  Go through the command array, and when you find vary, go
  from knobs[0] to knobs[frames-1] and add (or modify) the
  dictionary corresponding to the given knob with the
  appropirate value.
  ===================="""
def second_pass( commands, num_frames ):
    frames = [ {} for i in range(num_frames) ]
    
    for command in commands:
        c = command['op']
        args = command['args']
        
        if c == 'vary':
            kname = command['knob']
            fr0 = int(args[0])
            frE = args[1]
            s = args[2]
            e = args[3]
            i = (e - s) / (frE - fr0)
            val = s
            while(fr0 <= frE):
                frames[fr0][kname] = val
                val += i
                fr0 += 1
                
    
    return frames


def run(filename):
    """
    This function runs an mdl script
    """
    p = mdl.parseFile(filename)
    if p:
        (commands, symbols) = p
    else:
        print("Parsing failed.")
        return
    view = [0, 0, 1]
    ambient = [50,
               50,
               50]
    #symbols['base'] = ['light', { 'location': [0.5,
    #          0.75,
    #          1],
    #         'color': [255,
    #          255,
    #          255]}]

    color = [0, 0, 0]
    symbols['.white'] = ['constants',
                         {'red': [0.2, 0.5, 0.5],
                          'green': [0.2, 0.5, 0.5],
                          'blue': [0.2, 0.5, 0.5]}]
    reflect = '.white'
    (name, num_frames) = first_pass(commands)
    frames = second_pass(commands, num_frames)
    f = False
    if (num_frames > 1): f = True
    
    for i in range(num_frames):

        tmp = new_matrix()
        ident( tmp )
        cm = new_matrix()
        ident(cm)
        if 'camera' in symbols:
            cm = make_camera(symbols['camera'][1]['position'])
        stack = [ [x[:] for x in tmp] ]
        screen = new_screen()
        zbuffer = new_zbuffer()
        tmp = []
        step_3d = 100
        consts = ''
        coords = []
        coords1 = []
        if f:
            for knob in frames[i]:
                symbols[knob][1] = frames[i][knob]
        print(str(i))
        for command in commands:
            c = command['op']
            args = command['args']
            knob_value = frames[i]
            if c == 'box':
                if command['constants']:
                    reflect = command['constants']
                add_box(tmp,
                        args[0], args[1], args[2],
                        args[3], args[4], args[5])
                matrix_mult( stack[-1], tmp )
                matrix_mult(invert(cm), tmp)
                draw_polygons(tmp, screen, zbuffer, view, ambient, symbols, reflect)
                tmp = []
                reflect = '.white'
            elif c == 'sphere':
                if command['constants']:
                    reflect = command['constants']
                add_sphere(tmp,
                           args[0], args[1], args[2], args[3], step_3d)
                matrix_mult( stack[-1], tmp )
                matrix_mult(invert(cm), tmp)
                draw_polygons(tmp, screen, zbuffer, view, ambient, symbols, reflect)
                tmp = []
                reflect = '.white'
            elif c == 'mesh':
            	if command['constants']:
            	    reflect = command['constants']
            	else:
            	    reflect = '.white'
            	add_mesh(tmp, command['cs'] + '.obj')
            	matrix_mult( stack[-1], tmp)
            	matrix_mult(invert(cm), tmp)
            	draw_polygons(tmp, screen, zbuffer, view, ambient, symbols, reflect)
            	tmp = []
            	reflect = '.white'
            elif c == 'torus':
                if command['constants']:
                    reflect = command['constants']
                add_torus(tmp,
                          args[0], args[1], args[2], args[3], args[4], step_3d)
                matrix_mult( stack[-1], tmp )
                matrix_mult(invert(cm), tmp)
                draw_polygons(tmp, screen, zbuffer, view, ambient, symbols, reflect)
                tmp = []
                reflect = '.white'
            elif c == 'line':
                add_edge(tmp,
                         args[0], args[1], args[2], args[3], args[4], args[5])
                matrix_mult( stack[-1], tmp )
                matrix_mult(invert(cm), tmp)
                draw_lines(tmp, screen, zbuffer, color)
                tmp = []
            elif c == 'move':
                x = args[0]
                y = args[1]
                z = args[2]
                if command['knob']:
                    x = x * symbols[command['knob']][1]
                    y = y * symbols[command['knob']][1]
                    z = z * symbols[command['knob']][1]
                tmp = make_translate(x, y, z)
                matrix_mult(stack[-1], tmp)
                stack[-1] = [x[:] for x in tmp]
                tmp = []
            elif c == 'cmove':
                x = args[0]
                y = args[1]
                z = args[2]
                if command['knob']:
                    x = x * symbols[command['knob']][1]
                    y = y * symbols[command['knob']][1]
                    z = z * symbols[command['knob']][1]
                move_camera(cm, x, y, z)
            elif c == 'scale':
                x = args[0]
                y = args[1]
                z = args[2]
                if command['knob']:
                    x = x * symbols[command['knob']][1]
                    y = y * symbols[command['knob']][1]
                    z = z * symbols[command['knob']][1]                
                tmp = make_scale(x, y, z)
                matrix_mult(stack[-1], tmp)
                stack[-1] = [x[:] for x in tmp]
                tmp = []
            elif c == 'rotate':
                theta = args[1] * (math.pi/180)
                if command['knob']:
                    theta = theta * symbols[command['knob']][1]
                if args[0] == 'x':
                    tmp = make_rotX(theta)
                elif args[0] == 'y':
                    tmp = make_rotY(theta)
                else:
                    tmp = make_rotZ(theta)
                matrix_mult( stack[-1], tmp )
                stack[-1] = [ x[:] for x in tmp]
                tmp = []
            elif c == 'crotate':
                theta = args[1] * (math.pi/180)
                if command['knob']:
                    theta = theta * symbols[command['knob']][1]
                if args[0] == 'x':
                    tmp = make_rotX(theta)
                elif args[0] == 'y':
                    tmp = make_rotY(theta)
                else:
                    tmp = make_rotZ(theta)
                matrix_mult(cm, tmp)
                cm = [ x[:] for x in tmp]
                tmp = []
            elif c == 'push':
                stack.append([x[:] for x in stack[-1]] )
            elif c == 'pop':
                stack.pop()
            elif c == 'display':
                display(screen)
            elif c == 'save':
                save_extension(screen, args[0])
                
            save_extension(screen, 'anim/' + name + format(i, "04") + '.png')
    if (num_frames > 1):
    	make_animation(name)
            # end operation loop
