//#define _GNU_SOURCE

#include <cstdio>
#include <cstdlib>
#include <dlfcn.h>
#include <unistd.h>

#include <unordered_map>
#include <utility>
#include <fcntl.h>

#include <sys/types.h>
#include <sys/mman.h>
#include <sys/stat.h>


#define SHM_THRESHOLD (1024 * 1024)
static char SHM_TEMPLATE[] = "SPARTAN_%s_%u_%u_%u";

static std::unordered_map<void*, std::pair<char*, size_t>> malloc_dict;

void* malloc(size_t size)
{
    static void* (*real_malloc)(size_t) = NULL;

    if(real_malloc == NULL) {
        srand (time(NULL));
        real_malloc = (void* (*)(size_t))dlsym(RTLD_NEXT, "malloc");
        if (NULL == real_malloc) {
            fprintf(stderr, "Error in `dlsym`: %s\n", dlerror());
            exit(errno);
        }
    }

    void *ptr = NULL;
    if (size > SHM_THRESHOLD) {
        unsigned int random_id = rand();
        unsigned int id = 0;
        static unsigned int subid = 0;
        id = static_cast<unsigned int>(getpid());
        subid += 1;
        char *name = reinterpret_cast<char *>(malloc(64));
        sprintf(name, SHM_TEMPLATE, "host_ip", random_id, id, subid);
        
        /* Create shared file */
        int fd = shm_open(name, O_CREAT | O_RDWR, (S_IRUSR | S_IWUSR));
        if (-1 == fd) {
            fprintf(stderr, "Error in `shm_open`: %s\n", dlerror());
            exit(errno);
        }
        
        if (-1 == ftruncate(fd, size)) {
            fprintf(stderr, "Error in `ftruncate`: %s\n", dlerror());
            exit(errno);
        }

        /* Map shared memory object */
        ptr = mmap(NULL, size, PROT_READ | PROT_WRITE, MAP_SHARED, fd, 0);
        if (MAP_FAILED == ptr) {
            fprintf(stderr, "Error in `mmap`: %s\n", dlerror());
            exit(errno);
        }
        close(fd);

        /* Record for free API */
        malloc_dict[ptr] = std::make_pair(name, size);
        //printf("malloc %p %u\n", ptr, size);
    } else {
        ptr = real_malloc(size);
    }
    return ptr;
}

//void* realloc(void *ptr, size_t size) 
//{
    //static void* (*real_realloc)(void *ptr, size_t size) = NULL;
    //if (real_realloc == NULL) {
        //real_realloc = (void* (*)(void*, size_t))dlsym(RTLD_NEXT, "realloc");
        //if (NULL == real_realloc) {
            //fprintf(stderr, "Error in `dlsym`: %s\n", dlerror());
            //exit(errno);
        //}
    //}
    //auto it = malloc_dict.find(ptr);
    //if (it != malloc_dict.end()) {
        //printf("realloc\n");
    //}
    //return real_realloc(ptr, size); 
//}

//void* mmap(void* addr, size_t length, int prot, int flags, int fd, off_t offset)
//{
    //static void* (*real_mmap)(void*, size_t, int, int, int, off_t);

    //if (real_mmap == NULL) {
        //real_mmap = (void* (*)(void*, size_t, int, int, int, off_t))dlsym(RTLD_NEXT, "mmap");
        //if (NULL == real_mmap) {
            //fprintf(stderr, "Error in `dlsym`: %s\n", dlerror());
            //exit(errno);
        //}
    //}
    //auto it = malloc_dict.find(addr);
    //if (malloc_dict.size() >= 1) {
        //printf("mmap\n");
    //}
    //return real_mmap(addr, length, prot, flags, fd, offset);
//}

void free(void *ptr)
{
    static void (*real_free)(void *ptr) = NULL;

    if (real_free == NULL) {
        real_free = (void (*)(void*))dlsym(RTLD_NEXT, "free");
        if (NULL == real_free) {
            fprintf(stderr, "Error in `dlsym`: %s\n", dlerror());
            exit(errno);
        }
    }

    auto it = malloc_dict.find(ptr);
    if (it != malloc_dict.end()) {
        //printf("free   %p %u\n", ptr, it->second.second);
        //printf("munmap %d\n", munmap(ptr, it->second.second));
         munmap(ptr, it->second.second);
        shm_unlink(it->second.first);
        malloc_dict.erase(it);
    } else {
        real_free(ptr);
    }
}
