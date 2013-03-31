#include <stdlib.h>
#include <stdio.h>
#include <sys/ioctl.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <asm/types.h>
#include <fcntl.h>
#include <unistd.h>
#include <linux/hiddev.h>

#define EV_NUM 5

// I found this code here: http://ubuntuforums.org/archive/index.php/t-2044904.html
// It was written by whoever is CrusaderAD on that forum
//
// TO COMPILE: cc -o readscale readscale.c -lusb -lhid
// Requires libusb and libhid

int main (int argc, char **argv) {

    int fd = -1;
    int i;
    struct hiddev_event ev[EV_NUM];
    char name[100];

    if (argc != 2) {
        fprintf(stderr, "usage: %s hiddevice - probably /dev/usb/hiddev0\n", argv[0]);
        exit(1);
    }
    if ((fd = open(argv[1], O_RDONLY)) < 0) {
        perror("hiddev open");
        exit(1);
    }

    ioctl(fd, HIDIOCGNAME(100), name);

    printf("OK name = %s\n", name);

    printf("Reading values .. \n");

    read(fd, ev, sizeof(struct hiddev_event) * EV_NUM);
    for (i = 1; i < 2;i++) {
        printf("%d\n", ev[i].value);

    }

    close(fd);

    exit(0);
}
