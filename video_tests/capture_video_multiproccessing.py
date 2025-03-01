import multiprocessing.process
import keyboard
import cv2

def capture_video(video_queue, stop_event):
    
    width, height = 1920, 1080
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
    print(cap.get(cv2.CAP_PROP_FPS))
    
    while not stop_event.is_set():
        ret, frame = cap.read()
        if ret:
            video_queue.put(frame)  # Put the frame in the queue
        else:
            break

    cap.release()

def save_video(video_queue, stop_event):
    
    width, height = 1920, 1080
    fps = 20

    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    video_writer = cv2.VideoWriter("./outputs/test.avi", fourcc, fps, (width, height))

    while not stop_event.is_set():
        frame = video_queue.get(timeout=0.1)
        video_writer.write(frame)

def main():
    video_queue = multiprocessing.Queue()
    stop_event = multiprocessing.Event()

    capture_video_process = multiprocessing.Process(target=capture_video, args=(video_queue, stop_event,))
    save_video_process = multiprocessing.Process(target=save_video, args=(video_queue, stop_event,))

    capture_video_process.start()
    save_video_process.start()

    while True:
        if keyboard.is_pressed('e'):
            print("Stopping...")
            stop_event.set()
            break

    capture_video_process.join()
    save_video_process.join()


if __name__ == "__main__":
    main()