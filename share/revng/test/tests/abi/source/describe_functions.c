/*
 * This file is distributed under the MIT License. See LICENSE.md for details.
 */

/* RUN-default: nope */

#include "common.h"
#include "functions.h"
#include "functions.inc"

#ifdef TARGET_x86_64
#include "x86_64/describe_functions.inc"
#elif TARGET_x86
#include "x86/describe_functions.inc"
#elif TARGET_arm
#include "arm/describe_functions.inc"
#else
#error "Impossible to find sources because the target architecture is unknown."
#endif
