#pragma once

#include <ntifs.h>

typedef enum _ipEnumResponseType {
	SIZE = 0,
	IP_ARRAY = 1,

} ipEnumResponseType;


typedef struct _ipEnumResponseHeader {
	ipEnumResponseType type;
	UINT64 dataSize;

} ipEnumResponseHeader, * PipEnumResponseHeader;