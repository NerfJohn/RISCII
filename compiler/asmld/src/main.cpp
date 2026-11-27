// Dummy

#include <stdio.h>

#include "Dummy/Foo.h"
#include "version.h"

int main() {
    printf("Example program at %d\n", addOne(4));
    printf("VER %s\n", VERSION_NUMBER);
    printf("VER %s\n", VERSION_HASH);
    printf("VER %s\n", VERSION_DATE);
    return 0;
}
