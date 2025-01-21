import cv2

from cards.img import get_cam

if __name__ == '__main__':
    cam = get_cam()

    while True:
        result, img = cam.read()
        cv2.imshow("Cam", img)
        if cv2.waitKey(0) & 0xFF == ord('q'):
            break

    cv2.destroyAllWindows()
