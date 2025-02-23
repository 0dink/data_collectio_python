import cv2
import pickle
import pygame
import sys

def generate_path_segment(path, direction, distance):
    x_end, y_end = path[-1]    

    if direction == "UP":
        path_segment = [(x_end, y_end - i) for i in range(distance)]
    elif direction == "DOWN":
        path_segment = [(x_end, y_end + i) for i in range(distance)]
    elif direction == "LEFT":
        path_segment = [(x_end - i, y_end) for i in range(distance)]
    elif direction == "RIGHT":
        path_segment = [(x_end + i, y_end) for i in range(distance)]
    else:
        print("invalid direction")
    path.extend(path_segment)
    return path

def generate_path(start, instructions):
    path = [start]
    for direction, distance in instructions:
        path = generate_path_segment(path, direction, distance)
    
    return(path)

def display_dot_and_record(display_resolution, capture_resolution, mode, fps, directory, path_step=5):
    """
    Valid calibration modes are: "snake", "center_box", "face", "no_marker", "quincunx", 
    "7x7_grid", "5x5_grid", "calibration_fancy", "calibration_quincunx" 
    """
    draw_marker = True

    pygame.init()
    
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW) # may need to change backend 

    if not cap.isOpened():
        print("Error: Could not open webcam.")
        exit()

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, capture_resolution[0])
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, capture_resolution[1])

    if cap.get(cv2.CAP_PROP_FRAME_WIDTH) != capture_resolution[0] or cap.get(cv2.CAP_PROP_FRAME_HEIGHT) != capture_resolution[1]:
        cap.release()
        raise RuntimeError(f"Error: Unable to set resolution to {capture_resolution[0]}x{capture_resolution[1]}, current resolution is {cap.get(cv2.CAP_PROP_FRAME_WIDTH)}x{cap.get(cv2.CAP_PROP_FRAME_HEIGHT)}")

    save_as = f"{directory}/calibration_video.avi"
    
    cap.set(cv2.CAP_PROP_AUTOFOCUS, 0)
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter(save_as, fourcc, fps, (capture_resolution[0], capture_resolution[1]))

    if not out.isOpened():
        cap.release()
        raise RuntimeError("Error: Could not open VideoWriter.")

    screen = pygame.display.set_mode((display_resolution[0], display_resolution[1]), pygame.RESIZABLE)
    pygame.display.set_caption('Eye tracking data collection with ground truth')

    dot_color = (255, 0, 0)  # Red color
    dot_radius = 25

    width = display_resolution[0]
    height = display_resolution[1]

    if mode.lower() == "snake":
        path_name = "snake.pickle"
        start = (50, 75)
        instructions = [("DOWN",height-150), ("RIGHT",int(width*.25)-25), ("UP",height-150),
                        ("RIGHT",int(width*.25)-25), ("DOWN",height-150), ("RIGHT",int(width*.25)-25),
                        ("UP",height-150), ("RIGHT",int(width*.25)-25), ("DOWN",height-150)]
        path = generate_path(start, instructions)
    elif mode.lower() == "center_box":
        path_name = "center_box.pickle"
        width_third = width//3
        height_third = height//3
        start = (width_third, height_third)
        instructions = [("RIGHT", width_third), ("DOWN", height_third), ("LEFT", width_third), ("UP",height_third )]
        path = generate_path(start, instructions)
    elif mode.lower() == "face":
        path_step = 1
        path_name = "face.pickle"
        leye = [ (840, 460) for i in range(0,100)]
        reye = [(1045, 460) for i in range(0,100)]
        mouth = [(940, 670) for i in range(0,100)]
        path = []
        path.extend(leye)
        path.extend(reye)
        path.extend(mouth)
    elif mode.lower() == "quincunx":
        path_step = 1
        path_name = "quincunx.pickle"
        top_left = [(75,75) for _ in range(0,75)]
        top_right = [(width-75,75) for _ in range(0,75)]
        bottom_left = [(75, height-75) for _ in range(0,75)]
        bottom_right = [(width-75,height-75)for _ in range(0,75)]
        center = [(width//2, height//2)for _ in range(0,75)]
        path = []
        path.extend(top_left)
        path.extend(top_right)
        path.extend(bottom_left)
        path.extend(bottom_right)
        path.extend(center)
    elif mode.lower() == "5x5_grid":
        path_step = 1
        path_name = "5x5_grid.pickle"
        path = []
        for y_index in range(0,5):
            for x_index in range(0,5):
                dot = [((x_index*width/5) + width/10, (y_index * height/5) + height/10) for _ in range(0,40) ]
                path.extend(dot)
    elif mode.lower() == "7x7_grid":
        path_step = 1
        path_name = "7x7_grid.pickle"
        path = []
        for y_index in range(0,7):
            for x_index in range(0,7):
                dot = [((x_index*round(width/7)) + round(width/14) , (y_index * round(height/7)) + round(height/10)) for _ in range(0,40)]
                path.extend(dot)
    elif mode.lower() == "calibration_fancy":
        path_step = 1
        path_name = "calibration_fancy.pickle"
        path = []
        for x_index in range(0,2): # first 2 columns
            for y_index in range(0,5):
                dot = [((x_index*width/5) + width/10, (y_index * height/5) + height/10) for _ in range(0,40) ]
                path.extend(dot)
        path.extend([((2*width/5) + width/10, (0 * height/5) + height/10) for _ in range(0,40) ]) # center top
        path.extend([((width/2)-(width/10), (height/2)-(height/6)) for _ in range(0,40)])         # up left
        path.extend([((width/2), (height/2)-(height/6)) for _ in range(0,40)])                    # up center
        path.extend([((width/2)+(width/10), (height/2)-(height/6)) for _ in range(0,40)])         # up right 
        path.extend([((width/2)-(width/10), (height/2)) for _ in range(0,40)])                    # center left
        path.extend([((width/2), (height/2)) for _ in range(0,40)])                               # center 
        path.extend([((width/2)+(width/10), (height/2)) for _ in range(0,40)])                    # center right
        path.extend([((width/2)-(width/10), (height/2)+(height/6)) for _ in range(0,40)])         # down left 
        path.extend([((width/2), (height/2)+(height/6)) for _ in range(0,40)])                    # down center 
        path.extend([((width/2)+(width/10), (height/2)+(height/6)) for _ in range(0,40)])         # down right 
        path.extend([((2*width/5) + width/10, (4 * height/5) + height/10) for _ in range(0,40) ]) # center bottom
        for x_index in range(3,5): # last 2 columns
            for y_index in range(0,5):
                dot = [((x_index*width/5) + width/10, (y_index * height/5) + height/10) for _ in range(0,40) ]
                path.extend(dot)
    elif mode.lower() == "calibration_quincunx":
        path_step = 1
        path_name = "calibration_quincunx.pickle"
        path = []
        for x_index in range(0,2): # first 2 columns
            for y_index in range(0,5):
                dot = [((x_index*width/5) + width/10, (y_index * height/5) + height/10) for _ in range(0,40) ]
                path.extend(dot)
        path.extend([((2*width/5) + width/10, (0 * height/5) + height/10) for _ in range(0,40) ]) # center top
        path.extend([((width/2)-(width/10), (height/2)-(height/6)) for _ in range(0,40)])         # up left
        path.extend([((width/2), (height/2)-(height/6)) for _ in range(0,40)])                    # up center
        path.extend([((width/2)+(width/10), (height/2)-(height/6)) for _ in range(0,40)])         # up right 
        
        path.extend([((width/2)-(width/20), (height/2)-(height/12)) for _ in range(0,40)])        # half up left
        path.extend([((width/2)+(width/20), (height/2)-(height/12)) for _ in range(0,40)])        # half up right
        
        path.extend([((width/2)-(width/10), (height/2)) for _ in range(0,40)])                    # center left
        path.extend([((width/2), (height/2)) for _ in range(0,40)])                               # center 
        path.extend([((width/2)+(width/10), (height/2)) for _ in range(0,40)])                    # center right
        
        path.extend([((width/2)-(width/20), (height/2)+(height/12)) for _ in range(0,40)])        # half down left
        path.extend([((width/2)+(width/20), (height/2)+(height/12)) for _ in range(0,40)])        # half down right

        path.extend([((width/2)-(width/10), (height/2)+(height/6)) for _ in range(0,40)])         # down left 
        path.extend([((width/2), (height/2)+(height/6)) for _ in range(0,40)])                    # down center 
        path.extend([((width/2)+(width/10), (height/2)+(height/6)) for _ in range(0,40)])         # down right 
        path.extend([((2*width/5) + width/10, (4 * height/5) + height/10) for _ in range(0,40) ]) # center bottom
        for x_index in range(3,5): # last 2 columns
            for y_index in range(0,5):
                dot = [((x_index*width/5) + width/10, (y_index * height/5) + height/10) for _ in range(0,40) ]
                path.extend(dot)
    elif mode.lower() == "no_marker":
        draw_marker = False
    else:
        print("invalid path selection")
        exit()

    font = pygame.font.SysFont(None, 100)

    countdown = 3
    countdown_start_time = pygame.time.get_ticks()  # Get the current time in milliseconds

    # Countdown loop
    while countdown > 0:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                cap.release()
                out.release()
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                cap.release()
                out.release()
                pygame.quit()
                sys.exit()

        screen.fill((112, 128, 144))

        # Render the countdown number
        countdown_text = font.render(str(countdown), True, (0, 0, 0))  # Black color
        text_rect = countdown_text.get_rect(center=(1920 // 2, 1080 // 2))  # Center the text
        screen.blit(countdown_text, text_rect)
        pygame.display.flip()# Update the display

        # Check if 1 second has passed
        if pygame.time.get_ticks() - countdown_start_time >= 1000:
            countdown -= 1  # Decrease the countdown
            countdown_start_time = pygame.time.get_ticks()  # Reset the timer

    # Main loop
    path_index = 0  # Start at the first point in the path
    save_video = True

    if draw_marker:
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    cap.release()
                    if save_video:
                        out.release()
                    pygame.quit()
                    sys.exit()

                # Allow quitting with ESC key
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    save_video = False
                    cap.release()
                    pygame.quit()
                    sys.exit()

            screen.fill((112, 128, 144))
            dot_position = path[path_index]
            pygame.draw.circle(screen, dot_color, dot_position, dot_radius)
            pygame.display.flip()

            ret, frame = cap.read()
            if not ret:
                print("Error: Failed to capture frame.")
                exit()
            
            if save_video:
                out.write(frame)
            
            # Move to the next position in the path
            path_index += path_step
            if path_index >= len(path):
                if save_video:
                    with open(f"{directory}/{path_name}", 'wb') as f:
                        pickle.dump(path, f)
                    out.release()
                cap.release()
                pygame.quit()
                return 
            
            pygame.time.delay(0) # controls the speed of the movement
    else: # This acts as a debug option to just record a video
        start_time = pygame.time.get_ticks()
        screen.fill((112, 128, 144))
        pygame.display.flip()  
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    cap.release()
                    if save_video:
                        out.release()
                    sys.exit()

                # Allow quitting with ESC key
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    save_video = False
                    cap.release()
                    pygame.quit()
                    sys.exit()
            
            elapsed_time = pygame.time.get_ticks() - start_time

            ret, frame = cap.read()
            if not ret:
                print("Error: Failed to capture frame.")
                exit()
            
            if save_video:
                out.write(frame)            
            
            if elapsed_time >= 2000:
                cap.release()
                out.release()
                pygame.quit()
                return