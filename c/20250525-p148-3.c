#define RAND_MAX 0x7fff
// 设置rand()函数的返回数值范围：[0, RAND_MAX]

#define EXIT_SUCCESS 0
#define EXIT_FAILURE 1
// 程序非0返回均视为运行出错（EXIT_FAILURE），返回0视为运行成功（EXIT_SUCCESS）

#ifndef cplusplus
#define max(a, b) ((a) > (b) ? (a) : (b))
#define min(a, b) ((a) < (b) ? (a) : (b))
#endif
// 当不是C++语言时，定义max和min宏函数

#ifndef _MAC
#define _MAX_PATH 260
#define _MAX_DRIVE 3
#define _MAX_DIR 256
#define _MAX_FNAME 256
#define _MAX_EXT 256
#else
#define _MAX_PATH 256
#define _MAX_DIR 32
#define _MAX_FNAME 64
#endif
// 当执行平台是MACOS时，定义文件路径相关的宏常量