import cv2
import keyboard
import time
def record_webcam():
    
    width, height = 1920, 1080
    
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

    # num_frames = 120
 
    # print("Capturing {0} frames".format(num_frames))
 
    # # Start time
    # start = time.time()
 
    # # Grab a few frames
    # for i in range(0, num_frames) :
    #     ret, frame = cap.read()
 
    # # End time
    # end = time.time()
 
    # # Time elapsed
    # seconds = end - start
    # print ("Time taken : {0} seconds".format(seconds))
 
    # # Calculate frames per second
    # fps  = num_frames / seconds
    # print("Estimated frames per second : {0}".format(fps))

    fps = 60

    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    video_writer = cv2.VideoWriter("./outputs/test.avi", fourcc, fps, (width, height))

    while True:
        if keyboard.is_pressed('e'):
            break
        
        ret, frame = cap.read()
        if ret:
            video_writer.write(frame)
        else:
            break

    cap.release()
    video_writer.release()


def main():
    record_webcam()

if __name__ == "__main__":
    main()