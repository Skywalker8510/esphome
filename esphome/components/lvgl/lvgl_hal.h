//
// Created by Clyde Stubbs on 20/9/2023.
//

#pragma once

#ifdef __cplusplus
#define EXTERNC extern "C"
#else
#define EXTERNC extern
#endif

EXTERNC unsigned long lv_millis(void);
EXTERNC void * lv_custom_mem_alloc(size_t size);
EXTERNC void lv_custom_mem_free(void * ptr);
EXTERNC void * lv_custom_mem_realloc(void * ptr, size_t size);
