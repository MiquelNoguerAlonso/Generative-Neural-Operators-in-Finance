#define _GNU_SOURCE
#include <dlfcn.h>
#include <unistd.h>
#include <stdio.h>
#include <string.h>
/* This runtime exposes the process's own executable through /proc/self/exe,
   but not /proc/<getpid()>/exe. Adapt only that self-identification request.
   No Lean code, proof checking, or mathematical declarations are changed. */
ssize_t readlink(const char *path, char *buf, size_t size) {
    static ssize_t (*original)(const char *, char *, size_t) = NULL;
    if (!original) original = dlsym(RTLD_NEXT, "readlink");
    char own[64];
    snprintf(own, sizeof(own), "/proc/%d/exe", (int)getpid());
    return original(strcmp(path, own) == 0 ? "/proc/self/exe" : path, buf, size);
}
