// Dummy

#include <stdio.h>

#include "Dummy/Foo.h"
#include "version.h"

int main(int argc, char* argv[]) {
    printf("Example program at %d\n", addOne(4));
    printf("VER %s\n", VERSION_NUMBER);
    printf("VER %s\n", VERSION_HASH);
    printf("VER %s\n", VERSION_DATE);

    for (int i = 0; i < argc; i++) {
        printf("%s\n", argv[i]);
    }
    return 0;
}
